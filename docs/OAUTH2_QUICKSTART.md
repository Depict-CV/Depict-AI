# OAuth2 Social Login - Quick Start

## ✅ What's Been Added

I've successfully added OAuth2 social login to your application with support for:
- 🔵 **Google** - Sign in with Google
- 🟦 **Microsoft** - Sign in with Microsoft/Outlook  
- 🔷 **Facebook** - Sign in with Facebook

## 📁 Files Modified/Created

### Frontend Changes:
- ✅ `LoginPage.vue` - Added OAuth2 social login buttons with branded styling
- ✅ `App.vue` - Added OAuth token handling from URL redirects

### Backend Changes:
- ✅ `api/oauth2.py` - **NEW** - Complete OAuth2 implementation for all 3 providers
- ✅ `db/tables.py` - Added `oauth_provider` and `oauth_id` fields to User table
- ✅ `endpoints.py` - Registered OAuth2 router
- ✅ `config.py` - Added OAuth2 configuration variables

### Configuration:
- ✅ `.env` - Added OAuth2 credentials placeholders
- ✅ `pyproject.toml` - Added httpx dependency
- ✅ `docs/oauth2_setup.md` - **NEW** - Complete setup guide

## 🚀 Next Steps

### 1. Install Required Packages

```bash
pip install httpx
```

### 2. Set Up OAuth2 Providers

You need to get credentials from each provider you want to use:

#### Google (Recommended to start with):
1. Go to https://console.cloud.google.com/
2. Create a project
3. Enable Google+ API
4. Create OAuth2 credentials
5. Set redirect URI: `http://localhost:8000/auth/google/callback`
6. Copy Client ID and Secret to `.env`

#### Microsoft:
1. Go to https://portal.azure.com/
2. Register an app in Azure AD
3. Set redirect URI: `http://localhost:8000/auth/microsoft/callback`
4. Copy Application ID and Secret to `.env`

#### Facebook:
1. Go to https://developers.facebook.com/
2. Create a new app
3. Add Facebook Login product
4. Set redirect URI: `http://localhost:8000/auth/facebook/callback`
5. Copy App ID and Secret to `.env`

**See `docs/oauth2_setup.md` for detailed step-by-step instructions!**

### 3. Update .env File

Replace the placeholder values in `.env`:

```env
# Google
GOOGLE_CLIENT_ID="your-actual-google-client-id"
GOOGLE_CLIENT_SECRET="your-actual-google-client-secret"

# Microsoft
MICROSOFT_CLIENT_ID="your-actual-microsoft-client-id"
MICROSOFT_CLIENT_SECRET="your-actual-microsoft-client-secret"

# Facebook
FACEBOOK_CLIENT_ID="your-actual-facebook-app-id"
FACEBOOK_CLIENT_SECRET="your-actual-facebook-app-secret"
```

### 4. Restart Your Servers

```bash
# Backend
uvicorn src.backend.endpoints:app --reload

# Frontend (in another terminal)
cd src/frontend_vue
npm run dev
```

### 5. Test It Out!

1. Go to the login page
2. You'll see three new buttons below the regular login form:
   - "Continue with Google"
   - "Continue with Microsoft"
   - "Continue with Facebook"
3. Click any button to test (only works if you've set up that provider's credentials)

## 🎨 What You'll See

The login page now has:
- A divider with "OR" separating traditional login from social login
- Three branded buttons with official colors and logos
- Smooth hover effects
- Loading states during authentication

## 🔐 How It Works

1. User clicks a social login button
2. User is redirected to provider's login page (Google/Microsoft/Facebook)
3. User authenticates with their account
4. Provider redirects back to your app with authorization code
5. Backend exchanges code for user info
6. Backend creates/finds user in database
7. Backend generates JWT token
8. User is automatically logged in!

## 🛡️ Security Features

- ✅ OAuth2 state parameter to prevent CSRF attacks
- ✅ JWT tokens for session management
- ✅ Separate storage for OAuth vs local users
- ✅ Secure token exchange flow

## ⚠️ Important Notes

- **OAuth buttons will show errors until you configure credentials** - This is normal!
- Start with Google as it's the easiest to set up
- Each provider requires separate registration and configuration
- For production, you'll need HTTPS and updated redirect URIs
- The regular email/password login still works normally

## 📚 Need Help?

Read the full setup guide: `docs/oauth2_setup.md`

It includes:
- Detailed setup instructions for each provider
- Screenshots and step-by-step guides
- Troubleshooting common issues
- Security best practices
- Production deployment notes

## 🎯 Testing Without OAuth Setup

If you don't want to set up OAuth providers right now:
- The regular email/password login still works perfectly
- The OAuth buttons are visible but will redirect to placeholder endpoints
- You can hide the OAuth section by commenting out the "social-login" div in LoginPage.vue

Enjoy your new social login feature! 🎉
