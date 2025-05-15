"""
Start the application with model evaluation.
This script runs the model evaluation first and then starts the Flask app.
"""
import os
import subprocess
import sys
import time
from datetime import datetime

# ANSI color codes
RESET = "\033[0m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
BOLD = "\033[1m"

def print_header(message):
    """Print a formatted header"""
    print(f"\n{BOLD}{CYAN}{'=' * 60}{RESET}")
    print(f"{BOLD}{CYAN}{message.center(60)}{RESET}")
    print(f"{BOLD}{CYAN}{'=' * 60}{RESET}\n")

def main():
    """Run model evaluation and start the Flask app"""
    # Clear terminal
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print_header("CREDIT RISK MODELING SYSTEM STARTUP")
    print(f"{BOLD}Date and Time:{RESET} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Run model evaluation
    print(f"\n{YELLOW}STEP 1: Running Model Evaluation...{RESET}")
    try:
        subprocess.run([sys.executable, "run_model_evaluation.py"], check=True)
        print(f"{GREEN}Model evaluation completed successfully.{RESET}")
    except subprocess.CalledProcessError:
        print(f"\n{YELLOW}WARNING: Model evaluation encountered issues but we'll continue.{RESET}")
    
    # Step 2: Start the Flask application
    print(f"\n{YELLOW}STEP 2: Starting Flask Application...{RESET}")
    print(f"{YELLOW}Press Ctrl+C to stop the server.{RESET}\n")
    
    try:
        # We use subprocess.run with shell=True to pass the complex command
        subprocess.run("gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app", shell=True)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Server stopped by user.{RESET}")
    except Exception as e:
        print(f"\n{YELLOW}Error starting Flask application: {str(e)}{RESET}")

if __name__ == "__main__":
    main()