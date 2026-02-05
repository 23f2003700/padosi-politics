"""
PythonAnywhere CLI Deployment Script
Deploy Padosi Politics backend to PythonAnywhere using their API.

Prerequisites:
1. Create account at pythonanywhere.com
2. Get API token from: Account > API Token
3. Set environment variables:
   - PA_USERNAME: Your PythonAnywhere username
   - PA_API_TOKEN: Your API token

Usage:
  python deploy_pythonanywhere.py
"""

import os
import sys
import requests
import subprocess
from pathlib import Path

# Configuration
PA_USERNAME = os.environ.get('PA_USERNAME')
PA_API_TOKEN = os.environ.get('PA_API_TOKEN')
PA_HOST = 'www.pythonanywhere.com'
PYTHON_VERSION = '3.10'  # PythonAnywhere Python version

# API endpoints
API_BASE = f'https://{PA_HOST}/api/v0/user/{PA_USERNAME}'
HEADERS = {'Authorization': f'Token {PA_API_TOKEN}'}


def check_credentials():
    """Verify API credentials are set."""
    if not PA_USERNAME or not PA_API_TOKEN:
        print("❌ Error: Set PA_USERNAME and PA_API_TOKEN environment variables")
        print("\nGet your API token from: https://www.pythonanywhere.com/account/#api_token")
        print("\nWindows PowerShell:")
        print('  $env:PA_USERNAME = "yourusername"')
        print('  $env:PA_API_TOKEN = "your-api-token"')
        sys.exit(1)
    print(f"✅ Credentials found for user: {PA_USERNAME}")


def api_get(endpoint):
    """Make GET request to PythonAnywhere API."""
    response = requests.get(f'{API_BASE}{endpoint}', headers=HEADERS)
    return response


def api_post(endpoint, data=None, files=None):
    """Make POST request to PythonAnywhere API."""
    response = requests.post(f'{API_BASE}{endpoint}', headers=HEADERS, data=data, files=files)
    return response


def api_patch(endpoint, data=None):
    """Make PATCH request to PythonAnywhere API."""
    response = requests.patch(f'{API_BASE}{endpoint}', headers=HEADERS, data=data)
    return response


def api_delete(endpoint):
    """Make DELETE request to PythonAnywhere API."""
    response = requests.delete(f'{API_BASE}{endpoint}', headers=HEADERS)
    return response


def upload_file(local_path, remote_path):
    """Upload a file to PythonAnywhere."""
    with open(local_path, 'rb') as f:
        response = requests.post(
            f'https://{PA_HOST}/api/v0/user/{PA_USERNAME}/files/path{remote_path}',
            headers=HEADERS,
            files={'content': f}
        )
    return response


def create_directory(remote_path):
    """Create a directory on PythonAnywhere."""
    response = requests.post(
        f'https://{PA_HOST}/api/v0/user/{PA_USERNAME}/files/path{remote_path}/',
        headers=HEADERS
    )
    return response


def run_console_command(command):
    """Run a bash command in a PythonAnywhere console."""
    # Create a new bash console
    response = api_post('/consoles/', data={'executable': 'bash'})
    if response.status_code != 201:
        print(f"❌ Failed to create console: {response.text}")
        return None
    
    console_id = response.json()['id']
    
    # Send command to console
    response = requests.post(
        f'{API_BASE}/consoles/{console_id}/send_input/',
        headers=HEADERS,
        data={'input': command + '\n'}
    )
    
    return console_id


def get_webapp_info():
    """Get info about existing web app."""
    domain = f'{PA_USERNAME}.pythonanywhere.com'
    response = api_get(f'/webapps/{domain}/')
    return response


def create_webapp():
    """Create or update web app configuration."""
    domain = f'{PA_USERNAME}.pythonanywhere.com'
    
    # Check if webapp exists
    response = get_webapp_info()
    
    if response.status_code == 404:
        # Create new webapp
        print(f"📦 Creating web app: {domain}")
        response = api_post('/webapps/', data={
            'domain_name': domain,
            'python_version': PYTHON_VERSION,
        })
        if response.status_code != 201:
            print(f"❌ Failed to create webapp: {response.text}")
            return False
        print("✅ Web app created")
    else:
        print(f"✅ Web app exists: {domain}")
    
    return True


def upload_project():
    """Upload all project files."""
    project_dir = Path(__file__).parent
    remote_base = f'/home/{PA_USERNAME}/padosi-politics'
    
    print(f"\n📤 Uploading project files to {remote_base}...")
    
    # Create main directory
    create_directory(remote_base)
    
    # Files to upload
    files_to_upload = []
    
    # Get all Python files, config files, etc.
    for pattern in ['*.py', '*.txt', '*.toml', '.env.example']:
        files_to_upload.extend(project_dir.glob(pattern))
    
    # Add app directory
    app_dir = project_dir / 'app'
    if app_dir.exists():
        for py_file in app_dir.rglob('*.py'):
            files_to_upload.append(py_file)
    
    # Upload each file
    for local_file in files_to_upload:
        relative_path = local_file.relative_to(project_dir)
        remote_path = f'{remote_base}/{relative_path}'.replace('\\', '/')
        
        # Create parent directories
        parent_dir = str(relative_path.parent)
        if parent_dir != '.':
            dirs = parent_dir.replace('\\', '/').split('/')
            current = remote_base
            for d in dirs:
                current = f'{current}/{d}'
                create_directory(current)
        
        print(f"  Uploading: {relative_path}")
        response = upload_file(local_file, remote_path)
        if response.status_code not in [200, 201]:
            print(f"    ⚠️ Warning: {response.status_code}")
    
    print("✅ Files uploaded")
    return True


def configure_wsgi():
    """Configure WSGI file for Flask."""
    domain = f'{PA_USERNAME}.pythonanywhere.com'
    wsgi_path = f'/var/www/{PA_USERNAME.replace("-", "_")}_pythonanywhere_com_wsgi.py'
    
    wsgi_content = f'''# WSGI configuration for Padosi Politics
import sys
import os

# Add project to path
project_home = '/home/{PA_USERNAME}/padosi-politics'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['DATABASE_URL'] = 'sqlite:////home/{PA_USERNAME}/padosi-politics/padosi_prod.db'

# Import Flask app
from app import create_app
application = create_app('production')
'''
    
    print("\n⚙️ Configuring WSGI...")
    
    # Upload WSGI file
    response = requests.post(
        f'https://{PA_HOST}/api/v0/user/{PA_USERNAME}/files/path{wsgi_path}',
        headers=HEADERS,
        files={'content': wsgi_content.encode()}
    )
    
    if response.status_code in [200, 201]:
        print("✅ WSGI configured")
        return True
    else:
        print(f"❌ WSGI config failed: {response.text}")
        return False


def setup_virtualenv():
    """Create and setup virtual environment."""
    print("\n🐍 Setting up virtual environment...")
    
    venv_path = f'/home/{PA_USERNAME}/.virtualenvs/padosi-env'
    
    commands = [
        f'mkvirtualenv padosi-env --python=/usr/bin/python{PYTHON_VERSION}',
        f'workon padosi-env',
        f'pip install -r /home/{PA_USERNAME}/padosi-politics/requirements.txt',
    ]
    
    # We'll need to run these via console
    print("  Run these commands in PythonAnywhere Bash console:")
    for cmd in commands:
        print(f"    $ {cmd}")
    
    return venv_path


def configure_webapp_settings():
    """Configure webapp source directory and virtualenv."""
    domain = f'{PA_USERNAME}.pythonanywhere.com'
    
    print("\n⚙️ Configuring web app settings...")
    
    # Update webapp configuration
    response = api_patch(f'/webapps/{domain}/', data={
        'source_directory': f'/home/{PA_USERNAME}/padosi-politics',
        'virtualenv_path': f'/home/{PA_USERNAME}/.virtualenvs/padosi-env',
    })
    
    if response.status_code == 200:
        print("✅ Web app configured")
        return True
    else:
        print(f"⚠️ Config update: {response.text}")
        return True  # May already be configured


def reload_webapp():
    """Reload the web app."""
    domain = f'{PA_USERNAME}.pythonanywhere.com'
    
    print("\n🔄 Reloading web app...")
    response = api_post(f'/webapps/{domain}/reload/')
    
    if response.status_code == 200:
        print("✅ Web app reloaded")
        print(f"\n🎉 Deployment complete!")
        print(f"   URL: https://{domain}")
        return True
    else:
        print(f"❌ Reload failed: {response.text}")
        return False


def main():
    print("=" * 50)
    print("🚀 PythonAnywhere Deployment Script")
    print("=" * 50)
    
    check_credentials()
    
    # Step 1: Create/verify webapp
    if not create_webapp():
        return
    
    # Step 2: Upload project files
    if not upload_project():
        return
    
    # Step 3: Configure WSGI
    if not configure_wsgi():
        return
    
    # Step 4: Setup instructions
    venv_path = setup_virtualenv()
    
    # Step 5: Configure webapp
    configure_webapp_settings()
    
    # Step 6: Reload
    reload_webapp()
    
    print("\n" + "=" * 50)
    print("📋 MANUAL STEPS REQUIRED:")
    print("=" * 50)
    print(f"""
1. Go to: https://www.pythonanywhere.com/user/{PA_USERNAME}/consoles/
2. Open a Bash console and run:
   
   mkvirtualenv padosi-env --python=/usr/bin/python{PYTHON_VERSION}
   cd ~/padosi-politics
   pip install -r requirements.txt
   python -c "from app import create_app; from app.extensions import db; app = create_app('production'); app.app_context().push(); db.create_all(); print('DB created!')"

3. Go to Web tab and:
   - Set Source code: /home/{PA_USERNAME}/padosi-politics
   - Set Virtualenv: /home/{PA_USERNAME}/.virtualenvs/padosi-env
   - Click Reload

4. Your app will be live at:
   https://{PA_USERNAME}.pythonanywhere.com
""")


if __name__ == '__main__':
    main()
