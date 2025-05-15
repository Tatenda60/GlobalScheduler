#!/bin/bash

# This script runs model evaluation, initializes the database, and starts the Flask app

# Clear terminal
clear

# ANSI color codes
CYAN="\033[1;36m"
GREEN="\033[1;32m"
YELLOW="\033[1;33m"
RED="\033[1;31m"
RESET="\033[0m"

# Print header
echo -e "\n${CYAN}======================================================="
echo -e "         CREDIT RISK MODELING SYSTEM STARTUP           "
echo -e "=======================================================${RESET}\n"

# Step 1: Run model evaluation
echo -e "${CYAN}STEP 1: Running Model Evaluation...${RESET}"
python run_model_evaluation_only.py

# Step 2: Database setup
echo -e "\n${CYAN}======================================================="
echo -e "         DATABASE SETUP AND INITIALIZATION            "
echo -e "=======================================================${RESET}\n"

# Check if we have a database URL
if [ -z "$DATABASE_URL" ]; then
  echo -e "${RED}Error: DATABASE_URL environment variable is not set.${RESET}"
  echo -e "${YELLOW}Will use SQLite database as fallback.${RESET}"
else
  echo -e "${GREEN}Database connection string found.${RESET}"
fi

echo -e "${YELLOW}Initializing database tables...${RESET}"
# Run the database initialization script
python init_db.py
if [ $? -eq 0 ]; then
  echo -e "${GREEN}Database initialization successful.${RESET}"
else
  echo -e "${RED}Warning: Database initialization may have had issues.${RESET}"
  echo -e "${YELLOW}Application will still attempt to start.${RESET}"
fi

# Step 3: Start Flask app
echo -e "\n${CYAN}======================================================="
echo -e "         STARTING FLASK APPLICATION                   "
echo -e "=======================================================${RESET}\n"

echo -e "${YELLOW}Starting server on port 5000...${RESET}"
echo -e "${YELLOW}Press Ctrl+C to stop the server${RESET}\n"

# Start the application
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app