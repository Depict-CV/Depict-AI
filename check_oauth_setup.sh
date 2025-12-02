#!/bin/bash
# Quick test script for OAuth2 setup

echo "🔍 Checking OAuth2 Setup..."
echo ""

# Check if .env has OAuth credentials configured
echo "1. Checking .env configuration..."

if grep -q "YOUR_GOOGLE_CLIENT_ID" .env; then
    echo "   ⚠️  Google credentials not configured yet"
else
    echo "   ✅ Google credentials configured"
fi

if grep -q "YOUR_MICROSOFT_CLIENT_ID" .env; then
    echo "   ⚠️  Microsoft credentials not configured yet"
else
    echo "   ✅ Microsoft credentials configured"
fi

if grep -q "YOUR_FACEBOOK_APP_ID" .env; then
    echo "   ⚠️  Facebook credentials not configured yet"
else
    echo "   ✅ Facebook credentials configured"
fi

echo ""
echo "2. Checking Python dependencies..."

# Check if httpx is installed
if python -c "import httpx" 2>/dev/null; then
    echo "   ✅ httpx installed"
else
    echo "   ⚠️  httpx not installed - Run: pip install httpx"
fi

# Check if python-jose is installed
if python -c "import jose" 2>/dev/null; then
    echo "   ✅ python-jose installed"
else
    echo "   ⚠️  python-jose not installed - Run: pip install python-jose[cryptography]"
fi

echo ""
echo "3. Testing OAuth2 endpoints..."

# Check if FastAPI server is running
if curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo "   ✅ Backend server is running"
    
    # Check OAuth endpoints
    if curl -s http://localhost:8000/auth/google/login > /dev/null 2>&1; then
        echo "   ✅ Google OAuth endpoint accessible"
    else
        echo "   ⚠️  Google OAuth endpoint not accessible"
    fi
else
    echo "   ⚠️  Backend server not running - Start with: uvicorn src.backend.endpoints:app --reload"
fi

echo ""
echo "4. Testing frontend..."

# Check if frontend is running
if curl -s http://localhost:5173/ > /dev/null 2>&1; then
    echo "   ✅ Frontend server is running"
else
    echo "   ⚠️  Frontend server not running - Start with: cd src/frontend_vue && npm run dev"
fi

echo ""
echo "📋 Summary:"
echo ""
echo "To complete OAuth2 setup:"
echo "1. Get credentials from provider consoles (see docs/oauth2_setup.md)"
echo "2. Update .env with real credentials"
echo "3. Install dependencies: pip install httpx python-jose[cryptography]"
echo "4. Restart backend: uvicorn src.backend.endpoints:app --reload"
echo "5. Test login at: http://localhost:5173"
echo ""
echo "For detailed instructions, see: docs/oauth2_setup.md"
