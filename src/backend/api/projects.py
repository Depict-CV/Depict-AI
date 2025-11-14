from fastapi import APIRouter, Body, Depends, HTTPException
from sqlmodel import Session, select

from src.backend.api.deps import get_session
from src.backend.db.tables import Project, ProjectUserLink, User

router = APIRouter(prefix="/projects", tags=["projects"])


###############
#    create   #
###############
@router.post("/")
def create_project(item: Project, db: Session = Depends(get_session)):
    db.add(item)
    db.commit()
    db.refresh(item)
    # Link owner to project in ProjectUserLink
    if item.owner_id:
        owner_link = ProjectUserLink(project_id=item.id, user_id=item.owner_id)
        db.add(owner_link)
    # Link AI user to project in ProjectUserLink
    statement = select(User).where(User.username == "ai")
    ai_user = db.exec(statement).first()
    if ai_user:
        ai_link = ProjectUserLink(project_id=item.id, user_id=ai_user.id)
        db.add(ai_link)
    db.commit()
    return item


@router.post("/{project_id}/users/{user_id}")
def add_user_to_project(project_id: int, user_id: int, db: Session = Depends(get_session), ai: bool = False):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    statement = select(ProjectUserLink).where(
        ProjectUserLink.project_id == project_id, ProjectUserLink.user_id == user_id
    )
    existing_link = db.exec(statement).first()
    if existing_link:
        raise HTTPException(status_code=400, detail="User already in project")

    link = ProjectUserLink(project_id=project_id, user_id=user_id)
    db.add(link)
    if ai:
        statement = select(User).where(User.username == "ai")
        ai_user = db.exec(statement).first()
        if ai_user:
            ai_link = ProjectUserLink(project_id=project_id, user_id=ai_user.id)
            db.add(ai_link)
    db.commit()

    return {"message": f"User {user_id} added to project {project_id}"}


###############
#    read     #
###############
@router.get("/all")
def read_all_projects(db: Session = Depends(get_session)):
    projects = db.exec(select(Project)).all()
    if not projects:
        raise HTTPException(status_code=404, detail="No project found")
    return projects


@router.get("/{project_id}")
def read_project(project_id: int, db: Session = Depends(get_session)):
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/projects/fetch", tags=["projects"])
def get_project_id(data: dict = Body(...), db: Session = Depends(get_session)):
    statement = select(Project).where(Project.name == data["project_name"])
    project = db.exec(statement).first()
    if project:
        return {"message": "Join successful", "project_id": project.id}
    raise HTTPException(status_code=401, detail="Invalid username or password")


###############
#   update    #
###############
@router.put("/{project_id}")
def update_project(project_id: int, updated_project: Project, db: Session = Depends(get_session)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.commit()
    db.refresh(updated_project)
    return project


###############
#   delete    #
###############
@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_session)):
    statement = select(Project).where(Project.id == project_id)
    project = db.exec(statement).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
    return {"message": f"Project with id {project_id} deleted"}
