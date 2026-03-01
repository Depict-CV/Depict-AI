"""
Clerk JWT authentication for FastAPI.
Validates Clerk-issued JWTs and maps to local User model.
"""

import sys
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import httpx  # noqa: E402
from fastapi import Depends, HTTPException, status  # noqa: E402
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer  # noqa: E402
from jose import JWTError, jwt  # noqa: E402
from sqlmodel import Session, select  # noqa: E402

import config  # noqa: E402
from src.backend.db.database import engine  # noqa: E402
from src.backend.db.tables import PermissionEnum, User  # noqa: E402

bearer_scheme = HTTPBearer(auto_error=False)


def get_session():
    """Dependency that yields a SQLModel Session."""
    with Session(engine) as session:
        yield session


@lru_cache(maxsize=1)
def get_jwks() -> Dict[str, Any]:
    """
    Fetch Clerk's JWKS (JSON Web Key Set) for token validation.
    Cached to avoid repeated API calls.
    """
    if not config.config.CLERK_JWKS_URL:
        raise ValueError("CLERK_JWKS_URL not configured")

    try:
        resp = httpx.get(config.config.CLERK_JWKS_URL, timeout=10.0)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Failed to fetch JWKS: {str(e)}")


def get_signing_key(token: str) -> Optional[Dict[str, Any]]:
    """
    Extract the signing key from JWKS based on the token's kid (key ID).
    """
    try:
        jwks = get_jwks()
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")

        if not kid:
            return None

        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                return key

        return None
    except Exception:
        return None


async def get_current_clerk_user(
    session: Session = Depends(get_session),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> User:
    """
    FastAPI dependency that validates Clerk JWT and returns the authenticated User.

    - Validates JWT signature using Clerk's public keys (JWKS)
    - Extracts user info from token (sub, email)
    - Creates or retrieves User from database
    - Maps Clerk user to local User model with oauth_provider='clerk'

    If AUTH_ENABLED=false in config, returns a local dev user without token validation.
    """

    if not config.config.AUTH_ENABLED:
        username = "local-dev-user"
        email = "local-dev-user@local.dev"
        statement = select(User).where(User.username == username)
        user = session.exec(statement).first()

        if not user:
            user = User(
                username=username,
                email=email,
                permission=PermissionEnum.CAN_CERTIFY,
                oauth_provider="local",
                oauth_id="local-dev-user",
            )
            session.add(user)
            session.commit()
            session.refresh(user)

        return user

    # Check if credentials were provided
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials

    # Get signing key from JWKS
    signing_key = get_signing_key(token)
    if not signing_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: signing key not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # Decode and validate JWT
        payload = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],  # Clerk uses RS256
            issuer=config.config.CLERK_ISSUER,
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_iss": True,
            },
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract user info from token
    clerk_user_id = payload.get("sub")
    email = payload.get("email") or payload.get("email_address") or payload.get("primary_email_address")
    username = payload.get("username") or email.split("@")[0] if email else clerk_user_id

    if not clerk_user_id:
        raise credentials_exception

    # Find or create user in database
    statement = select(User).where(User.oauth_provider == "clerk", User.oauth_id == clerk_user_id)
    user = session.exec(statement).first()

    if not user:
        # Create new user from Clerk data
        # Check if username/email already exist (edge case)
        existing_username = session.exec(select(User).where(User.username == username)).first()
        if existing_username:
            username = f"{username}_{clerk_user_id[:8]}"

        existing_email = session.exec(
            select(User).where(User.email == (email or f"{clerk_user_id}@clerk.local"))
        ).first()
        if existing_email:
            email = f"{clerk_user_id}@clerk.local"

        user = User(
            username=username,
            email=email or f"{clerk_user_id}@clerk.local",
            hashed_password=None,  # Not used for OAuth users
            permission=PermissionEnum.VIEW_ONLY,  # Default permission
            oauth_provider="clerk",
            oauth_id=clerk_user_id,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
    else:
        # Update existing user's email/username if changed in Clerk
        updated = False
        if email and user.email != email:
            user.email = email
            updated = True
        if username and user.username != username:
            # Check username isn't taken by another user
            existing = session.exec(select(User).where(User.username == username, User.id != user.id)).first()
            if not existing:
                user.username = username
                updated = True

        if updated:
            session.add(user)
            session.commit()
            session.refresh(user)

    return user


# Backward compatibility: alias for existing code
get_current_user = get_current_clerk_user
