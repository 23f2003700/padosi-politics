#!/bin/bash
# PythonAnywhere Setup Script
# Run this in PythonAnywhere Bash console after cloning repo

set -e

echo "🚀 Setting up Padosi Politics on PythonAnywhere"
echo "   Frontend: Cloudflare Pages (padosi-politics.pages.dev)"
echo "   Backend: PythonAnywhere (this server)"
echo ""

# Variables
PROJECT_DIR="$HOME/padosi-politics/backend"
VENV_DIR="$HOME/.virtualenvs/padosi-env"
PYTHON_VERSION="python3.10"
FRONTEND_URL="https://padosi-politics.pages.dev"

# Navigate to project
cd "$PROJECT_DIR"
echo "📁 Working directory: $(pwd)"

# Create virtualenv if not exists
if [ ! -d "$VENV_DIR" ]; then
    echo "🐍 Creating virtual environment..."
    $PYTHON_VERSION -m venv $VENV_DIR
else
    echo "🐍 Virtual environment already exists"
fi

# Activate virtualenv
echo "🐍 Activating virtual environment..."
source $VENV_DIR/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Generate secrets
SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
JWT_SECRET=$(python -c "import secrets; print(secrets.token_hex(32))")
CRON_SECRET=$(python -c "import secrets; print(secrets.token_hex(16))")

# Create .env if not exists
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env file..."
    cat > .env << EOF
# Padosi Politics - Production Environment
# Backend: PythonAnywhere
# Frontend: Cloudflare Pages

FLASK_ENV=production
SECRET_KEY=$SECRET_KEY
JWT_SECRET_KEY=$JWT_SECRET
SECURITY_PASSWORD_SALT=$(python -c "import secrets; print(secrets.token_hex(16))")
DATABASE_URL=sqlite:///$PROJECT_DIR/padosi_prod.db

# CORS - Allow Cloudflare Pages frontend
CORS_ORIGINS=$FRONTEND_URL
FRONTEND_URL=$FRONTEND_URL

# Task settings (no Celery on PythonAnywhere)
SERVERLESS=true
CELERY_ENABLED=false

# Cron secret - SAVE THIS! Add to Cloudflare Worker secrets
CRON_SECRET=$CRON_SECRET
EOF
    echo "✅ .env created"
    echo ""
    echo "🔑 IMPORTANT - Save these values:"
    echo "   CRON_SECRET=$CRON_SECRET"
    echo ""
else
    echo "✅ .env already exists"
fi

# Initialize database
echo "🗄️ Initializing database..."
python << 'PYEOF'
from app import create_app
from app.extensions import db

app = create_app('production')
with app.app_context():
    db.create_all()
    print("✅ Database tables created!")
    
    # Check if we need to seed
    from app.models import User
    if User.query.count() == 0:
        print("📝 Run 'python seed_data.py' to add test data")
    else:
        print(f"✅ Database has {User.query.count()} users")
PYEOF

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "NEXT STEPS:"
echo ""
echo "1️⃣  Go to Web tab in PythonAnywhere dashboard"
echo ""
echo "2️⃣  Set these values:"
echo "    Source code: $PROJECT_DIR"
echo "    Virtualenv: $VENV_DIR"
echo ""
echo "3️⃣  Edit WSGI file and replace with:"
echo "----------------------------------------"
cat << WSGIEOF
import sys
import os

project_home = '/home/$USER/padosi-politics/backend'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

from dotenv import load_dotenv
load_dotenv(os.path.join(project_home, '.env'))

os.environ['FLASK_ENV'] = 'production'

from app import create_app
application = create_app('production')
WSGIEOF
echo "----------------------------------------"
echo ""
echo "4️⃣  Click RELOAD button"
echo ""
echo "5️⃣  Your API will be live at:"
echo "    https://$USER.pythonanywhere.com/api"
echo ""
echo "6️⃣  Update Cloudflare Worker with CRON_SECRET from .env"
echo ""
