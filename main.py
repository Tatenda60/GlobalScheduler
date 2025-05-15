# Main application entry point
from app import app
from routes import auth, loan, profile, insights, admin
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Note: Model evaluation is now performed separately by run_model_evaluation.py
# which is executed by the startup.sh script before the Flask app starts
logger.info("Starting Flask application...")

# Register blueprints
app.register_blueprint(auth.bp)
app.register_blueprint(loan.bp)
app.register_blueprint(profile.bp)
app.register_blueprint(insights.bp)
app.register_blueprint(admin.bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
