<# 
Padosi Politics - Complete Deployment Script
Run this after setting up PythonAnywhere backend

Prerequisites:
1. PythonAnywhere account with backend deployed
2. Wrangler CLI logged in (wrangler login)
3. Update PA_USERNAME below
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$PA_USERNAME,
    
    [Parameter(Mandatory=$false)]
    [string]$CRON_SECRET = "padosi-cron-$(Get-Random -Maximum 999999)"
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 Padosi Politics - Full Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$BACKEND_URL = "https://$PA_USERNAME.pythonanywhere.com"
$FRONTEND_URL = "https://padosi-politics.pages.dev"

Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  Frontend: $FRONTEND_URL"
Write-Host "  Backend:  $BACKEND_URL"
Write-Host "  Cron Secret: $CRON_SECRET"
Write-Host ""

# Step 1: Update frontend .env.production
Write-Host "📝 Step 1: Updating frontend configuration..." -ForegroundColor Green
$envContent = @"
# Padosi Politics - Production Environment
# Frontend: Cloudflare Pages
# Backend: PythonAnywhere

# API URL - PythonAnywhere backend
VITE_API_URL=$BACKEND_URL/api
"@
Set-Content -Path ".\frontend\.env.production" -Value $envContent
Write-Host "   ✅ .env.production updated"

# Step 2: Build frontend
Write-Host ""
Write-Host "📦 Step 2: Building frontend..." -ForegroundColor Green
Push-Location .\frontend
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ❌ Build failed!" -ForegroundColor Red
    Pop-Location
    exit 1
}
Write-Host "   ✅ Frontend built successfully"
Pop-Location

# Step 3: Deploy frontend to Cloudflare Pages
Write-Host ""
Write-Host "☁️ Step 3: Deploying frontend to Cloudflare Pages..." -ForegroundColor Green
Push-Location .\frontend
npx wrangler pages deploy dist --project-name=padosi-politics
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ❌ Deployment failed!" -ForegroundColor Red
    Pop-Location
    exit 1
}
Write-Host "   ✅ Frontend deployed to $FRONTEND_URL"
Pop-Location

# Step 4: Deploy Cron Worker
Write-Host ""
Write-Host "⏰ Step 4: Deploying Cron Worker..." -ForegroundColor Green
Push-Location .\cloudflare-worker

# Deploy worker
npx wrangler deploy
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ⚠️ Worker deployment may have issues" -ForegroundColor Yellow
}

# Set secrets
Write-Host "   Setting worker secrets..."
Write-Host $BACKEND_URL | npx wrangler secret put BACKEND_URL
Write-Host $CRON_SECRET | npx wrangler secret put CRON_SECRET

Write-Host "   ✅ Cron worker deployed"
Pop-Location

# Step 5: Display summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🌐 Your app is live at:" -ForegroundColor Yellow
Write-Host "   Frontend: $FRONTEND_URL"
Write-Host "   Backend:  $BACKEND_URL"
Write-Host "   API:      $BACKEND_URL/api"
Write-Host ""
Write-Host "⏰ Cron Jobs:" -ForegroundColor Yellow
Write-Host "   Worker: padosi-politics-cron.YOUR_CF_SUBDOMAIN.workers.dev"
Write-Host "   Schedule: 2 AM, 8 AM, 2 PM, 8 PM UTC"
Write-Host ""
Write-Host "🔑 Important - Save this CRON_SECRET:" -ForegroundColor Red
Write-Host "   $CRON_SECRET"
Write-Host ""
Write-Host "📋 Add this to PythonAnywhere .env file:" -ForegroundColor Yellow
Write-Host "   CRON_SECRET=$CRON_SECRET"
Write-Host "   CORS_ORIGINS=$FRONTEND_URL"
Write-Host ""
