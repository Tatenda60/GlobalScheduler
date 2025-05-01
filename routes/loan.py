import os
import csv
import tempfile
from datetime import datetime
from flask import (
    Blueprint, render_template, redirect, url_for, 
    flash, request, current_app, jsonify
)
from flask_login import login_required, current_user
from app import db
from models import LoanApplication, RiskAssessment
from forms import LoanApplicationForm, CSVUploadForm
from risk_engine import CreditRiskEngine

bp = Blueprint('loan', __name__)

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    """Display the dashboard/homepage"""
    # Get the user's loan applications
    applications = LoanApplication.query.filter_by(user_id=current_user.id).order_by(LoanApplication.created_at.desc()).limit(5).all()
    
    # Calculate some statistics for the dashboard
    total_applications = LoanApplication.query.filter_by(user_id=current_user.id).count()
    approved_applications = LoanApplication.query.filter_by(user_id=current_user.id, status='Approved').count()
    
    return render_template(
        'index.html', 
        title='Dashboard',
        applications=applications,
        total_applications=total_applications,
        approved_applications=approved_applications
    )


@bp.route('/apply', methods=['GET', 'POST'])
@login_required
def apply():
    """Handle loan application submission"""
    form = LoanApplicationForm()
    
    if form.validate_on_submit():
        # Create a new loan application
        application = LoanApplication(
            user_id=current_user.id,
            loan_amount=form.loan_amount.data,
            loan_purpose=form.loan_purpose.data,
            loan_term=form.loan_term.data,
            age=form.age.data,
            annual_income=form.annual_income.data,
            monthly_expenses=form.monthly_expenses.data,
            credit_score=form.credit_score.data,
            existing_debt=form.existing_debt.data,
            employment_status=form.employment_status.data,
            employment_length=form.employment_length.data,
            home_ownership=form.home_ownership.data,
            status='Pending'
        )
        
        # Add application to database
        db.session.add(application)
        db.session.commit()
        
        # Process the application and calculate risk
        application_data = {
            'loan_amount': application.loan_amount,
            'loan_term': application.loan_term,
            'credit_score': application.credit_score,
            'annual_income': application.annual_income,
            'monthly_expenses': application.monthly_expenses,
            'existing_debt': application.existing_debt,
            'employment_status': application.employment_status
        }
        
        assessment = CreditRiskEngine.assess_loan_application(application_data)
        
        # Create risk assessment record
        risk_assessment = RiskAssessment(
            loan_application_id=application.id,
            probability_of_default=assessment['probability_of_default'],
            loss_given_default=assessment['loss_given_default'],
            exposure_at_default=assessment['exposure_at_default'],
            expected_loss=assessment['expected_loss'],
            risk_rating=assessment['risk_rating'],
            recommendation=assessment['recommendation'],
            reasons=', '.join(assessment['reasons'])
        )
        
        # Update application status based on recommendation
        if assessment['recommendation'] == 'Approve':
            application.status = 'Approved'
        elif assessment['recommendation'] == 'Reject':
            application.status = 'Rejected'
        else:
            application.status = 'Under Review'
        
        # Add risk assessment to database
        db.session.add(risk_assessment)
        db.session.commit()
        
        flash('Your loan application has been submitted successfully!', 'success')
        return redirect(url_for('loan.predict', application_id=application.id))
    
    return render_template('apply.html', title='Apply for Loan', form=form)


@bp.route('/predict/<int:application_id>')
@login_required
def predict(application_id):
    """Display prediction results for a loan application"""
    application = LoanApplication.query.get_or_404(application_id)
    
    # Ensure the application belongs to the current user
    if application.user_id != current_user.id:
        flash('You do not have permission to view this application.', 'danger')
        return redirect(url_for('loan.index'))
    
    # Get the risk assessment for the application
    risk_assessment = RiskAssessment.query.filter_by(loan_application_id=application_id).first()
    
    if not risk_assessment:
        flash('No risk assessment found for this application.', 'danger')
        return redirect(url_for('loan.index'))
    
    return render_template(
        'predict.html',
        title='Loan Prediction Result',
        application=application,
        assessment=risk_assessment
    )


@bp.route('/history')
@login_required
def history():
    """Display loan application history"""
    applications = LoanApplication.query.filter_by(user_id=current_user.id).order_by(LoanApplication.created_at.desc()).all()
    
    return render_template(
        'history.html',
        title='Loan Application History',
        applications=applications
    )


@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """Handle CSV upload for batch loan processing"""
    form = CSVUploadForm()
    
    if form.validate_on_submit():
        # Save the uploaded file to a temporary file
        uploaded_file = form.csv_file.data
        fd, temp_path = tempfile.mkstemp()
        try:
            with os.fdopen(fd, 'wb') as tmp:
                uploaded_file.save(tmp)
            
            # Process the CSV file
            try:
                assessments = CreditRiskEngine.process_csv_data(temp_path)
                
                # Create loan applications and risk assessments for each row
                for assessment in assessments:
                    app_data = assessment['application_data']
                    
                    application = LoanApplication(
                        user_id=current_user.id,
                        loan_amount=app_data['loan_amount'],
                        loan_term=app_data['loan_term'],
                        age=30,  # Default value, not in CSV
                        annual_income=app_data['annual_income'],
                        monthly_expenses=app_data['monthly_expenses'],
                        credit_score=app_data['credit_score'],
                        existing_debt=app_data['existing_debt'],
                        employment_status=app_data['employment_status'],
                        employment_length=0,  # Default value, not in CSV
                        home_ownership='rent',  # Default value, not in CSV
                        status='Pending'
                    )
                    
                    # Update application status based on recommendation
                    if assessment['recommendation'] == 'Approve':
                        application.status = 'Approved'
                    elif assessment['recommendation'] == 'Reject':
                        application.status = 'Rejected'
                    else:
                        application.status = 'Under Review'
                    
                    # Add application to database
                    db.session.add(application)
                    db.session.commit()
                    
                    risk_assessment = RiskAssessment(
                        loan_application_id=application.id,
                        probability_of_default=assessment['probability_of_default'],
                        loss_given_default=assessment['loss_given_default'],
                        exposure_at_default=assessment['exposure_at_default'],
                        expected_loss=assessment['expected_loss'],
                        risk_rating=assessment['risk_rating'],
                        recommendation=assessment['recommendation'],
                        reasons=', '.join(assessment['reasons'])
                    )
                    
                    # Add risk assessment to database
                    db.session.add(risk_assessment)
                    db.session.commit()
                
                flash(f'Successfully processed {len(assessments)} applications from the CSV file.', 'success')
                return redirect(url_for('loan.history'))
                
            except Exception as e:
                flash(f'Error processing CSV file: {str(e)}', 'danger')
        
        finally:
            # Remove the temporary file
            os.unlink(temp_path)
    
    return render_template('upload.html', title='Upload CSV Data', form=form)
