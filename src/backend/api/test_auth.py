"""
Test endpoints for Clerk authentication and user management.
These endpoints help verify that Clerk auth is working correctly.
"""

from typing import Any, Dict

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from src.backend.api.clerk_auth import get_current_clerk_user, get_session
from src.backend.db.tables import Annotation, Data, Project, User

router = APIRouter(prefix="/test", tags=["testing"])


@router.get("/whoami")
def who_am_i(current_user: User = Depends(get_current_clerk_user)) -> Dict[str, Any]:
    """
    Test endpoint to verify Clerk authentication is working.
    Returns information about the currently authenticated user.
    """
    return {
        "authenticated": True,
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "permission": current_user.permission,
            "oauth_provider": current_user.oauth_provider,
            "oauth_id": current_user.oauth_id,
        },
        "message": f"Hello {current_user.username}! You are authenticated via {current_user.oauth_provider}.",
    }


@router.get("/my-stats")
def get_my_stats(
    current_user: User = Depends(get_current_clerk_user), db: Session = Depends(get_session)
) -> Dict[str, Any]:
    """
    Get statistics about the current user's content.
    Shows how user-specific filtering works.
    """

    # Count projects where user is a member
    from src.backend.db.tables import ProjectUserLink

    projects_statement = select(Project).join(ProjectUserLink).where(ProjectUserLink.user_id == current_user.id)
    projects = db.exec(projects_statement).all()

    # Count annotations by this user
    annotations_statement = select(Annotation).where(Annotation.author_id == current_user.id)
    annotations = db.exec(annotations_statement).all()

    # Count data uploaded by this user
    data_statement = select(Data).where(Data.author_id == current_user.id)
    data_items = db.exec(data_statement).all()

    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "stats": {
            "projects": len(projects),
            "annotations": len(annotations),
            "data_uploads": len(data_items),
        },
        "details": {
            "project_names": [p.name for p in projects],
            "recent_annotations": [
                {"id": a.id, "label": a.label, "status": a.status}
                for a in annotations[:5]  # Show first 5
            ],
        },
    }


@router.get("/all-users")
def list_all_users(
    db: Session = Depends(get_session), current_user: User = Depends(get_current_clerk_user)
) -> Dict[str, Any]:
    """
    List all users in the database (for debugging).
    In production, you might want to restrict this to admins only.
    """
    users = db.exec(select(User)).all()

    return {
        "total_users": len(users),
        "users": [
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "oauth_provider": u.oauth_provider or "local (password)",
                "has_password": bool(u.hashed_password),
            }
            for u in users
        ],
        "current_user_id": current_user.id,
    }
