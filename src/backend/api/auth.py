from fastapi import APIRouter, Body, Depends, HTTPException
from sqlmodel import Session, select

from src.backend.api.deps import get_session
from src.backend.db.tables import PermissionEnum, User

router = APIRouter(tags=["users"])  # keep tag 'users' for login


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
#    read     #
###############
@router.post("/login")
def login(data: dict = Body(...), db: Session = Depends(get_session)):
    statement = select(User).where(User.username == data["username"])
    user = db.exec(statement).first()
    if user and user.hashed_password == data.get("hashed_password"):
        return {"message": "Login successful", "user_id": user.id}
    raise HTTPException(status_code=401, detail="Invalid username or password")
