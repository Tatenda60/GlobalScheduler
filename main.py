# Main application entry point
from app import app
from routes import auth, loan, profile, insights

# Register blueprints
app.register_blueprint(auth.bp)
app.register_blueprint(loan.bp)
app.register_blueprint(profile.bp)
app.register_blueprint(insights.bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
