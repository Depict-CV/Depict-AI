from fastapi import APIRouter, Body, Depends, HTTPException
from sqlmodel import Session, select

from backend.api.deps import get_session
from backend.db.tables import User

router = APIRouter(tags=["users"])  # keep tag 'users' for login


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
