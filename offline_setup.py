#!/usr/bin/env python3
"""
Offline Setup Script
This script downloads all external dependencies and configures the application
to run completely offline, without internet access.
"""

import os
import sys
import urllib.request
from pathlib import Path

# Directories for static files
BASE_DIR = Path('static/vendor')
CSS_DIR = BASE_DIR / 'css'
JS_DIR = BASE_DIR / 'js'
FONT_DIR = BASE_DIR / 'fontawesome/webfonts'

# List of dependencies to download
DEPENDENCIES = {
    # Bootstrap
    f'{CSS_DIR}/bootstrap.min.css': 'https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css',
    f'{JS_DIR}/bootstrap.bundle.min.js': 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js',
    
    # Chart.js
    f'{JS_DIR}/chart.min.js': 'https://cdn.jsdelivr.net/npm/chart.js',
    
    # Font Awesome CSS
    f'{BASE_DIR}/fontawesome/css/all.min.css': 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css',
    f'{BASE_DIR}/fontawesome/css/fontawesome.min.css': 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/fontawesome.min.css',
    f'{BASE_DIR}/fontawesome/css/solid.min.css': 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/solid.min.css',
    f'{BASE_DIR}/fontawesome/css/regular.min.css': 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/regular.min.css',
    
    # Font Awesome Fonts
    f'{FONT_DIR}/fa-solid-900.woff2': 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/webfonts/fa-solid-900.woff2',
    f'{FONT_DIR}/fa-solid-900.ttf': 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/webfonts/fa-solid-900.ttf',
    f'{FONT_DIR}/fa-regular-400.woff2': 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/webfonts/fa-regular-400.woff2',
    f'{FONT_DIR}/fa-regular-400.ttf': 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/webfonts/fa-regular-400.ttf',
}

def ensure_dirs():
    """Create directories if they don't exist"""
    for dir_path in [CSS_DIR, JS_DIR, BASE_DIR / 'fontawesome/css', FONT_DIR]:
        dir_path.mkdir(parents=True, exist_ok=True)

def download_dependencies():
    """Download all external dependencies"""
    print("Setting up offline mode...")
    
    # Create required directories
    ensure_dirs()
    
    # Download each file
    success_count = 0
    total_files = len(DEPENDENCIES)
    
    for target_path, url in DEPENDENCIES.items():
        if Path(target_path).exists():
            print(f"Already exists: {target_path}")
            success_count += 1
            continue
            
        print(f"Downloading {url} to {target_path}...")
        try:
            urllib.request.urlretrieve(url, target_path)
            success_count += 1
            print(f"Successfully downloaded {target_path}")
        except Exception as e:
            print(f"Failed to download {url}: {e}")
    
    # Report success
    if success_count == total_files:
        print("\nAll dependencies successfully downloaded/verified!")
        print("The application is now configured to run in offline mode.")
    else:
        print(f"\nDownloaded {success_count} of {total_files} dependencies.")
        print("Some dependencies could not be downloaded. The application may not work correctly offline.")

if __name__ == "__main__":
    download_dependencies()