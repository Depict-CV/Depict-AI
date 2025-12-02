# OAuth2 Social Login Setup Guide

This guide will help you set up OAuth2 social login with Google, Microsoft, and Facebook for your Depict AI application.

## Overview

The application now supports three OAuth2 providers:
- **Google** - Sign in with Google
- **Microsoft** - Sign in with Microsoft/Outlook
- **Facebook** - Sign in with Facebook

## Prerequisites

Before setting up OAuth2, you need to:
1. Install required Python dependencies: `httpx`, `python-jose[cryptography]`, `python-dotenv`
2. Update your database schema to support OAuth users (migration will be automatic)

## Setup Instructions

### 1. Google OAuth2 Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google+ API" and enable it
4. Create OAuth2 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Application type: "Web application"
   - Name: "Depict AI"
   - Authorized redirect URIs: `http://localhost:8000/auth/google/callback`
   - For production, add: `https://yourdomain.com/auth/google/callback`
5. Copy the **Client ID** and **Client Secret**
6. Update `.env` file:
   ```env
   GOOGLE_CLIENT_ID="your-google-client-id"
   GOOGLE_CLIENT_SECRET="your-google-client-secret"
   GOOGLE_REDIRECT_URI="http://localhost:8000/auth/google/callback"
   ```

### 2. Microsoft OAuth2 Setup

1. Go to [Azure Portal](https://portal.azure.com/)
2. Navigate to "Azure Active Directory" > "App registrations"
3. Click "New registration":
   - Name: "Depict AI"
   - Supported account types: "Accounts in any organizational directory and personal Microsoft accounts"
   - Redirect URI: 
     - Platform: "Web"
     - URI: `http://localhost:8000/auth/microsoft/callback`
4. After creation, note the **Application (client) ID**
5. Go to "Certificates & secrets":
   - Click "New client secret"
   - Description: "Depict AI Secret"
   - Expires: Choose appropriate duration
   - Copy the **Value** (this is your client secret)
6. Go to "API permissions":
   - Click "Add a permission" > "Microsoft Graph" > "Delegated permissions"
   - Add: `openid`, `email`, `profile`
   - Click "Grant admin consent"
7. Update `.env` file:
   ```env
   MICROSOFT_CLIENT_ID="your-microsoft-client-id"
   MICROSOFT_CLIENT_SECRET="your-microsoft-client-secret"
   MICROSOFT_REDIRECT_URI="http://localhost:8000/auth/microsoft/callback"
   ```

### 3. Facebook OAuth2 Setup

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create a new app:
   - Click "My Apps" > "Create App"
   - Use case: "Authenticate and request data from users with Facebook Login"
   - App name: "Depict AI"
   - Contact email: Your email
3. In the app dashboard:
   - Go to "Settings" > "Basic"
   - Copy the **App ID** and **App Secret**
4. Set up Facebook Login:
   - In left sidebar, click "Products" > "Facebook Login" > "Settings"
   - Valid OAuth Redirect URIs: `http://localhost:8000/auth/facebook/callback`
   - For production, add: `https://yourdomain.com/auth/facebook/callback`
5. Update `.env` file:
   ```env
   FACEBOOK_CLIENT_ID="your-facebook-app-id"
   FACEBOOK_CLIENT_SECRET="your-facebook-app-secret"
   FACEBOOK_REDIRECT_URI="http://localhost:8000/auth/facebook/callback"
   ```

### 4. Update Frontend URL (Optional)

If your frontend runs on a different port or domain:

```env
FRONTEND_URL="http://localhost:5173"  # Default
# For production:
# FRONTEND_URL="https://yourdomain.com"
```

## Testing OAuth2 Login

1. Install dependencies:
   ```bash
   pip install httpx python-jose[cryptography] python-dotenv
   ```

2. Restart your FastAPI server:
   ```bash
   uvicorn src.backend.endpoints:app --reload
   ```

3. Start your frontend:
   ```bash
   cd src/frontend_vue
   npm run dev
   ```

4. Open the login page and click on any OAuth2 button (Google, Microsoft, or Facebook)

5. You'll be redirected to the provider's login page

6. After successful authentication, you'll be redirected back to your app and automatically logged in

## How It Works

### Backend Flow:
1. User clicks "Continue with Google/Microsoft/Facebook"
2. Frontend redirects to `/auth/{provider}/login`
3. Backend redirects to provider's OAuth2 authorization page
4. User logs in at provider's site
5. Provider redirects to `/auth/{provider}/callback` with authorization code
6. Backend exchanges code for access token
7. Backend fetches user info from provider's API
8. Backend creates or finds user in database
9. Backend generates JWT token
10. Backend redirects to frontend with JWT token in URL
11. Frontend stores token and fetches user info

### Database Schema:
The `User` table now includes:
- `oauth_provider`: String ("google", "microsoft", "facebook", or NULL for local users)
- `oauth_id`: Provider's unique user ID
- `hashed_password`: Empty string for OAuth users

OAuth users can log in without a password. Local users can still use email/password authentication.

## Security Considerations

### Production Deployment:

1. **Use HTTPS**: All OAuth2 providers require HTTPS in production
2. **Update Redirect URIs**: Add production URLs to provider configurations
3. **Secure Secrets**: Never commit `.env` file. Use environment variables or secret managers
4. **CORS**: Update CORS settings in `endpoints.py` to only allow your frontend domain
5. **State Parameter**: The implementation uses a state parameter to prevent CSRF attacks

### Environment Variables:

Never commit these values to version control:
- Client IDs are public but should be kept in `.env`
- Client Secrets are sensitive and must never be exposed
- Use different credentials for development and production

## Troubleshooting

### "Invalid redirect URI" error:
- Ensure the redirect URI in your `.env` matches exactly what's configured in the provider console
- Check for trailing slashes - some providers are strict about this

### "Failed to get access token":
- Verify your client ID and secret are correct
- Check that your OAuth2 app is published/enabled in the provider console

### User data not displaying:
- Check browser console for errors
- Verify the `/me` endpoint is working with the JWT token
- Ensure CORS is configured correctly

### Database errors:
- Run database migrations to add `oauth_provider` and `oauth_id` columns
- If using SQLite, restart the app to apply schema changes

## API Endpoints

### OAuth2 Login Endpoints:
- `GET /auth/google/login` - Initiate Google login
- `GET /auth/microsoft/login` - Initiate Microsoft login
- `GET /auth/facebook/login` - Initiate Facebook login

### OAuth2 Callback Endpoints (used by providers):
- `GET /auth/google/callback` - Google redirect callback
- `GET /auth/microsoft/callback` - Microsoft redirect callback
- `GET /auth/facebook/callback` - Facebook redirect callback

### User Info Endpoint:
- `GET /me` - Get current user info (requires JWT token)

## Additional Resources

- [Google OAuth2 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Microsoft Identity Platform](https://docs.microsoft.com/en-us/azure/active-directory/develop/)
- [Facebook Login Documentation](https://developers.facebook.com/docs/facebook-login)
