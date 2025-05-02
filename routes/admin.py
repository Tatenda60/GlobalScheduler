"""
Administrative routes for bank staff, loan officers, and system administrators.
"""
import json
from datetime import datetime, timedelta
from functools import wraps

from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func, case, desc, asc

from app import db
from models import User, LoanApplication, RiskAssessment

bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """
    Decorator to restrict access to admin users only
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('loan.index'))
        return f(*args, **kwargs)
    return decorated_function

def staff_required(f):
    """
    Decorator to restrict access to staff users (admin, loan officer, staff)
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.has_staff_privileges():
            flash('Access denied. Staff privileges required.', 'danger')
            return redirect(url_for('loan.index'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/dashboard')
@login_required
@staff_required
def dashboard():
    """Administrative dashboard with loan statistics and overview"""
    # Application statistics
    total_applications = LoanApplication.query.count()
    pending_applications = LoanApplication.query.filter_by(status='Pending').count()
    approved_applications = LoanApplication.query.filter_by(status='Approved').count()
    rejected_applications = LoanApplication.query.filter_by(status='Rejected').count()
    under_review_applications = LoanApplication.query.filter_by(status='Under Review').count()
    
    # Recent applications
    recent_applications = LoanApplication.query.order_by(LoanApplication.created_at.desc()).limit(10).all()
    
    # User statistics
    total_users = User.query.count()
    customer_users = User.query.filter_by(role='customer').count()
    staff_count = User.query.filter(User.is_staff).count()
    
    # Staff list for admin
    staff_users = []
    if current_user.is_admin():
        staff_users = User.query.filter(User.is_staff).all()
    
    return render_template(
        'admin/dashboard.html',
        total_applications=total_applications,
        pending_applications=pending_applications,
        approved_applications=approved_applications,
        rejected_applications=rejected_applications,
        under_review_applications=under_review_applications,
        recent_applications=recent_applications,
        total_users=total_users,
        customer_users=customer_users,
        staff_count=staff_count,
        staff_users=staff_users
    )

@bp.route('/applications')
@login_required
@staff_required
def all_applications():
    """View all loan applications in the system"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', 'all')
    sort_by = request.args.get('sort', 'created_at')
    order = request.args.get('order', 'desc')
    
    # Build query
    query = LoanApplication.query
    
    # Apply status filter
    if status_filter != 'all':
        query = query.filter(LoanApplication.status == status_filter)
    
    # Apply sorting
    if sort_by == 'created_at':
        if order == 'desc':
            query = query.order_by(LoanApplication.created_at.desc())
        else:
            query = query.order_by(LoanApplication.created_at.asc())
    elif sort_by == 'loan_amount':
        if order == 'desc':
            query = query.order_by(LoanApplication.loan_amount.desc())
        else:
            query = query.order_by(LoanApplication.loan_amount.asc())
    
    # Paginate results
    applications = query.paginate(page=page, per_page=20)
    
    return render_template(
        'admin/applications.html',
        applications=applications,
        status_filter=status_filter,
        sort_by=sort_by,
        order=order
    )

@bp.route('/applications/<int:application_id>')
@login_required
@staff_required
def application_details(application_id):
    """View detailed information about a specific loan application"""
    application = LoanApplication.query.get_or_404(application_id)
    applicant = User.query.get(application.user_id)
    risk_assessment = RiskAssessment.query.filter_by(loan_application_id=application_id).first()
    
    return render_template(
        'admin/application_details.html',
        application=application,
        applicant=applicant,
        risk_assessment=risk_assessment
    )

@bp.route('/applications/<int:application_id>/decision', methods=['POST'])
@login_required
@staff_required
def make_decision(application_id):
    """Make a decision (approve/reject) on a loan application"""
    application = LoanApplication.query.get_or_404(application_id)
    
    # Check if the application is already decided
    if application.status not in ['Pending', 'Under Review']:
        flash('This application has already been processed.', 'warning')
        return redirect(url_for('admin.application_details', application_id=application_id))
    
    decision = request.form.get('decision')
    notes = request.form.get('notes', '')
    
    if decision not in ['Approved', 'Rejected', 'Under Review']:
        flash('Invalid decision.', 'danger')
        return redirect(url_for('admin.application_details', application_id=application_id))
    
    # Update application status
    application.status = decision
    application.handled_by_id = current_user.id
    application.handled_at = datetime.utcnow()
    application.decision_notes = notes
    
    try:
        db.session.commit()
        flash(f'Application {decision.lower()} successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error processing application: {str(e)}', 'danger')
    
    return redirect(url_for('admin.application_details', application_id=application_id))

@bp.route('/users')
@login_required
@admin_required
def users():
    """View and manage users (admin only)"""
    page = request.args.get('page', 1, type=int)
    users_pagination = User.query.order_by(User.created_at.desc()).paginate(page=page, per_page=20)
    
    return render_template('admin/users.html', users=users_pagination)

@bp.route('/users/<int:user_id>/role', methods=['POST'])
@login_required
@admin_required
def update_user_role(user_id):
    """Update a user's role (admin only)"""
    user = User.query.get_or_404(user_id)
    new_role = request.form.get('role')
    
    if new_role not in ['customer', 'staff', 'officer', 'admin']:
        flash('Invalid role selected.', 'danger')
        return redirect(url_for('admin.users'))
    
    # Update user role
    user.role = new_role
    user.is_staff = new_role in ['staff', 'officer', 'admin']
    
    try:
        db.session.commit()
        flash(f'Role for {user.username} updated to {new_role}.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating role: {str(e)}', 'danger')
    
    return redirect(url_for('admin.users'))

@bp.route('/insights')
@login_required
@staff_required
def insights():
    """View data insights and analytics"""
    # Prepare data for charts
    
    # Credit score distribution
    credit_score_ranges = {
        '300-579 (Poor)': 0,
        '580-669 (Fair)': 0,
        '670-739 (Good)': 0,
        '740-850 (Excellent)': 0
    }
    
    credit_scores = db.session.query(LoanApplication.credit_score).all()
    for score in credit_scores:
        score = score[0]
        if 300 <= score <= 579:
            credit_score_ranges['300-579 (Poor)'] += 1
        elif 580 <= score <= 669:
            credit_score_ranges['580-669 (Fair)'] += 1
        elif 670 <= score <= 739:
            credit_score_ranges['670-739 (Good)'] += 1
        elif 740 <= score <= 850:
            credit_score_ranges['740-850 (Excellent)'] += 1
    
    # Approval rate by month
    # Get data for the past 6 months
    six_months_ago = datetime.utcnow() - timedelta(days=180)
    
    # SQL Alchemy ORM query to get monthly approval rates
    monthly_stats = db.session.query(
        func.strftime('%Y-%m', LoanApplication.created_at).label('month'),
        func.count(LoanApplication.id).label('total'),
        func.sum(case([(LoanApplication.status == 'Approved', 1)], else_=0)).label('approved')
    ).filter(LoanApplication.created_at >= six_months_ago).group_by('month').order_by('month').all()
    
    months = []
    approval_rate_data = []
    
    for stat in monthly_stats:
        months.append(stat.month)
        approval_rate = (stat.approved / stat.total) * 100 if stat.total > 0 else 0
        approval_rate_data.append(approval_rate)
    
    return render_template(
        'admin/insights.html',
        credit_score_ranges=credit_score_ranges,
        months=months,
        approval_rate_data=approval_rate_data
    )

@bp.route('/api/approval-stats')
@login_required
@staff_required
def approval_stats_api():
    """API endpoint for approval statistics"""
    stats = {}
    
    # Count applications by status
    statuses = db.session.query(
        LoanApplication.status, 
        func.count(LoanApplication.id)
    ).group_by(LoanApplication.status).all()
    
    for status, count in statuses:
        stats[status] = count
    
    return jsonify(stats)

@bp.route('/api/risk-by-income')
@login_required
@staff_required
def risk_by_income_api():
    """API endpoint for risk by income data"""
    # Get income brackets and average risk ratings
    income_risk = {}
    
    # Define income brackets
    brackets = [
        (0, 25000, 'Under $25K'),
        (25000, 50000, '$25K-$50K'),
        (50000, 75000, '$50K-$75K'),
        (75000, 100000, '$75K-$100K'),
        (100000, float('inf'), 'Over $100K')
    ]
    
    # Query for applications with risk assessments
    applications = db.session.query(
        LoanApplication.annual_income,
        RiskAssessment.risk_rating
    ).join(
        RiskAssessment, 
        LoanApplication.id == RiskAssessment.loan_application_id
    ).all()
    
    # Sort applications into brackets
    bracket_data = {bracket[2]: [] for bracket in brackets}
    
    for income, risk_rating in applications:
        for min_val, max_val, bracket_name in brackets:
            if min_val <= income < max_val:
                bracket_data[bracket_name].append(risk_rating)
                break
    
    # Calculate average risk rating for each bracket
    for bracket_name, ratings in bracket_data.items():
        if ratings:
            avg_rating = sum(ratings) / len(ratings)
            income_risk[bracket_name] = round(avg_rating, 1)
        else:
            income_risk[bracket_name] = 0
    
    return jsonify(income_risk)