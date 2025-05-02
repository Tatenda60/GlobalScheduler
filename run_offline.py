#!/usr/bin/env python3
"""
Offline Mode Runner
This script first ensures all dependencies are downloaded for offline use
and then launches the Flask application.
"""

import os
import sys
import subprocess

def main():
    """Main function to launch the application in offline mode"""
    print("Initializing Credit Risk Modeling System in Offline Mode...")
    
    # Step 1: Run the offline setup script to download dependencies
    print("\n=== Checking and downloading offline dependencies ===")
    try:
        exit_code = subprocess.call([sys.executable, 'offline_setup.py'])
        if exit_code != 0:
            print("Warning: There were issues setting up offline dependencies.")
            print("The application may not function correctly without internet access.")
    except Exception as e:
        print(f"Error during offline setup: {e}")
    
    # Step 2: Start the Flask application using gunicorn
    print("\n=== Starting Credit Risk Modeling System ===")
    os.environ['FLASK_DEBUG'] = '0'  # Disable debug mode for production
    
    try:
        # Use gunicorn to run the app
        subprocess.call(['gunicorn', '--bind', '0.0.0.0:5000', '--reuse-port', 'main:app'])
    except KeyboardInterrupt:
        print("\nShutting down the server...")
    except Exception as e:
        print(f"Error starting the server: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())