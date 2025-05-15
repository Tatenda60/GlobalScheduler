"""
Initialize database tables and create sample data.
This script runs when the application first starts to ensure the database is set up.
"""
import os
import sys
from app import app, db
from models import User, LoanApplication, RiskAssessment
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def init_database():
    """Initialize the database tables"""
    try:
        # Create all tables
        with app.app_context():
            db.create_all()
            logger.info("Database tables created successfully")
            
            # Check if we have any users
            user_count = User.query.count()
            if user_count == 0:
                logger.info("No users found, creating sample data")
                try:
                    # Try to import and run the seed_applications function
                    from seed_applications import seed_sample_data
                    seed_sample_data()
                    logger.info("Sample data created successfully")
                except Exception as e:
                    logger.error(f"Error creating sample data: {str(e)}")
            else:
                logger.info(f"Found {user_count} existing users. Skipping sample data creation.")
                
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        return False
        
    return True

if __name__ == "__main__":
    # Run the database initialization
    success = init_database()
    sys.exit(0 if success else 1)