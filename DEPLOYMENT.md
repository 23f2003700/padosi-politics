# Padosi Politics - Deployment Guide

This guide covers deploying Padosi Politics with:
- **Frontend**: Cloudflare Pages (Free)
- **Backend**: Render.com (Free tier)
- **Database**: PostgreSQL on Render (Free)

---

## 🚀 Quick Deployment

### Step 1: Deploy Backend to Render

1. **Create a Render Account**: https://render.com

2. **Connect GitHub Repository**:
   - Go to Render Dashboard > New > Blueprint
   - Connect your GitHub repo
   - Render will detect `render.yaml` and set up everything automatically

3. **Or Manual Setup**:
   - Create a new **Web Service**
   - Connect your GitHub repo
   - Settings:
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 4 "app:create_app()"`
     - **Root Directory**: `backend`

4. **Environment Variables** (set in Render Dashboard):
   ```
   FLASK_ENV=production
   SECRET_KEY=<generate-random-32-char-string>
   JWT_SECRET_KEY=<generate-random-32-char-string>
   CORS_ORIGINS=https://your-app.pages.dev
   SERVERLESS=true
   CELERY_ENABLED=false
   CRON_SECRET=<generate-random-string>
   ```

5. **Create PostgreSQL Database**:
   - New > PostgreSQL
   - Name: `padosi-politics-db`
   - Link it to your web service

6. **Initialize Database** (run once after first deploy):
   - Go to your web service > Shell
   - Run: `python init_production_db.py`

7. **Note your Backend URL**: `https://your-app.onrender.com`

---

### Step 2: Deploy Frontend to Cloudflare Pages

1. **Create Cloudflare Account**: https://dash.cloudflare.com

2. **Deploy via CLI** (recommended):
   ```bash
   cd frontend
   npm run build
   npx wrangler pages deploy dist --project-name=padosi-politics
   ```

3. **Or via Dashboard**:
   - Pages > Create a project > Connect to Git
   - Framework: Vue
   - Build command: `npm run build`
   - Output directory: `dist`
   - Root directory: `frontend`

4. **Set Environment Variable**:
   - Settings > Environment Variables
   - Add: `VITE_API_URL = https://your-backend.onrender.com/api`
   - Trigger a redeploy for changes to take effect

5. **Your site is live at**: `https://padosi-politics.pages.dev`

---

## 🔧 Configuration Details

### Backend Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Flask secret key (32+ chars) | Yes |
| `JWT_SECRET_KEY` | JWT signing key (32+ chars) | Yes |
| `DATABASE_URL` | PostgreSQL connection string | Auto by Render |
| `CORS_ORIGINS` | Allowed frontend domains | Yes |
| `SERVERLESS` | Enable serverless mode | Yes (`true`) |
| `CELERY_ENABLED` | Disable Celery (no Redis) | Yes (`false`) |
| `CRON_SECRET` | Secret for cron endpoints | Yes |

### Frontend Environment Variables

| Variable | Description |
|----------|-------------|
| `VITE_API_URL` | Backend API URL |

---

## ⏰ Scheduled Tasks (Cron Jobs)

Padosi Politics has background tasks for:
- Auto-escalating old complaints
- Sending reminders
- Cleaning up old notifications
- Calculating statistics

### Option 1: Cloudflare Cron Triggers (Recommended)

Create a Worker to call your backend cron endpoints:

```javascript
// workers/cron-worker.js
export default {
  async scheduled(event, env, ctx) {
    const tasks = [
      '/api/cron/escalate',
      '/api/cron/reminders', 
      '/api/cron/cleanup'
    ];
    
    for (const task of tasks) {
      await fetch(`${env.BACKEND_URL}${task}`, {
        headers: { 'X-Cron-Secret': env.CRON_SECRET }
      });
    }
  }
}
```

### Option 2: External Cron Service

Use a free service like [cron-job.org](https://cron-job.org):
- URL: `https://your-backend.onrender.com/api/cron/escalate`
- Header: `X-Cron-Secret: your-secret`
- Schedule: Daily at 2 AM

---

## 📁 File Uploads

Currently, file uploads are stored on the Render server filesystem. For production:

### Option 1: Cloudflare R2 (Recommended)
- Create an R2 bucket
- Update backend to use boto3 with R2
- Free tier: 10GB storage, 10M requests/month

### Option 2: Keep Local
- Files work but are lost on server restart
- Fine for demos, not for production

---

## 🔐 Security Checklist

- [ ] Change admin password after first login
- [ ] Use strong, unique values for SECRET_KEY and JWT_SECRET_KEY
- [ ] Set specific CORS_ORIGINS (not *)
- [ ] Use HTTPS everywhere
- [ ] Set a secure CRON_SECRET

---

## 🐛 Troubleshooting

### "CORS Error" in browser
- Check CORS_ORIGINS includes your Cloudflare Pages URL
- Make sure there's no trailing slash

### "502 Bad Gateway" on Render
- Check build logs for errors
- Verify DATABASE_URL is set
- Run `python init_production_db.py` in shell

### "Network Error" in frontend
- Verify VITE_API_URL is correct
- Redeploy frontend after changing env vars
- Check backend health: `https://your-backend.onrender.com/api/health`

### Render server sleeping (free tier)
- Free tier servers sleep after 15 mins of inactivity
- First request takes ~30s to wake up
- Consider upgrading or using an uptime service

---

## 📊 Free Tier Limits

### Cloudflare Pages
- Unlimited sites
- 500 builds/month
- 100,000 requests/day

### Render.com
- 750 hours/month (enough for one always-on service)
- Server sleeps after 15 mins inactivity
- PostgreSQL: 1GB, expires after 90 days (recreate)

---

## 🎉 You're Live!

Your Padosi Politics app should now be accessible at:
- **Frontend**: `https://padosi-politics.pages.dev`
- **Backend API**: `https://padosi-politics-api.onrender.com/api`

Test credentials (change in production!):
- Admin: `admin@padosipolitics.com` / `AdminPassword123!`
