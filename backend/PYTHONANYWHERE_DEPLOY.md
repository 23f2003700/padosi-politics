# Padosi Politics - PythonAnywhere Deployment

## Quick CLI Deployment

### Step 1: Get API Token
1. Create account at https://www.pythonanywhere.com
2. Go to **Account** → **API Token** → Create token
3. Copy your token

### Step 2: Set Environment Variables (PowerShell)
```powershell
$env:PA_USERNAME = "your-username"
$env:PA_API_TOKEN = "your-api-token-here"
```

### Step 3: Run Deployment Script
```powershell
cd d:\IITM\padosi-politics\backend
python deploy_pythonanywhere.py
```

### Step 4: Finish Setup in Console
The script will upload files. Then go to PythonAnywhere Bash console:

```bash
# Create virtual environment
mkvirtualenv padosi-env --python=/usr/bin/python3.10

# Install dependencies
cd ~/padosi-politics
pip install -r requirements.txt

# Initialize database
python -c "from app import create_app; from app.extensions import db; app = create_app('production'); app.app_context().push(); db.create_all(); print('Done!')"
```

### Step 5: Configure Web App
1. Go to **Web** tab
2. Set **Source code**: `/home/YOUR_USERNAME/padosi-politics`
3. Set **Virtualenv**: `/home/YOUR_USERNAME/.virtualenvs/padosi-env`
4. Click **Reload**

---

## Alternative: Full CLI with Git (Recommended)

If your code is on GitHub, this is easier:

### In PythonAnywhere Bash Console:
```bash
# Clone repo
git clone https://github.com/YOUR_USERNAME/padosi-politics.git
cd padosi-politics/backend

# Create virtualenv
mkvirtualenv padosi-env --python=/usr/bin/python3.10
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
FLASK_ENV=production
SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
JWT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
DATABASE_URL=sqlite:////home/$USER/padosi-politics/backend/padosi_prod.db
CORS_ORIGINS=https://padosi-politics.pages.dev
SERVERLESS=true
CELERY_ENABLED=false
EOF

# Initialize database
python -c "from app import create_app; from app.extensions import db; app = create_app('production'); app.app_context().push(); db.create_all()"
```

---

## WSGI Configuration

In **Web** tab → **WSGI configuration file**, replace content with:

```python
import sys
import os

project_home = '/home/YOUR_USERNAME/padosi-politics/backend'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.environ['FLASK_ENV'] = 'production'

from app import create_app
application = create_app('production')
```

---

## Free Tier Benefits
- ✅ **Never sleeps** (always on!)
- ✅ 1 web app
- ✅ 512 MB disk space
- ⚠️ Limited outbound HTTP (whitelist only)
- ⚠️ No custom domain on free tier

---

## Update Your Cloudflare Frontend

After deploying, update your frontend's API URL:

```powershell
cd d:\IITM\padosi-politics\frontend
# Edit .env.production
# Set: VITE_API_URL=https://YOUR_USERNAME.pythonanywhere.com/api

npm run build
npx wrangler pages deploy dist --project-name=padosi-politics
```

Your app will be live at: `https://YOUR_USERNAME.pythonanywhere.com`
