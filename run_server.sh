#!/bin/bash

# Run model evaluation first
echo -e "\n\033[1;36m======================================================="
echo -e "               RUNNING MODEL EVALUATION                "
echo -e "=======================================================\033[0m\n"

python run_model_evaluation.py

echo -e "\n\033[1;36m======================================================="
echo -e "               STARTING FLASK APPLICATION               "
echo -e "=======================================================\033[0m\n"

# Start the Flask application
# Use the local database
echo "Setting up PostgreSQL database connection..."
export DATABASE_URL=${DATABASE_URL}
export PGUSER=${PGUSER}
export PGPASSWORD=${PGPASSWORD}
export PGHOST=${PGHOST}
export PGPORT=${PGPORT}
export PGDATABASE=${PGDATABASE}

# Start the Flask application
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app