// Standalone Auth JavaScript for Offline Mode

document.addEventListener('DOMContentLoaded', function() {
    // Password toggle functionality
    const passwordToggles = document.querySelectorAll('.password-toggle');
    if (passwordToggles) {
        passwordToggles.forEach(toggle => {
            toggle.addEventListener('click', function() {
                const target = document.querySelector(this.getAttribute('data-target'));
                if (target) {
                    if (target.type === 'password') {
                        target.type = 'text';
                        this.innerHTML = '<span>👁️‍🗨️</span>';
                    } else {
                        target.type = 'password';
                        this.innerHTML = '<span>👁️</span>';
                    }
                }
            });
        });
    }

    // Password strength meter (if on registration page)
    const passwordInput = document.getElementById('password');
    const strengthMeter = document.getElementById('password-strength-meter');
    const strengthText = document.getElementById('password-strength-text');

    if (passwordInput && strengthMeter && strengthText) {
        passwordInput.addEventListener('input', function() {
            const password = this.value;
            let strength = 0;
            let feedback = '';

            // Length check
            if (password.length >= 8) strength += 1;
            if (password.length >= 10) strength += 1;

            // Character type checks
            if (/[A-Z]/.test(password)) strength += 1;
            if (/[a-z]/.test(password)) strength += 1;
            if (/[0-9]/.test(password)) strength += 1;
            if (/[^A-Za-z0-9]/.test(password)) strength += 1;

            // Update the UI
            const percentage = (strength / 6) * 100;
            strengthMeter.style.width = percentage + '%';

            // Remove any existing classes
            strengthMeter.classList.remove('bg-danger', 'bg-warning', 'bg-info', 'bg-success');

            // Add the appropriate class based on strength
            if (percentage <= 25) {
                strengthMeter.classList.add('bg-danger');
                feedback = 'Very Weak';
            } else if (percentage <= 50) {
                strengthMeter.classList.add('bg-warning');
                feedback = 'Weak';
            } else if (percentage <= 75) {
                strengthMeter.classList.add('bg-info');
                feedback = 'Good';
            } else {
                strengthMeter.classList.add('bg-success');
                feedback = 'Strong';
            }

            strengthText.textContent = 'Password strength: ' + feedback;
        });
    }

    // Alert auto-dismiss functionality
    const alerts = document.querySelectorAll('.alert-dismissible');
    if (alerts) {
        alerts.forEach(alert => {
            setTimeout(() => {
                alert.classList.remove('show');
                setTimeout(() => {
                    alert.remove();
                }, 150);
            }, 5000);
        });
    }

    // Form validation
    const forms = document.querySelectorAll('form.auth-form');
    if (forms) {
        forms.forEach(form => {
            form.addEventListener('submit', function(event) {
                const requiredFields = form.querySelectorAll('[required]');
                let valid = true;

                requiredFields.forEach(field => {
                    if (!field.value.trim()) {
                        valid = false;
                        // Add validation styling
                        field.classList.add('is-invalid');
                    } else {
                        field.classList.remove('is-invalid');
                    }
                });

                // Prevent form submission if validation fails
                if (!valid) {
                    event.preventDefault();
                }
            });
        });
    }
});