"""
Script to initialize all existing users with default roles and permissions
"""
from app import app, db
from models import User

def initialize_roles():
    """
    Initialize all users with default roles and staff permissions
    """
    print("Initializing user roles...")
    
    # Get all users
    users = User.query.all()
    
    # Set default values for each user
    for user in users:
        if user.id == 1:  # Make the first user an admin by default
            user.role = 'admin'
            user.is_staff = True
            print(f"Set user {user.username} (ID: {user.id}) as admin")
        else:
            user.role = 'customer'
            user.is_staff = False
            print(f"Set user {user.username} (ID: {user.id}) as customer")
    
    # Commit changes
    db.session.commit()
    print("User roles initialized successfully!")

if __name__ == "__main__":
    with app.app_context():
        initialize_roles()