"""
Administrative routes for bank staff, loan officers, and system administrators.
"""
from datetime import datetime
from flask import (
    Blueprint, render_template, redirect, url_for, 
    flash, request, current_app, jsonify
)
from flask_login import login_required, current_user
from app import db
from models import User, LoanApplication, RiskAssessment
from functools import wraps

bp = Blueprint('admin', __name__, url_prefix='/admin')

# Custom decorator for admin access
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.has_staff_privileges():
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('loan.index'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/')
@login_required
@admin_required
def dashboard():
    """Administrative dashboard with loan statistics and overview"""
    # Get loan application statistics
    total_applications = LoanApplication.query.count()
    pending_applications = LoanApplication.query.filter_by(status='Pending').count()
    approved_applications = LoanApplication.query.filter_by(status='Approved').count()
    rejected_applications = LoanApplication.query.filter_by(status='Rejected').count()
    under_review_applications = LoanApplication.query.filter_by(status='Under Review').count()
    
    # Get the most recent loan applications
    recent_applications = LoanApplication.query.order_by(LoanApplication.created_at.desc()).limit(10).all()
    
    # Get statistics about loan officers/staff activity
    staff_users = User.query.filter(User.is_staff == True).all()
    
    # Admin-specific data
    if current_user.is_admin():
        # Get user statistics
        total_users = User.query.count()
        customer_users = User.query.filter_by(role='customer').count()
        staff_count = User.query.filter(User.is_staff == True).count()
    else:
        total_users = None
        customer_users = None
        staff_count = None
    
    return render_template(
        'admin/dashboard.html',
        title='Admin Dashboard',
        total_applications=total_applications,
        pending_applications=pending_applications,
        approved_applications=approved_applications,
        rejected_applications=rejected_applications,
        under_review_applications=under_review_applications,
        recent_applications=recent_applications,
        staff_users=staff_users,
        total_users=total_users,
        customer_users=customer_users,
        staff_count=staff_count
    )

@bp.route('/applications')
@login_required
@admin_required
def all_applications():
    """View all loan applications in the system"""
    # Get filter parameters
    status_filter = request.args.get('status', 'all')
    sort_by = request.args.get('sort', 'created_at')
    order = request.args.get('order', 'desc')
    
    # Base query
    query = LoanApplication.query
    
    # Apply status filter if provided
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    # Apply sorting
    if sort_by == 'created_at':
        if order == 'desc':
            query = query.order_by(LoanApplication.created_at.desc())
        else:
            query = query.order_by(LoanApplication.created_at)
    elif sort_by == 'loan_amount':
        if order == 'desc':
            query = query.order_by(LoanApplication.loan_amount.desc())
        else:
            query = query.order_by(LoanApplication.loan_amount)
    
    # Get all applications with pagination
    page = request.args.get('page', 1, type=int)
    applications = query.paginate(page=page, per_page=20)
    
    return render_template(
        'admin/applications.html',
        title='All Loan Applications',
        applications=applications,
        status_filter=status_filter,
        sort_by=sort_by,
        order=order
    )

@bp.route('/application/<int:application_id>')
@login_required
@admin_required
def application_details(application_id):
    """View detailed information about a specific loan application"""
    application = LoanApplication.query.get_or_404(application_id)
    
    # Get the applicant details
    applicant = User.query.get(application.user_id)
    
    # Get risk assessment
    risk_assessment = application.risk_assessment
    
    # Get who handled the loan, if applicable
    handler = None
    if application.handled_by_id:
        handler = User.query.get(application.handled_by_id)
    
    return render_template(
        'admin/application_details.html',
        title='Loan Application Details',
        application=application,
        applicant=applicant,
        risk_assessment=risk_assessment,
        handler=handler
    )

@bp.route('/application/<int:application_id>/decision', methods=['POST'])
@login_required
@admin_required
def make_decision(application_id):
    """Make a decision (approve/reject) on a loan application"""
    application = LoanApplication.query.get_or_404(application_id)
    
    # Get form data
    decision = request.form.get('decision')
    notes = request.form.get('notes', '')
    
    if decision not in ['Approved', 'Rejected', 'Under Review']:
        flash('Invalid decision.', 'danger')
        return redirect(url_for('admin.application_details', application_id=application_id))
    
    # Update application
    application.status = decision
    application.handled_by_id = current_user.id
    application.handled_at = datetime.utcnow()
    application.decision_notes = notes
    db.session.commit()
    
    flash(f'Loan application has been {decision.lower()}.', 'success')
    return redirect(url_for('admin.application_details', application_id=application_id))

@bp.route('/users')
@login_required
@admin_required
def users():
    """View and manage users (admin only)"""
    if not current_user.is_admin():
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('admin.dashboard'))
    
    # Get all users with pagination
    page = request.args.get('page', 1, type=int)
    all_users = User.query.paginate(page=page, per_page=20)
    
    return render_template(
        'admin/users.html',
        title='User Management',
        users=all_users
    )

@bp.route('/user/<int:user_id>/role', methods=['POST'])
@login_required
@admin_required
def update_user_role(user_id):
    """Update a user's role (admin only)"""
    if not current_user.is_admin():
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('admin.dashboard'))
    
    user = User.query.get_or_404(user_id)
    new_role = request.form.get('role')
    
    # Validate role
    if new_role not in ['customer', 'staff', 'officer', 'admin']:
        flash('Invalid role.', 'danger')
        return redirect(url_for('admin.users'))
    
    # Update user role
    user.role = new_role
    user.is_staff = (new_role in ['staff', 'officer', 'admin'])
    db.session.commit()
    
    flash(f'User role updated to {new_role}.', 'success')
    return redirect(url_for('admin.users'))

@bp.route('/insights')
@login_required
@admin_required
def insights():
    """View data insights and analytics"""
    # Calculate approval rate over time
    # This would normally be more sophisticated with proper time series analysis
    applications_by_month = {}
    approvals_by_month = {}
    
    applications = LoanApplication.query.all()
    for app in applications:
        month_key = app.created_at.strftime('%Y-%m')
        applications_by_month[month_key] = applications_by_month.get(month_key, 0) + 1
        
        if app.status == 'Approved':
            approvals_by_month[month_key] = approvals_by_month.get(month_key, 0) + 1
    
    # Calculate approval rate
    approval_rates = {}
    for month in applications_by_month:
        approval_rates[month] = (approvals_by_month.get(month, 0) / applications_by_month[month]) * 100
    
    # Sort by month
    months = sorted(approval_rates.keys())
    approval_rate_data = [approval_rates.get(month, 0) for month in months]
    
    # Get credit score distribution
    credit_score_ranges = {
        '300-550': 0,
        '551-650': 0,
        '651-750': 0,
        '751-850': 0
    }
    
    for app in applications:
        if app.credit_score <= 550:
            credit_score_ranges['300-550'] += 1
        elif app.credit_score <= 650:
            credit_score_ranges['551-650'] += 1
        elif app.credit_score <= 750:
            credit_score_ranges['651-750'] += 1
        else:
            credit_score_ranges['751-850'] += 1
    
    return render_template(
        'admin/insights.html',
        title='Loan Insights & Analytics',
        months=months,
        approval_rate_data=approval_rate_data,
        credit_score_ranges=credit_score_ranges
    )

@bp.route('/api/approval-stats')
@login_required
@admin_required
def approval_stats_api():
    """API endpoint for approval statistics"""
    status_counts = {
        'Pending': LoanApplication.query.filter_by(status='Pending').count(),
        'Approved': LoanApplication.query.filter_by(status='Approved').count(),
        'Rejected': LoanApplication.query.filter_by(status='Rejected').count(),
        'Under Review': LoanApplication.query.filter_by(status='Under Review').count()
    }
    
    return jsonify(status_counts)

@bp.route('/api/risk-by-income')
@login_required
@admin_required
def risk_by_income_api():
    """API endpoint for risk by income data"""
    # Group applications by income range and calculate average risk rating
    income_ranges = {
        '0-50k': {'count': 0, 'risk_sum': 0},
        '50k-75k': {'count': 0, 'risk_sum': 0},
        '75k-100k': {'count': 0, 'risk_sum': 0},
        '100k+': {'count': 0, 'risk_sum': 0}
    }
    
    applications = LoanApplication.query.all()
    for app in applications:
        if app.risk_assessment:
            if app.annual_income < 50000:
                income_ranges['0-50k']['count'] += 1
                income_ranges['0-50k']['risk_sum'] += app.risk_assessment.risk_rating
            elif app.annual_income < 75000:
                income_ranges['50k-75k']['count'] += 1
                income_ranges['50k-75k']['risk_sum'] += app.risk_assessment.risk_rating
            elif app.annual_income < 100000:
                income_ranges['75k-100k']['count'] += 1
                income_ranges['75k-100k']['risk_sum'] += app.risk_assessment.risk_rating
            else:
                income_ranges['100k+']['count'] += 1
                income_ranges['100k+']['risk_sum'] += app.risk_assessment.risk_rating
    
    # Calculate averages
    avg_risk_by_income = {}
    for range_name, data in income_ranges.items():
        if data['count'] > 0:
            avg_risk_by_income[range_name] = data['risk_sum'] / data['count']
        else:
            avg_risk_by_income[range_name] = 0
    
    return jsonify(avg_risk_by_income)