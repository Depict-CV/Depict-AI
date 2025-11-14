from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from src.backend.api.deps import get_session
from src.backend.db.tables import Project, User

router = APIRouter(prefix="/users", tags=["users"])


###############
#    create   #
###############
@router.post("/", response_model=User)
def create_user(item: User, db: Session = Depends(get_session)):
    statement = select(User).where(User.username == item.username)
    existing_user = db.exec(statement).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/{user_id}/projects")
def get_user_projects(user_id: int, db: Session = Depends(get_session)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    projects = db.exec(select(Project).where(Project.owner_id == user_id)).all()
    return projects


###############
#    read     #
###############
@router.get("/{user_id}")
def read_user(user_id: int, db: Session = Depends(get_session)):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


###############
#   update    #
###############
@router.put("/{user_id}")
def update_user(user_id: int, updated_user: User, db: Session = Depends(get_session)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # preserve original semantics: commit and refresh
    db.commit()
    db.refresh(updated_user)
    return user


###############
#   delete    #
###############
@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_session)):
    statement = select(User).where(User.id == user_id)
    user = db.exec(statement).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": f"User with id {user_id} deleted"}
