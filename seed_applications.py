"""
Script to seed the database with sample loan applications

This script generates realistic loan applications with diverse risk levels,
ensuring a balanced mix of approved, rejected and pending applications.
"""
import random
import csv
import os
from datetime import datetime, timedelta
from app import app, db
from models import User, LoanApplication, RiskAssessment
from risk_engine import CreditRiskEngine
from werkzeug.security import generate_password_hash

# Configuration options
NUM_SAMPLE_USERS = 10  # Number of sample users to create
NUM_ADMIN_OFFICERS = 3  # Number of admin/officer accounts to create
MIN_APPLICATIONS_PER_USER = 2  # Minimum applications per user
MAX_APPLICATIONS_PER_USER = 5  # Maximum applications per user
SEED_DEMO_USER = True  # Create a demo user account

# Employment status options for random selection
EMPLOYMENT_STATUSES = ['full_time', 'part_time', 'self_employed', 'retired', 'unemployed']

# Home ownership options for random selection
HOME_OWNERSHIP_TYPES = ['own', 'mortgage', 'rent', 'other']

# Loan purpose options for random selection
LOAN_PURPOSES = ['business', 'equipment', 'inventory', 'refinance', 'working_capital', 'other']

# Admin/staff usernames to create
STAFF_USERS = [
    {'username': 'admin', 'email': 'admin@example.com', 'role': 'admin', 'password': 'Admin@123'},
    {'username': 'officer1', 'email': 'officer1@example.com', 'role': 'officer', 'password': 'Officer@123'},
    {'username': 'officer2', 'email': 'officer2@example.com', 'role': 'officer', 'password': 'Officer@123'},
    {'username': 'staff1', 'email': 'staff1@example.com', 'role': 'staff', 'password': 'Staff@123'},
]

# Names for sample users
FIRST_NAMES = [
    'James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer', 'Michael', 'Linda', 
    'William', 'Elizabeth', 'David', 'Barbara', 'Richard', 'Susan', 'Joseph', 'Jessica', 
    'Thomas', 'Sarah', 'Charles', 'Karen', 'Christopher', 'Nancy', 'Daniel', 'Lisa', 
    'Matthew', 'Margaret', 'Anthony', 'Betty', 'Mark', 'Sandra', 'Donald', 'Ashley', 
    'Steven', 'Emily', 'Paul', 'Donna', 'Andrew', 'Michelle', 'Joshua', 'Dorothy'
]

LAST_NAMES = [
    'Smith', 'Johnson', 'Williams', 'Jones', 'Brown', 'Davis', 'Miller', 'Wilson', 
    'Moore', 'Taylor', 'Anderson', 'Thomas', 'Jackson', 'White', 'Harris', 'Martin', 
    'Thompson', 'Garcia', 'Martinez', 'Robinson', 'Clark', 'Rodriguez', 'Lewis', 'Lee', 
    'Walker', 'Hall', 'Allen', 'Young', 'Hernandez', 'King', 'Wright', 'Lopez', 
    'Hill', 'Scott', 'Green', 'Adams', 'Baker', 'Gonzalez', 'Nelson', 'Carter'
]


def create_random_user(idx):
    """Create a random user"""
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    username = f"{first_name.lower()}{last_name.lower()}{idx}"
    email = f"{username}@example.com"
    password_hash = generate_password_hash('Password@123')
    
    user = User(
        username=username,
        email=email,
        password_hash=password_hash,
        first_name=first_name,
        last_name=last_name,
        role='customer'
    )
    
    return user


def create_random_application(user_id):
    """Create a random loan application with realistic data"""
    # Generate realistic application data with good variation
    loan_amount = random.randint(1000, 100000)
    loan_purpose = random.choice(LOAN_PURPOSES)
    loan_term = random.choice([6, 12, 24, 36, 48, 60])
    
    # Age between 21 and 70 with higher probability in middle range
    age = int(random.triangular(21, 70, 40))
    
    # Income with realistic distribution (higher probability of middle incomes)
    annual_income = random.randint(20000, 150000)
    if random.random() < 0.1:  # 10% chance of high income
        annual_income = random.randint(150000, 300000)
    
    # Monthly expenses as percentage of monthly income
    monthly_income = annual_income / 12
    expense_ratio = random.triangular(0.2, 0.8, 0.4) # Most people spend around 40% of income
    monthly_expenses = monthly_income * expense_ratio
    
    # Credit score with realistic distribution
    # More likely to be in the middle range
    credit_score_base = random.triangular(300, 850, 680)
    credit_score = int(credit_score_base)
    
    # Existing debt as multiple of monthly income
    debt_income_multiplier = random.triangular(0, 24, 6) # Most have around 6 months income in debt
    existing_debt = monthly_income * debt_income_multiplier
    
    employment_status = random.choice(EMPLOYMENT_STATUSES)
    # Set employment length based on employment status
    if employment_status == 'unemployed':
        employment_length = 0
    elif employment_status == 'retired':
        employment_length = random.triangular(5, 40, 25)
    else:
        employment_length = random.triangular(0, 30, 5)
    
    home_ownership = random.choice(HOME_OWNERSHIP_TYPES)
    
    # Create the application
    application = LoanApplication(
        user_id=user_id,
        loan_amount=loan_amount,
        loan_purpose=loan_purpose,
        loan_term=loan_term,
        age=age,
        annual_income=annual_income,
        monthly_expenses=monthly_expenses,
        credit_score=credit_score,
        existing_debt=existing_debt,
        employment_status=employment_status,
        employment_length=employment_length,
        home_ownership=home_ownership,
        created_at=datetime.utcnow() - timedelta(days=random.randint(1, 60))
    )
    
    return application


def seed_sample_data():
    """Seed the database with sample data"""
    created_users = []
    created_applications = []
    
    with app.app_context():
        print("Started seeding sample data...")
        
        # Create admin/staff users
        for staff_user in STAFF_USERS:
            existing_user = User.query.filter_by(username=staff_user['username']).first()
            if existing_user:
                print(f"Staff user {staff_user['username']} already exists, skipping")
                continue
                
            user = User(
                username=staff_user['username'],
                email=staff_user['email'],
                password_hash=generate_password_hash(staff_user['password']),
                role=staff_user['role'],
                is_staff=True
            )
            db.session.add(user)
            created_users.append(user)
            print(f"Created staff user: {staff_user['username']}")
        
        # Create a demo user account if it doesn't exist
        if SEED_DEMO_USER:
            demo_user = User.query.filter_by(username='demouser').first()
            if not demo_user:
                demo_user = User(
                    username='demouser',
                    email='demo@example.com',
                    password_hash=generate_password_hash('Demo@123'),
                    first_name='Demo',
                    last_name='User',
                    role='customer'
                )
                db.session.add(demo_user)
                created_users.append(demo_user)
                print("Created demo user: demouser")
        
        # Create random users
        for i in range(NUM_SAMPLE_USERS):
            user = create_random_user(i)
            db.session.add(user)
            created_users.append(user)
            print(f"Created sample user: {user.username}")
        
        # Commit to get user IDs
        db.session.commit()
        
        # Create applications for each user
        for user in created_users:
            num_applications = random.randint(MIN_APPLICATIONS_PER_USER, MAX_APPLICATIONS_PER_USER)
            
            for _ in range(num_applications):
                application = create_random_application(user.id)
                db.session.add(application)
                created_applications.append(application)
                
                print(f"Created application for user {user.username}")
            
        # Commit to get application IDs
        db.session.commit()
        
        # Process applications and create risk assessments
        staff_users = [user for user in created_users if user.is_staff]
        
        for application in created_applications:
            # Process the application with the risk engine
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
                
                # 80% of approved applications are handled by staff
                if random.random() < 0.8 and staff_users:
                    handler = random.choice(staff_users)
                    application.handled_by_id = handler.id
                    application.handled_at = datetime.utcnow() - timedelta(days=random.randint(0, 10))
                    application.decision_notes = "Approved based on good credit history and ability to repay."
            
            elif assessment['recommendation'] == 'Reject':
                application.status = 'Rejected'
                
                # 90% of rejected applications are handled by staff
                if random.random() < 0.9 and staff_users:
                    handler = random.choice(staff_users)
                    application.handled_by_id = handler.id
                    application.handled_at = datetime.utcnow() - timedelta(days=random.randint(0, 10))
                    application.decision_notes = "Rejected due to high risk factors and probability of default."
            else:
                # 50/50 chance of still being under review or having been processed
                if random.random() < 0.5:
                    application.status = 'Under Review'
                else:
                    # Staff reviewed but still uncertain
                    if staff_users:
                        handler = random.choice(staff_users)
                        application.handled_by_id = handler.id
                        application.handled_at = datetime.utcnow() - timedelta(days=random.randint(0, 5))
                        application.decision_notes = "Additional verification needed before final decision."
                        
                        # 50/50 chance of being ultimately approved or rejected
                        if random.random() < 0.5:
                            application.status = 'Approved'
                        else:
                            application.status = 'Rejected'
            
            db.session.add(risk_assessment)
            
        # Final commit with all data
        db.session.commit()
        
        print(f"Seeding complete! Created {len(created_users)} users and {len(created_applications)} applications.")


if __name__ == "__main__":
    seed_sample_data()