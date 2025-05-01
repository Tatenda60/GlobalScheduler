from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField, BooleanField, 
    FloatField, IntegerField, SelectField, TextAreaField,
    FileField
)
from wtforms.validators import (
    DataRequired, Email, EqualTo, Length, ValidationError,
    NumberRange, Regexp
)
from models import User

class LoginForm(FlaskForm):
    """Login form for user authentication"""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')


class RegistrationForm(FlaskForm):
    """Registration form for new users"""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, max=12, message="Password must be 8-12 characters long"),
        Regexp(
            r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$',
            message="Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character"
        )
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), 
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        """Check if username is already taken"""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is already taken. Please choose a different one.')
    
    def validate_email(self, email):
        """Check if email is already registered"""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already registered. Please use a different one.')


class ForgotPasswordForm(FlaskForm):
    """Form for password reset request"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    """Form for setting a new password"""
    password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, max=12, message="Password must be 8-12 characters long"),
        Regexp(
            r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$',
            message="Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character"
        )
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(), 
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Reset Password')


class LoanApplicationForm(FlaskForm):
    """Form for loan application"""
    # Loan details
    loan_amount = FloatField('Loan Amount ($)', validators=[
        DataRequired(),
        NumberRange(min=1000, max=100000, message="Loan amount must be between $1,000 and $100,000")
    ])
    loan_purpose = SelectField('Loan Purpose', validators=[DataRequired()], choices=[
        ('', 'Select a purpose'),
        ('business', 'Business Expansion'),
        ('equipment', 'Equipment Purchase'),
        ('inventory', 'Inventory Purchase'),
        ('refinance', 'Debt Refinancing'),
        ('working_capital', 'Working Capital'),
        ('other', 'Other')
    ])
    loan_term = IntegerField('Loan Term (months)', validators=[
        DataRequired(),
        NumberRange(min=6, max=60, message="Loan term must be between 6 and 60 months")
    ])
    
    # Personal financial information
    age = IntegerField('Age', validators=[
        DataRequired(),
        NumberRange(min=18, max=100, message="Age must be between 18 and 100")
    ])
    annual_income = FloatField('Annual Income ($)', validators=[
        DataRequired(),
        NumberRange(min=0, message="Annual income cannot be negative")
    ])
    monthly_expenses = FloatField('Monthly Expenses ($)', validators=[
        DataRequired(),
        NumberRange(min=0, message="Monthly expenses cannot be negative")
    ])
    credit_score = IntegerField('Credit Score', validators=[
        DataRequired(),
        NumberRange(min=300, max=850, message="Credit score must be between 300 and 850")
    ])
    existing_debt = FloatField('Existing Debt ($)', validators=[
        DataRequired(),
        NumberRange(min=0, message="Existing debt cannot be negative")
    ])
    employment_status = SelectField('Employment Status', validators=[DataRequired()], choices=[
        ('', 'Select status'),
        ('full_time', 'Full-Time Employed'),
        ('part_time', 'Part-Time Employed'),
        ('self_employed', 'Self-Employed'),
        ('unemployed', 'Unemployed'),
        ('retired', 'Retired')
    ])
    employment_length = FloatField('Years at Current Employment', validators=[
        NumberRange(min=0, message="Employment length cannot be negative")
    ])
    home_ownership = SelectField('Home Ownership', validators=[DataRequired()], choices=[
        ('', 'Select ownership type'),
        ('own', 'Own'),
        ('mortgage', 'Mortgage'),
        ('rent', 'Rent'),
        ('other', 'Other')
    ])
    
    submit = SubmitField('Submit Application')


class ProfileUpdateForm(FlaskForm):
    """Form for updating user profile"""
    first_name = StringField('First Name', validators=[Length(max=64)])
    last_name = StringField('Last Name', validators=[Length(max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[Length(max=20)])
    submit = SubmitField('Update Profile')
    
    def __init__(self, original_email, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        self.original_email = original_email
        
    def validate_email(self, email):
        """Validate that the new email is not already in use"""
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email already in use. Please use a different one.')


class SecurityUpdateForm(FlaskForm):
    """Form for updating security settings"""
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, max=12, message="Password must be 8-12 characters long"),
        Regexp(
            r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$',
            message="Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character"
        )
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(), 
        EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField('Update Password')


class CSVUploadForm(FlaskForm):
    """Form for uploading CSV data"""
    csv_file = FileField('Upload CSV File', validators=[DataRequired()])
    submit = SubmitField('Upload')
