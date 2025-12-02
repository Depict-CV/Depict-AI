# Quick test script for OAuth2 setup (PowerShell version)

Write-Host "🔍 Checking OAuth2 Setup..." -ForegroundColor Cyan
Write-Host ""

# Check if .env has OAuth credentials configured
Write-Host "1. Checking .env configuration..." -ForegroundColor Yellow

$envContent = Get-Content .env -Raw

if ($envContent -match "YOUR_GOOGLE_CLIENT_ID") {
    Write-Host "   ⚠️  Google credentials not configured yet" -ForegroundColor Yellow
} else {
    Write-Host "   ✅ Google credentials configured" -ForegroundColor Green
}

if ($envContent -match "YOUR_MICROSOFT_CLIENT_ID") {
    Write-Host "   ⚠️  Microsoft credentials not configured yet" -ForegroundColor Yellow
} else {
    Write-Host "   ✅ Microsoft credentials configured" -ForegroundColor Green
}

if ($envContent -match "YOUR_FACEBOOK_APP_ID") {
    Write-Host "   ⚠️  Facebook credentials not configured yet" -ForegroundColor Yellow
} else {
    Write-Host "   ✅ Facebook credentials configured" -ForegroundColor Green
}

Write-Host ""
Write-Host "2. Checking Python dependencies..." -ForegroundColor Yellow

# Check if httpx is installed
try {
    python -c "import httpx" 2>$null
    Write-Host "   ✅ httpx installed" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  httpx not installed - Run: pip install httpx" -ForegroundColor Yellow
}

# Check if python-jose is installed
try {
    python -c "import jose" 2>$null
    Write-Host "   ✅ python-jose installed" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  python-jose not installed - Run: pip install python-jose[cryptography]" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "3. Testing OAuth2 endpoints..." -ForegroundColor Yellow

# Check if FastAPI server is running
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/" -TimeoutSec 2 -ErrorAction Stop
    Write-Host "   ✅ Backend server is running" -ForegroundColor Green
    
    # Check OAuth endpoints
    try {
        $oauthResponse = Invoke-WebRequest -Uri "http://localhost:8000/auth/google/login" -TimeoutSec 2 -MaximumRedirection 0 -ErrorAction Stop
        Write-Host "   ✅ Google OAuth endpoint accessible" -ForegroundColor Green
    } catch {
        if ($_.Exception.Response.StatusCode -eq 302) {
            Write-Host "   ✅ Google OAuth endpoint accessible (redirecting)" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️  Google OAuth endpoint not accessible" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "   ⚠️  Backend server not running - Start with: uvicorn src.backend.endpoints:app --reload" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "4. Testing frontend..." -ForegroundColor Yellow

# Check if frontend is running
try {
    $frontendResponse = Invoke-WebRequest -Uri "http://localhost:5173/" -TimeoutSec 2 -ErrorAction Stop
    Write-Host "   ✅ Frontend server is running" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  Frontend server not running - Start with: cd src/frontend_vue; npm run dev" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📋 Summary:" -ForegroundColor Cyan
Write-Host ""
Write-Host "To complete OAuth2 setup:"
Write-Host "1. Get credentials from provider consoles (see docs/oauth2_setup.md)"
Write-Host "2. Update .env with real credentials"
Write-Host "3. Install dependencies: pip install httpx python-jose[cryptography]"
Write-Host "4. Restart backend: uvicorn src.backend.endpoints:app --reload"
Write-Host "5. Test login at: http://localhost:5173"
Write-Host ""
Write-Host "For detailed instructions, see: docs/oauth2_setup.md" -ForegroundColor Green
