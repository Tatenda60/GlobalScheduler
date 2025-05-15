#!/bin/bash

# This script runs the standalone model evaluation first, then attempts to start the Flask app.
# Even if the Flask app fails due to DB connection issues, the model evaluation will still run.

# Run the standalone model evaluation
python run_model_evaluation_only.py

# Inform the user
echo -e "\n\033[1;36m======================================================="
echo -e "        ATTEMPTING TO START FLASK APPLICATION           "
echo -e "=======================================================\033[0m\n"

echo -e "\033[1;33mNote: If the database connection fails, you can still see the model evaluation metrics above.\033[0m"

# Try to start the Flask app
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app