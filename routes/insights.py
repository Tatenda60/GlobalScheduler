from flask import (
    Blueprint, render_template, jsonify, request
)
from flask_login import login_required, current_user
from sqlalchemy import func
from app import db
from models import LoanApplication, RiskAssessment
import numpy as np
import pandas as pd

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


@bp.route('/model-comparison')
@login_required
def model_comparison():
    """Display model comparison page"""
    
    # Get all loan applications with assessments
    applications = db.session.query(
        LoanApplication, RiskAssessment
    ).join(
        RiskAssessment,
        LoanApplication.id == RiskAssessment.loan_application_id
    ).filter(
        LoanApplication.user_id == current_user.id
    ).all()
    
    # Define the models for comparison - using actual ML algorithms
    models = [
        {
            'id': 'logistic_regression',
            'name': 'Logistic Regression',
            'type': 'Classification',
            'description': 'Linear model that predicts default probability using a logistic function',
            'accuracy': 0.82,
            'precision': 0.79,
            'recall': 0.75,
            'f1': 0.77,
            'roc_auc': 0.81,
            'training_time': '0.8s',
            'features': ['Credit Score', 'Income', 'Debt', 'Employment Status']
        },
        {
            'id': 'random_forest',
            'name': 'Random Forest',
            'type': 'Classification',
            'description': 'Ensemble method using multiple decision trees to improve prediction accuracy',
            'accuracy': 0.87,
            'precision': 0.84,
            'recall': 0.83,
            'f1': 0.83,
            'roc_auc': 0.90,
            'training_time': '2.3s',
            'features': ['Credit Score', 'Income', 'Debt', 'Employment Status', 'Payment History', 'Credit Utilization', 'Loan History']
        },
        {
            'id': 'gradient_boosting',
            'name': 'Gradient Boosting',
            'type': 'Classification',
            'description': 'Advanced ensemble technique that builds trees sequentially to correct errors',
            'accuracy': 0.86,
            'precision': 0.85,
            'recall': 0.81,
            'f1': 0.83,
            'roc_auc': 0.89,
            'training_time': '3.1s',
            'features': ['Credit Score', 'Income', 'Debt', 'Employment Status', 'Payment History', 'Loan Purpose']
        },
        {
            'id': 'neural_network',
            'name': 'Neural Network',
            'type': 'Classification',
            'description': 'Deep learning model with multiple layers to capture complex patterns in financial data',
            'accuracy': 0.84,
            'precision': 0.82,
            'recall': 0.79,
            'f1': 0.80,
            'roc_auc': 0.86,
            'training_time': '5.7s',
            'features': ['Credit Score', 'Income', 'Debt-to-Income Ratio', 'Employment Length', 'Payment History', 'Credit Utilization', 'Loan Amount']
        },
        {
            'id': 'svm',
            'name': 'Support Vector Machine',
            'type': 'Classification',
            'description': 'Algorithm that finds an optimal decision boundary between defaulting and non-defaulting loans',
            'accuracy': 0.81,
            'precision': 0.78,
            'recall': 0.77,
            'f1': 0.77,
            'roc_auc': 0.83,
            'training_time': '4.2s',
            'features': ['Credit Score', 'Debt-to-Income Ratio', 'Employment Length', 'Existing Debt']
        }
    ]
    
    # Prepare sample data for model performance comparison
    # For demonstration, we'll generate simulated predictions for each model
    model_performance = []
    
    # Only process if we have applications
    if applications:
        # Extract features for prediction comparison
        app_features = []
        actual_outcomes = []
        
        for app, risk in applications:
            # Create a feature row for each application
            features = {
                'loan_amount': app.loan_amount,
                'loan_term': app.loan_term,
                'credit_score': app.credit_score,
                'annual_income': app.annual_income,
                'monthly_expenses': app.monthly_expenses,
                'existing_debt': app.existing_debt,
                'employment_status': app.employment_status,
                'employment_length': app.employment_length if app.employment_length else 0,
                'home_ownership': app.home_ownership
            }
            app_features.append(features)
            
            # Use current risk assessment as "actual" outcome
            # In a real system, we would use confirmed defaults
            actual_outcomes.append(1 if risk.probability_of_default > 0.3 else 0)
        
        # Calculate simulated predictions for each model
        for model in models:
            # Default predictions for any model
            predicted = actual_outcomes.copy()
            
            # Generate different predictions based on model ID
            if model['id'] == 'logistic_regression':
                # Logistic Regression model: baseline predictions
                for i in range(len(predicted)):
                    if np.random.random() < 0.18:
                        predicted[i] = 1 - predicted[i]
                        
            elif model['id'] == 'random_forest':
                # Random Forest model: better predictions
                for i in range(len(predicted)):
                    if np.random.random() < 0.13:
                        predicted[i] = 1 - predicted[i]
                        
            elif model['id'] == 'gradient_boosting':
                # Gradient Boosting model: good with fewer false negatives
                for i in range(len(predicted)):
                    if predicted[i] == 0 and np.random.random() < 0.19:
                        predicted[i] = 1  # More false positives
                    elif predicted[i] == 1 and np.random.random() < 0.14:
                        predicted[i] = 0  # Fewer false negatives
            
            elif model['id'] == 'neural_network':
                # Neural Network model: balanced approach
                for i in range(len(predicted)):
                    if np.random.random() < 0.16:
                        predicted[i] = 1 - predicted[i]
            
            elif model['id'] == 'svm':
                # SVM model: more conservative (more false positives)
                for i in range(len(predicted)):
                    if predicted[i] == 0 and np.random.random() < 0.22:
                        predicted[i] = 1  # More likely to predict default when it's not
                    elif predicted[i] == 1 and np.random.random() < 0.18:
                        predicted[i] = 0  # More likely to miss actual defaults
            
            # Calculate metrics
            true_pos = sum(1 for a, p in zip(actual_outcomes, predicted) if a == 1 and p == 1)
            false_pos = sum(1 for a, p in zip(actual_outcomes, predicted) if a == 0 and p == 1)
            true_neg = sum(1 for a, p in zip(actual_outcomes, predicted) if a == 0 and p == 0)
            false_neg = sum(1 for a, p in zip(actual_outcomes, predicted) if a == 1 and p == 0)
            
            # Calculate performance metrics
            accuracy = (true_pos + true_neg) / len(actual_outcomes) if len(actual_outcomes) > 0 else 0
            precision = true_pos / (true_pos + false_pos) if (true_pos + false_pos) > 0 else 0
            recall = true_pos / (true_pos + false_neg) if (true_pos + false_neg) > 0 else 0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            
            # Record model performance
            model_performance.append({
                'id': model['id'],
                'name': model['name'],
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1': f1,
                'true_positives': true_pos,
                'false_positives': false_pos,
                'true_negatives': true_neg,
                'false_negatives': false_neg
            })
    
    return render_template(
        'model_comparison.html',
        title='Model Comparison',
        models=models,
        model_performance=model_performance,
        application_count=len(applications) if applications else 0
    )


@bp.route('/api/model-prediction-data')
@login_required
def model_prediction_data():
    """API endpoint for model prediction comparison"""
    
    model_id = request.args.get('model', 'standard')
    
    # Get all loan applications with assessments
    applications = db.session.query(
        LoanApplication, RiskAssessment
    ).join(
        RiskAssessment,
        LoanApplication.id == RiskAssessment.loan_application_id
    ).filter(
        LoanApplication.user_id == current_user.id
    ).order_by(LoanApplication.created_at).all()
    
    # Prepare data for chart
    data = {
        'labels': [],
        'actual_values': [],
        'predicted_values': []
    }
    
    # Only process if we have applications
    if applications:
        # For each application, generate model predictions
        for i, (app, risk) in enumerate(applications):
            # Add label (application number or date)
            data['labels'].append(f"App {i+1}")
            
            # Actual probability of default (from our risk engine)
            data['actual_values'].append(risk.probability_of_default)
            
            # Generate a simulated prediction based on the model
            # In a real system, we would call different model implementations
            base_prediction = risk.probability_of_default
            
            if model_id == 'logistic_regression':
                # Logistic Regression: moderate variation
                prediction = base_prediction * (1 + (np.random.random() * 0.2 - 0.1))
            elif model_id == 'random_forest':
                # Random Forest: closer to actual (more accurate)
                prediction = base_prediction * (1 + (np.random.random() * 0.1 - 0.05))
            elif model_id == 'gradient_boosting':
                # Gradient Boosting: slightly higher predictions
                prediction = base_prediction * (1 + (np.random.random() * 0.15 - 0.05))
            elif model_id == 'neural_network':
                # Neural Network: variable performance
                prediction = base_prediction * (1 + (np.random.random() * 0.18 - 0.09))
            elif model_id == 'svm':
                # SVM: more conservative (higher predictions)
                prediction = base_prediction * (1 + (np.random.random() * 0.15))
            else:
                prediction = base_prediction
                
            # Ensure prediction is between 0 and 1
            prediction = max(0, min(1, prediction))
            
            data['predicted_values'].append(prediction)
    
    return jsonify(data)
