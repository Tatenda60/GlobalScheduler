import os
import urllib.request

# Create directories if they don't exist
os.makedirs('static/vendor/css', exist_ok=True)
os.makedirs('static/vendor/js', exist_ok=True)

# URLs for dependencies
dependencies = {
    'static/vendor/css/bootstrap.min.css': 'https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css',
    'static/vendor/js/bootstrap.bundle.min.js': 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js',
    'static/vendor/js/chart.min.js': 'https://cdn.jsdelivr.net/npm/chart.js',
}

# Download each file
for target_path, url in dependencies.items():
    print(f"Downloading {url} to {target_path}...")
    try:
        urllib.request.urlretrieve(url, target_path)
        print(f"Successfully downloaded {target_path}")
    except Exception as e:
        print(f"Failed to download {url}: {e}")