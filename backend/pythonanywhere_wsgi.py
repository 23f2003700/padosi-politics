# PythonAnywhere WSGI Configuration
# Copy this content to your WSGI file in PythonAnywhere Web tab
# Path: /var/www/YOUR_USERNAME_pythonanywhere_com_wsgi.py

import sys
import os

# IMPORTANT: Replace YOUR_USERNAME with your actual PythonAnywhere username
project_home = '/home/YOUR_USERNAME/padosi-politics/backend'

# Add project to Python path
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Load environment variables from .env file
from dotenv import load_dotenv
env_path = os.path.join(project_home, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)

# Set production environment
os.environ['FLASK_ENV'] = 'production'

# Import and create Flask app
from app import create_app
application = create_app('production')
