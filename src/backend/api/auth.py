from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from datetime import datetime, timedelta
from jose import jwt
from pydantic import BaseModel

from src.backend.api.deps import get_session, get_current_user
from src.backend.db.tables import PermissionEnum, User
import config

router = APIRouter(tags=["users"])


# Response models
class Token(BaseModel):
    access_token: str
    token_type: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    permission: PermissionEnum


def create_access_token(user_id: int, expires_delta: timedelta = None):
    """Create JWT access token"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=config.config.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"sub": str(user_id), "exp": expire}
    encoded_jwt = jwt.encode(to_encode, config.config.JWT_SECRET_KEY, algorithm=config.config.JWT_ALGORITHM)
    return encoded_jwt


###############
#    create   #
###############
@router.post("/signup")
def signup(data: dict = Body(...), db: Session = Depends(get_session)):
    # Check if username already exists
    statement = select(User).where(User.username == data["username"])
    existing_user = db.exec(statement).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Check if email already exists
    statement = select(User).where(User.email == data["email"])
    existing_email = db.exec(statement).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    # Create new user
    new_user = User(
        username=data["username"],
        email=data["email"],
        hashed_password=data["hashed_password"],
        permission=data.get("permission", PermissionEnum.VIEW_ONLY)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "Signup successful", "user_id": new_user.id}


###############
#    OAuth2    #
###############
@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_session)
):
    """
    OAuth2 compatible token login endpoint.
    Use username and password from OAuth2PasswordRequestForm.
    """
    statement = select(User).where(User.username == form_data.username)
    user = db.exec(statement).first()
    
    if not user or user.hashed_password != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(user.id)
    return {"access_token": access_token, "token_type": "bearer"}


###############
#    read     #
###############
@router.post("/login")
def login(data: dict = Body(...), db: Session = Depends(get_session)):
    """Legacy login endpoint for existing frontend (accepts JSON with hashed password)"""
    statement = select(User).where(User.username == data["username"])
    user = db.exec(statement).first()
    if user and user.hashed_password == data.get("hashed_password"):
        # Create JWT token
        access_token = create_access_token(user.id)
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user.id,
            "username": user.username
        }
    raise HTTPException(status_code=401, detail="Invalid username or password")


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current authenticated user information (protected route)"""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        permission=current_user.permission
    )
