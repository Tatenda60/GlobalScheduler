from flask import (
    Blueprint, render_template, jsonify
)
from flask_login import login_required, current_user
from sqlalchemy import func
from app import db
from models import LoanApplication, RiskAssessment

bp = Blueprint('insights', __name__)

@bp.route('/insights')
@login_required
def insights():
    """Display insights dashboard"""
    # Get basic statistics
    total_applications = LoanApplication.query.filter_by(user_id=current_user.id).count()
    approved_count = LoanApplication.query.filter_by(user_id=current_user.id, status='Approved').count()
    rejected_count = LoanApplication.query.filter_by(user_id=current_user.id, status='Rejected').count()
    review_count = LoanApplication.query.filter_by(user_id=current_user.id, status='Under Review').count()
    
    # Calculate approval rate
    approval_rate = (approved_count / total_applications * 100) if total_applications > 0 else 0
    
    # Get average risk metrics
    avg_metrics = db.session.query(
        func.avg(RiskAssessment.probability_of_default).label('avg_pd'),
        func.avg(RiskAssessment.loss_given_default).label('avg_lgd'),
        func.avg(RiskAssessment.expected_loss).label('avg_el'),
        func.avg(RiskAssessment.risk_rating).label('avg_risk')
    ).join(
        LoanApplication, 
        LoanApplication.id == RiskAssessment.loan_application_id
    ).filter(
        LoanApplication.user_id == current_user.id
    ).first()
    
    # Get recent applications for timeline
    recent_applications = LoanApplication.query.filter_by(
        user_id=current_user.id
    ).order_by(
        LoanApplication.created_at.desc()
    ).limit(5).all()
    
    return render_template(
        'insights.html',
        title='Insights',
        total_applications=total_applications,
        approved_count=approved_count,
        rejected_count=rejected_count,
        review_count=review_count,
        approval_rate=approval_rate,
        avg_metrics=avg_metrics,
        recent_applications=recent_applications
    )


@bp.route('/api/approval_stats')
@login_required
def approval_stats():
    """API endpoint for approval stats (for chart)"""
    statuses = ['Approved', 'Rejected', 'Under Review', 'Pending']
    counts = []
    
    for status in statuses:
        count = LoanApplication.query.filter_by(
            user_id=current_user.id,
            status=status
        ).count()
        counts.append(count)
    
    return jsonify({
        'labels': statuses,
        'data': counts
    })


@bp.route('/api/risk_by_income')
@login_required
def risk_by_income():
    """API endpoint for risk by income (for chart)"""
    # Get applications with risk assessments
    applications = db.session.query(
        LoanApplication, RiskAssessment
    ).join(
        RiskAssessment,
        LoanApplication.id == RiskAssessment.loan_application_id
    ).filter(
        LoanApplication.user_id == current_user.id
    ).all()
    
    # Prepare data for chart
    data = []
    for app, risk in applications:
        data.append({
            'income': app.annual_income,
            'risk_rating': risk.risk_rating
        })
    
    return jsonify(data)


@bp.route('/api/risk_by_credit_score')
@login_required
def risk_by_credit_score():
    """API endpoint for risk by credit score (for chart)"""
    # Define credit score ranges
    ranges = [
        {'min': 300, 'max': 500, 'label': '300-500'},
        {'min': 501, 'max': 600, 'label': '501-600'},
        {'min': 601, 'max': 700, 'label': '601-700'},
        {'min': 701, 'max': 800, 'label': '701-800'},
        {'min': 801, 'max': 850, 'label': '801-850'}
    ]
    
    # Calculate average risk rating for each range
    range_data = []
    
    for r in ranges:
        # Get applications in this credit score range
        apps = db.session.query(
            LoanApplication, RiskAssessment
        ).join(
            RiskAssessment,
            LoanApplication.id == RiskAssessment.loan_application_id
        ).filter(
            LoanApplication.user_id == current_user.id,
            LoanApplication.credit_score >= r['min'],
            LoanApplication.credit_score <= r['max']
        ).all()
        
        # Calculate average risk rating
        total_rating = sum(risk.risk_rating for _, risk in apps)
        avg_rating = total_rating / len(apps) if len(apps) > 0 else 0
        
        range_data.append({
            'range': r['label'],
            'avg_risk': avg_rating,
            'count': len(apps)
        })
    
    return jsonify({
        'labels': [r['label'] for r in ranges],
        'data': [d['avg_risk'] for d in range_data],
        'counts': [d['count'] for d in range_data]
    })
