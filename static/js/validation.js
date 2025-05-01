// Form validation functions

// Validate password strength
function validatePassword(password) {
    // Requirements:
    // - 8-12 characters long
    // - At least 1 uppercase, 1 lowercase, 1 number, 1 special character
    // - No spaces
    
    const lengthValid = password.length >= 8 && password.length <= 12;
    const hasUppercase = /[A-Z]/.test(password);
    const hasLowercase = /[a-z]/.test(password);
    const hasNumber = /[0-9]/.test(password);
    const hasSpecial = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password);
    const noSpaces = !/\s/.test(password);
    
    return {
        isValid: lengthValid && hasUppercase && hasLowercase && hasNumber && hasSpecial && noSpaces,
        errors: {
            length: !lengthValid,
            uppercase: !hasUppercase,
            lowercase: !hasLowercase,
            number: !hasNumber,
            special: !hasSpecial,
            spaces: !noSpaces
        }
    };
}

// Update password strength meter
function updatePasswordStrength(password, meterElement, feedbackElement) {
    const validation = validatePassword(password);
    const errors = validation.errors;
    let strength = 0;
    let feedback = '';
    
    // Calculate strength score (0-5)
    if (!errors.length) strength += 1;
    if (!errors.uppercase) strength += 1;
    if (!errors.lowercase) strength += 1;
    if (!errors.number) strength += 1;
    if (!errors.special) strength += 1;
    
    // Subtract for spaces
    if (errors.spaces) strength = Math.max(0, strength - 1);
    
    // Update meter
    const percent = (strength / 5) * 100;
    meterElement.style.width = percent + '%';
    
    // Set color based on strength
    if (strength <= 1) {
        meterElement.className = 'progress-bar bg-danger';
        feedback = 'Very weak';
    } else if (strength === 2) {
        meterElement.className = 'progress-bar bg-warning';
        feedback = 'Weak';
    } else if (strength === 3) {
        meterElement.className = 'progress-bar bg-info';
        feedback = 'Fair';
    } else if (strength === 4) {
        meterElement.className = 'progress-bar bg-primary';
        feedback = 'Good';
    } else {
        meterElement.className = 'progress-bar bg-success';
        feedback = 'Strong';
    }
    
    // Update feedback
    feedbackElement.textContent = feedback;
    
    // Add detailed error messages
    let errorMessages = [];
    if (errors.length) errorMessages.push('Password must be 8-12 characters long');
    if (errors.uppercase) errorMessages.push('Password must contain at least one uppercase letter');
    if (errors.lowercase) errorMessages.push('Password must contain at least one lowercase letter');
    if (errors.number) errorMessages.push('Password must contain at least one number');
    if (errors.special) errorMessages.push('Password must contain at least one special character');
    if (errors.spaces) errorMessages.push('Password cannot contain spaces');
    
    // Display error messages if there are any
    if (errorMessages.length > 0) {
        const errorList = document.createElement('ul');
        errorList.className = 'text-danger password-errors';
        errorMessages.forEach(msg => {
            const li = document.createElement('li');
            li.textContent = msg;
            errorList.appendChild(li);
        });
        
        // Remove any existing error list
        const existingErrorList = document.querySelector('.password-errors');
        if (existingErrorList) {
            existingErrorList.remove();
        }
        
        // Add the new error list after the feedback element
        feedbackElement.parentNode.appendChild(errorList);
    } else {
        // Remove error list if password is valid
        const existingErrorList = document.querySelector('.password-errors');
        if (existingErrorList) {
            existingErrorList.remove();
        }
    }
    
    return validation.isValid;
}

// Initialize password validation on registration and security pages
document.addEventListener('DOMContentLoaded', function() {
    // Registration page
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        const passwordField = document.getElementById('password');
        const confirmPasswordField = document.getElementById('confirm_password');
        const strengthMeter = document.getElementById('password-strength-meter');
        const strengthFeedback = document.getElementById('password-strength-text');
        
        if (passwordField && strengthMeter && strengthFeedback) {
            passwordField.addEventListener('input', function() {
                updatePasswordStrength(this.value, strengthMeter, strengthFeedback);
            });
            
            registerForm.addEventListener('submit', function(event) {
                const isValid = updatePasswordStrength(passwordField.value, strengthMeter, strengthFeedback);
                if (!isValid) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                
                // Check if passwords match
                if (passwordField.value !== confirmPasswordField.value) {
                    event.preventDefault();
                    event.stopPropagation();
                    
                    // Show error message
                    const errorDiv = document.createElement('div');
                    errorDiv.className = 'alert alert-danger';
                    errorDiv.textContent = 'Passwords do not match';
                    
                    // Remove any existing error message
                    const existingError = document.querySelector('.alert-danger');
                    if (existingError) {
                        existingError.remove();
                    }
                    
                    // Add error before the form
                    registerForm.parentNode.insertBefore(errorDiv, registerForm);
                }
            });
        }
    }
    
    // Security page (password change)
    const securityForm = document.getElementById('security-form');
    if (securityForm) {
        const newPasswordField = document.getElementById('new_password');
        const confirmPasswordField = document.getElementById('confirm_password');
        const strengthMeter = document.getElementById('password-strength-meter');
        const strengthFeedback = document.getElementById('password-strength-text');
        
        if (newPasswordField && strengthMeter && strengthFeedback) {
            newPasswordField.addEventListener('input', function() {
                updatePasswordStrength(this.value, strengthMeter, strengthFeedback);
            });
            
            securityForm.addEventListener('submit', function(event) {
                const isValid = updatePasswordStrength(newPasswordField.value, strengthMeter, strengthFeedback);
                if (!isValid) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                
                // Check if passwords match
                if (newPasswordField.value !== confirmPasswordField.value) {
                    event.preventDefault();
                    event.stopPropagation();
                    
                    // Show error message
                    const errorDiv = document.createElement('div');
                    errorDiv.className = 'alert alert-danger';
                    errorDiv.textContent = 'Passwords do not match';
                    
                    // Remove any existing error message
                    const existingError = document.querySelector('.alert-danger');
                    if (existingError) {
                        existingError.remove();
                    }
                    
                    // Add error before the form
                    securityForm.parentNode.insertBefore(errorDiv, securityForm);
                }
            });
        }
    }
});

// Validate loan application form
function validateLoanForm() {
    const form = document.getElementById('loan-application-form');
    if (!form) return;
    
    form.addEventListener('submit', function(event) {
        let isValid = true;
        
        // Validate loan amount
        const loanAmount = parseFloat(document.getElementById('loan_amount').value);
        if (isNaN(loanAmount) || loanAmount < 1000 || loanAmount > 100000) {
            showError('loan_amount', 'Loan amount must be between $1,000 and $100,000');
            isValid = false;
        } else {
            clearError('loan_amount');
        }
        
        // Validate loan purpose
        const loanPurpose = document.getElementById('loan_purpose').value;
        if (!loanPurpose) {
            showError('loan_purpose', 'Please select a loan purpose');
            isValid = false;
        } else {
            clearError('loan_purpose');
        }
        
        // Validate loan term
        const loanTerm = parseInt(document.getElementById('loan_term').value);
        if (isNaN(loanTerm) || loanTerm < 6 || loanTerm > 60) {
            showError('loan_term', 'Loan term must be between 6 and 60 months');
            isValid = false;
        } else {
            clearError('loan_term');
        }
        
        // Validate age
        const age = parseInt(document.getElementById('age').value);
        if (isNaN(age) || age < 18 || age > 100) {
            showError('age', 'Age must be between 18 and 100');
            isValid = false;
        } else {
            clearError('age');
        }
        
        // Validate income
        const income = parseFloat(document.getElementById('annual_income').value);
        if (isNaN(income) || income <= 0) {
            showError('annual_income', 'Please enter a valid annual income');
            isValid = false;
        } else {
            clearError('annual_income');
        }
        
        // Validate expenses
        const expenses = parseFloat(document.getElementById('monthly_expenses').value);
        if (isNaN(expenses) || expenses < 0) {
            showError('monthly_expenses', 'Monthly expenses cannot be negative');
            isValid = false;
        } else {
            clearError('monthly_expenses');
        }
        
        // Validate credit score
        const creditScore = parseInt(document.getElementById('credit_score').value);
        if (isNaN(creditScore) || creditScore < 300 || creditScore > 850) {
            showError('credit_score', 'Credit score must be between 300 and 850');
            isValid = false;
        } else {
            clearError('credit_score');
        }
        
        // If form is invalid, prevent submission
        if (!isValid) {
            event.preventDefault();
            event.stopPropagation();
            
            // Show summary error
            const errorDiv = document.createElement('div');
            errorDiv.className = 'alert alert-danger';
            errorDiv.textContent = 'Please correct the errors in the form before submitting.';
            
            // Remove any existing error message
            const existingError = document.querySelector('.form-error-summary');
            if (existingError) {
                existingError.remove();
            }
            
            // Add error class to summary
            errorDiv.classList.add('form-error-summary');
            
            // Add error at the top of the form
            form.prepend(errorDiv);
            
            // Scroll to top of form
            window.scrollTo({
                top: form.offsetTop - 20,
                behavior: 'smooth'
            });
        }
    });
    
    // Helper function to show field error
    function showError(fieldId, message) {
        const field = document.getElementById(fieldId);
        field.classList.add('is-invalid');
        
        // Create or update error message
        let errorDiv = field.nextElementSibling;
        if (!errorDiv || !errorDiv.classList.contains('invalid-feedback')) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'invalid-feedback';
            field.parentNode.insertBefore(errorDiv, field.nextSibling);
        }
        
        errorDiv.textContent = message;
    }
    
    // Helper function to clear field error
    function clearError(fieldId) {
        const field = document.getElementById(fieldId);
        field.classList.remove('is-invalid');
        
        // Remove error message if it exists
        const errorDiv = field.nextElementSibling;
        if (errorDiv && errorDiv.classList.contains('invalid-feedback')) {
            errorDiv.textContent = '';
        }
    }
}

// Initialize form validations
document.addEventListener('DOMContentLoaded', function() {
    validateLoanForm();
});
