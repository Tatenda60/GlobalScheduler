import os
import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy
db = SQLAlchemy(model_class=Base)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key_for_development")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure database with fallback to SQLite
db_url = os.environ.get("DATABASE_URL")
sqlite_url = "sqlite:///credit_risk.db"

# Try to use PostgreSQL but fallback to SQLite if connection fails
if db_url and 'postgres' in db_url:
    try:
        import psycopg2
        # Test the connection
        conn = psycopg2.connect(db_url)
        conn.close()
        # If we get here, connection worked
        app.config["SQLALCHEMY_DATABASE_URI"] = db_url
        print(f"Using PostgreSQL database")
    except Exception as e:
        print(f"PostgreSQL connection failed: {e}")
        print(f"Falling back to SQLite database")
        app.config["SQLALCHEMY_DATABASE_URI"] = sqlite_url
else:
    print(f"No valid DATABASE_URL found. Using SQLite database")
    app.config["SQLALCHEMY_DATABASE_URI"] = sqlite_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the database
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "info"

# Create all tables
with app.app_context():
    # Import models to ensure tables are created
    from models import User, LoanApplication, RiskAssessment
    db.create_all()

# Import the user loader function
from models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
