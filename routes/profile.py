from flask import (
    Blueprint, render_template, redirect, url_for, 
    flash, request
)
from flask_login import login_required, current_user
from app import db
from models import User
from forms import ProfileUpdateForm, SecurityUpdateForm

bp = Blueprint('profile', __name__)

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Handle user profile viewing and updating"""
    form = ProfileUpdateForm(current_user.email)
    
    if form.validate_on_submit():
        # Update user profile
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.email = form.email.data
        current_user.phone = form.phone.data
        
        # Save changes to database
        db.session.commit()
        
        flash('Your profile has been updated successfully!', 'success')
        return redirect(url_for('profile.profile'))
    
    elif request.method == 'GET':
        # Pre-populate form with current data
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email.data = current_user.email
        form.phone.data = current_user.phone
    
    return render_template('profile.html', title='Profile', form=form)


@bp.route('/security', methods=['GET', 'POST'])
@login_required
def security():
    """Handle security settings (password change)"""
    form = SecurityUpdateForm()
    
    if form.validate_on_submit():
        # Verify current password
        if not current_user.check_password(form.current_password.data):
            flash('Current password is incorrect.', 'danger')
            return redirect(url_for('profile.security'))
        
        # Update password
        current_user.set_password(form.new_password.data)
        
        # Save changes to database
        db.session.commit()
        
        flash('Your password has been updated successfully!', 'success')
        return redirect(url_for('profile.security'))
    
    return render_template('security.html', title='Security Settings', form=form)
