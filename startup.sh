#!/bin/bash

# Set executable permissions for this script
chmod +x startup.sh

# Clear terminal and print header
clear
echo -e "\n\033[1;36m======================================================="
echo -e "               MODEL EVALUATION METRICS                "
echo -e "=======================================================\033[0m\n"

# Run model evaluation
python run_model_evaluation.py

echo -e "\n\033[1;36m======================================================="
echo -e "          ATTEMPTING TO START FLASK APPLICATION         "
echo -e "=======================================================\033[0m\n"

# Try to start the Flask app with gunicorn
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app