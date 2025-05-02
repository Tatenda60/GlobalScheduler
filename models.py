from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    """User model for authentication and profile management"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    phone = db.Column(db.String(20))
    # Role-based access control
    role = db.Column(db.String(20), default='customer')  # 'customer', 'staff', 'officer', 'admin'
    is_staff = db.Column(db.Boolean, default=False)  # Quick check for any staff role
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with loan applications
    loan_applications = db.relationship('LoanApplication', 
                                     foreign_keys='LoanApplication.user_id',
                                     backref='applicant', 
                                     lazy='dynamic')
    
    def set_password(self, password):
        """Set the user's password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the password matches the hash"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'
        
    def is_admin(self):
        """Check if the user is an administrator"""
        return self.role == 'admin'
        
    def is_loan_officer(self):
        """Check if the user is a loan officer"""
        return self.role == 'officer'
        
    def is_bank_staff(self):
        """Check if the user is bank staff"""
        return self.role == 'staff'
        
    def has_staff_privileges(self):
        """Check if the user has any staff privileges"""
        return self.is_staff or self.role in ['staff', 'officer', 'admin']
        
    def get_display_name(self):
        """Get the user's display name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username


class LoanApplication(db.Model):
    """Loan application model to store user loan requests"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Loan details
    loan_amount = db.Column(db.Float, nullable=False)
    loan_purpose = db.Column(db.String(100), nullable=False)
    loan_term = db.Column(db.Integer, nullable=False)  # In months
    
    # Applicant financial information
    age = db.Column(db.Integer, nullable=False)
    annual_income = db.Column(db.Float, nullable=False)
    monthly_expenses = db.Column(db.Float, nullable=False)
    credit_score = db.Column(db.Integer, nullable=False)
    existing_debt = db.Column(db.Float, nullable=False)
    employment_status = db.Column(db.String(50), nullable=False)
    employment_length = db.Column(db.Float)  # In years
    home_ownership = db.Column(db.String(50))
    
    # Application status
    status = db.Column(db.String(50), default='Pending')  # Pending, Approved, Rejected, Under Review
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Tracking who handled the loan
    handled_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    handled_by = db.relationship('User', foreign_keys=[handled_by_id], backref='handled_loans', lazy='joined')
    handled_at = db.Column(db.DateTime, nullable=True)
    decision_notes = db.Column(db.Text, nullable=True)
    
    # Relationship with risk assessment
    risk_assessment = db.relationship('RiskAssessment', backref='loan_application', uselist=False, lazy='joined')
    
    def __repr__(self):
        return f'<LoanApplication {self.id} - ${self.loan_amount} - {self.status}>'


class RiskAssessment(db.Model):
    """Risk assessment model to store credit risk calculations"""
    id = db.Column(db.Integer, primary_key=True)
    loan_application_id = db.Column(db.Integer, db.ForeignKey('loan_application.id'), nullable=False)
    
    # Risk metrics
    probability_of_default = db.Column(db.Float, nullable=False)  # PD
    loss_given_default = db.Column(db.Float, nullable=False)  # LGD
    exposure_at_default = db.Column(db.Float, nullable=False)  # EAD
    expected_loss = db.Column(db.Float, nullable=False)  # EL = PD * LGD * EAD
    
    # Risk rating (1-10, with 10 being highest risk)
    risk_rating = db.Column(db.Integer, nullable=False)
    
    # Decision and reasons
    recommendation = db.Column(db.String(50), nullable=False)  # Approve, Reject, Review
    reasons = db.Column(db.Text)  # Reasons for the recommendation
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<RiskAssessment {self.id} - {self.recommendation} - Risk Rating: {self.risk_rating}>'
