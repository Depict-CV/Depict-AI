"""
OAuth2 Social Login Providers (Google, Microsoft, GitHub)
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select
from typing import Optional
import httpx
from datetime import timedelta
import secrets

from ..db.tables import User
from .auth import create_access_token
from .deps import get_session
from config import (
    GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI,
    MICROSOFT_CLIENT_ID, MICROSOFT_CLIENT_SECRET, MICROSOFT_REDIRECT_URI,
    GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET, GITHUB_REDIRECT_URI,
    FRONTEND_URL
)

router = APIRouter(prefix="/auth", tags=["oauth2"])

# Temporary storage for OAuth state (in production, use Redis or database)
oauth_states = {}


# ==================== GOOGLE OAUTH2 ====================

@router.get("/google/login")
async def google_login():
    """Redirect user to Google OAuth2 login page"""
    state = secrets.token_urlsafe(32)
    oauth_states[state] = "google"
    
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={GOOGLE_CLIENT_ID}&"
        f"redirect_uri={GOOGLE_REDIRECT_URI}&"
        f"response_type=code&"
        f"scope=openid email profile&"
        f"state={state}"
    )
    
    return RedirectResponse(google_auth_url)


@router.get("/google/callback")
async def google_callback(code: str, state: str, session: Session = Depends(get_session)):
    """Handle Google OAuth2 callback and create/login user"""
    # Verify state
    if state not in oauth_states or oauth_states[state] != "google":
        raise HTTPException(status_code=400, detail="Invalid state parameter")
    
    # Remove used state
    del oauth_states[state]
    
    # Exchange code for token
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code"
            }
        )
        
        if token_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get access token")
        
        token_data = token_response.json()
        access_token = token_data["access_token"]
        
        # Get user info from Google
        user_response = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if user_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get user info")
        
        user_info = user_response.json()
    
    # Find or create user
    user = await get_or_create_oauth_user(
        session=session,
        email=user_info["email"],
        username=user_info.get("name", user_info["email"].split("@")[0]),
        oauth_provider="google",
        oauth_id=user_info["id"]
    )
    
    # Create JWT token
    jwt_token = create_access_token(data={"sub": user.email})
    
    # Redirect to frontend with token
    return RedirectResponse(f"{FRONTEND_URL}?token={jwt_token}")


# ==================== MICROSOFT OAUTH2 ====================

@router.get("/microsoft/login")
async def microsoft_login():
    """Redirect user to Microsoft OAuth2 login page"""
    state = secrets.token_urlsafe(32)
    oauth_states[state] = "microsoft"
    
    microsoft_auth_url = (
        f"https://login.microsoftonline.com/common/oauth2/v2.0/authorize?"
        f"client_id={MICROSOFT_CLIENT_ID}&"
        f"redirect_uri={MICROSOFT_REDIRECT_URI}&"
        f"response_type=code&"
        f"scope=openid email profile&"
        f"state={state}"
    )
    
    return RedirectResponse(microsoft_auth_url)


@router.get("/microsoft/callback")
async def microsoft_callback(code: str, state: str, session: Session = Depends(get_session)):
    """Handle Microsoft OAuth2 callback and create/login user"""
    # Verify state
    if state not in oauth_states or oauth_states[state] != "microsoft":
        raise HTTPException(status_code=400, detail="Invalid state parameter")
    
    # Remove used state
    del oauth_states[state]
    
    # Exchange code for token
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://login.microsoftonline.com/common/oauth2/v2.0/token",
            data={
                "code": code,
                "client_id": MICROSOFT_CLIENT_ID,
                "client_secret": MICROSOFT_CLIENT_SECRET,
                "redirect_uri": MICROSOFT_REDIRECT_URI,
                "grant_type": "authorization_code"
            }
        )
        
        if token_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get access token")
        
        token_data = token_response.json()
        access_token = token_data["access_token"]
        
        # Get user info from Microsoft
        user_response = await client.get(
            "https://graph.microsoft.com/v1.0/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if user_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get user info")
        
        user_info = user_response.json()
    
    # Find or create user
    user = await get_or_create_oauth_user(
        session=session,
        email=user_info["mail"] or user_info["userPrincipalName"],
        username=user_info.get("displayName", user_info["mail"].split("@")[0]),
        oauth_provider="microsoft",
        oauth_id=user_info["id"]
    )
    
    # Create JWT token
    jwt_token = create_access_token(data={"sub": user.email})
    
    # Redirect to frontend with token
    return RedirectResponse(f"{FRONTEND_URL}?token={jwt_token}")


# ==================== GITHUB OAUTH2 ====================

@router.get("/github/login")
async def github_login():
    """Redirect user to GitHub OAuth2 login page"""
    state = secrets.token_urlsafe(32)
    oauth_states[state] = "github"
    
    github_auth_url = (
        f"https://github.com/login/oauth/authorize?"
        f"client_id={GITHUB_CLIENT_ID}&"
        f"redirect_uri={GITHUB_REDIRECT_URI}&"
        f"state={state}&"
        f"scope=user:email"
    )
    
    return RedirectResponse(github_auth_url)


@router.get("/github/callback")
async def github_callback(code: str, state: str, session: Session = Depends(get_session)):
    """Handle GitHub OAuth2 callback and create/login user"""
    # Verify state
    if state not in oauth_states or oauth_states[state] != "github":
        raise HTTPException(status_code=400, detail="Invalid state parameter")
    
    # Remove used state
    del oauth_states[state]
    
    # Exchange code for token
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "code": code,
                "client_id": GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "redirect_uri": GITHUB_REDIRECT_URI
            }
        )
        
        if token_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get access token")
        
        token_data = token_response.json()
        access_token = token_data.get("access_token")
        
        if not access_token:
            raise HTTPException(status_code=400, detail="No access token received")
        
        # Get user info from GitHub
        user_response = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if user_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get user info")
        
        user_info = user_response.json()
        
        # Get user email if not public
        email = user_info.get("email")
        if not email:
            emails_response = await client.get(
                "https://api.github.com/user/emails",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            if emails_response.status_code == 200:
                emails = emails_response.json()
                primary_email = next((e for e in emails if e.get("primary")), None)
                if primary_email:
                    email = primary_email.get("email")
    
    # Find or create user
    user = await get_or_create_oauth_user(
        session=session,
        email=email,
        username=user_info.get("login", f"github_{user_info['id']}"),
        oauth_provider="github",
        oauth_id=str(user_info["id"])
    )
    
    # Create JWT token
    jwt_token = create_access_token(data={"sub": user.email})
    
    # Redirect to frontend with token
    return RedirectResponse(f"{FRONTEND_URL}?token={jwt_token}")


# ==================== HELPER FUNCTIONS ====================

async def get_or_create_oauth_user(
    session: Session,
    email: Optional[str],
    username: str,
    oauth_provider: str,
    oauth_id: str
) -> User:
    """Find existing user by email or create new OAuth user"""
    
    # Try to find user by email first
    if email:
        statement = select(User).where(User.email == email)
        user = session.exec(statement).first()
        
        if user:
            # Update OAuth info if not set
            if not user.oauth_provider:
                user.oauth_provider = oauth_provider
                user.oauth_id = oauth_id
                session.add(user)
                session.commit()
                session.refresh(user)
            return user
    
    # Try to find by OAuth provider + ID
    statement = select(User).where(
        User.oauth_provider == oauth_provider,
        User.oauth_id == oauth_id
    )
    user = session.exec(statement).first()
    
    if user:
        return user
    
    # Create new user
    new_user = User(
        username=username,
        email=email,
        oauth_provider=oauth_provider,
        oauth_id=oauth_id,
        hashed_password="",  # OAuth users don't have passwords
        permission="editor"  # Default permission for OAuth users
    )
    
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    
    return new_user
