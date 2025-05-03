from flask import (
    Blueprint, render_template, redirect, url_for, 
    flash, request, session
)
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from app import db
from models import User
from forms import LoginForm, RegistrationForm, ForgotPasswordForm, ResetPasswordForm

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    
    # Redirect if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('loan.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        # Look up user in database
        user = User.query.filter_by(username=form.username.data).first()
        
        # Check if user exists and password is correct
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))
        
        # Log the user in
        login_user(user, remember=form.remember_me.data)
        
        # Redirect to the page the user was trying to access
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('loan.index')
        
        flash('You have been logged in successfully!', 'success')
        return redirect(next_page)
    
    return render_template('auth/login.html', title='Log In', form=form)


@bp.route('/logout')
def logout():
    """Handle user logout"""
    logout_user()
    flash('You have been logged out successfully!', 'success')
    return redirect(url_for('auth.login'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration"""
    
    # Redirect if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('loan.index'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        # Create new user
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        
        # Add user to database
        db.session.add(user)
        db.session.commit()
        
        flash('Your account has been created successfully! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='Register', form=form)


@bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    """Handle password reset request"""
    
    # Redirect if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('loan.index'))
    
    form = ForgotPasswordForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user:
            # In a real application, this would send a password reset email
            # For demo purposes, we'll just store the user_id in session
            session['reset_user_id'] = user.id
            flash('Password reset instructions have been sent to your email.', 'info')
            return redirect(url_for('auth.reset_password'))
        else:
            flash('No account found with that email address.', 'danger')
    
    return render_template('auth/forgot_password.html', title='Forgot Password', form=form)


@bp.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    """Handle password reset"""
    
    # Redirect if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('loan.index'))
    
    # In a real application, we would verify a token from the email
    # For demo purposes, we're using the user_id from session
    user_id = session.get('reset_user_id')
    
    if not user_id:
        flash('Invalid or expired password reset link.', 'danger')
        return redirect(url_for('auth.forgot_password'))
    
    user = User.query.get(user_id)
    
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('auth.forgot_password'))
    
    form = ResetPasswordForm()
    
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        
        # Clear the session
        session.pop('reset_user_id', None)
        
        flash('Your password has been reset successfully. You can now log in with your new password.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html', title='Reset Password', form=form, reset=True)
