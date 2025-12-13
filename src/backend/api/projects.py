from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, func, select

from src.backend.api.clerk_auth import get_current_clerk_user, get_session
from src.backend.db.tables import Annotation, Data, Project, ProjectUserLink, User

router = APIRouter(prefix="/projects", tags=["projects"])


# Response models
class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    owner_id: Optional[int] = None
    created_at: datetime
    members: int = 0
    images: int = 0
    role: str = "Viewer"

    class Config:
        from_attributes = True


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None


###############
#    create   #
###############
@router.post("/", response_model=ProjectResponse)
def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_clerk_user),
):
    """Create a new project with the current user as owner"""
    project = Project(name=project_data.name, description=project_data.description, owner_id=current_user.id)
    db.add(project)
    db.commit()
    db.refresh(project)

    # Link owner to project in ProjectUserLink
    owner_link = ProjectUserLink(project_id=project.id, user_id=current_user.id)
    db.add(owner_link)

    # Link AI user to project in ProjectUserLink
    statement = select(User).where(User.username == "ai")
    ai_user = db.exec(statement).first()
    if ai_user:
        ai_link = ProjectUserLink(project_id=project.id, user_id=ai_user.id)
        db.add(ai_link)

    db.commit()

    # Build response with member count
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        owner_id=project.owner_id,
        created_at=datetime.now(),
        images=0,
    )


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
@router.get("/my-projects", response_model=list[ProjectResponse])
def get_user_projects(db: Session = Depends(get_session), current_user: User = Depends(get_current_clerk_user)):
    """Get all projects for the current user"""
    # Get all project links for the user
    statement = select(ProjectUserLink).where(ProjectUserLink.user_id == current_user.id)
    user_links = db.exec(statement).all()

    projects_response = []
    for link in user_links:
        project = db.get(Project, link.project_id)
        if not project:
            continue

        # Count members
        member_count_stmt = select(ProjectUserLink).where(ProjectUserLink.project_id == project.id)
        member_count = len(db.exec(member_count_stmt).all())

        # Count images (assuming you have an Image table)
        # TODO: Add actual image count from your Image table
        image_count = 0

        # Determine user role
        role = "Admin" if project.owner_id == current_user.id else "Editor"

        projects_response.append(
            ProjectResponse(
                id=project.id,
                name=project.name,
                description=project.description,
                owner_id=project.owner_id,
                status="active",
                created_at=datetime.now(),
                members=member_count,
                images=image_count,
                role=role,
            )
        )

    return projects_response


@router.get("/all")
def read_all_projects(db: Session = Depends(get_session)):
    """Get all projects with image and annotation counts"""
    from src.backend.db.tables import Annotation, Data

    projects = db.exec(select(Project)).all()
    if not projects:
        return []

    # Enrich projects with counts
    enriched_projects = []
    for project in projects:
        # Count images
        image_count = db.exec(select(Data).where(Data.project_id == project.id)).all()

        # Count annotations
        annotation_count = db.exec(select(Annotation).where(Annotation.project_id == project.id)).all()

        # Count members
        member_count = db.exec(select(ProjectUserLink).where(ProjectUserLink.project_id == project.id)).all()

        # Create enriched project dict
        project_dict = {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "owner_id": project.owner_id,
            "created_at": project.created_at,
            "images": len(image_count),
            "annotations": len(annotation_count),
            "members": len(member_count),
        }
        enriched_projects.append(project_dict)

    return enriched_projects


@router.get("/{project_id}/users")
def get_project_users(project_id: int, db: Session = Depends(get_session)):
    """Get all users connected to a project"""

    # Verify project exists
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Get all user links for this project
    statement = select(ProjectUserLink).where(ProjectUserLink.project_id == project_id)
    links = db.exec(statement).all()

    # Get user details for each link
    users = []
    for link in links:
        user = db.get(User, link.user_id)
        if user:
            users.append({"id": user.id, "name": user.username, "email": user.email, "role": link.role})

    return users


@router.get("/{project_id}/statistics")
def get_project_statistics(project_id: int, db: Session = Depends(get_session)):
    """Get comprehensive statistics for a project using database aggregation"""

    # Verify project exists
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Total images count
    total_images = db.exec(select(func.count(Data.id)).where(Data.project_id == project_id)).one()

    # Total annotations count
    total_annotations = db.exec(select(func.count(Annotation.id)).where(Annotation.project_id == project_id)).one()

    # Annotated images (unique data_ids with annotations)
    annotated_images = db.exec(
        select(func.count(func.distinct(Annotation.data_id))).where(Annotation.project_id == project_id)
    ).one()

    # Annotations by status
    status_results = db.exec(
        select(Annotation.status, func.count(Annotation.id))
        .where(Annotation.project_id == project_id)
        .group_by(Annotation.status)
    ).all()
    by_status = {status: count for status, count in status_results}

    # Annotations by label
    label_results = db.exec(
        select(Annotation.label, func.count(Annotation.id))
        .where(Annotation.project_id == project_id, Annotation.label.isnot(None))
        .group_by(Annotation.label)
    ).all()
    by_label = {label: count for label, count in label_results}

    # Recent activity (last 10 annotations)
    recent_activity = db.exec(
        select(Annotation)
        .where(Annotation.project_id == project_id)
        .order_by(Annotation.creation_date.desc())
        .limit(10)
    ).all()

    # Calculate completion rate
    completion_rate = round((annotated_images / total_images * 100) if total_images > 0 else 0, 2)

    return {
        "total_images": total_images,
        "total_annotations": total_annotations,
        "annotated_images": annotated_images,
        "pending_images": total_images - annotated_images,
        "completion_rate": completion_rate,
        "by_status": by_status,
        "by_label": by_label,
        "recent_activity": [
            {
                "id": ann.id,
                "data_id": ann.data_id,
                "label": ann.label,
                "status": ann.status,
                "annotation_score": ann.annotation_score,
                "creation_date": ann.creation_date.isoformat() if ann.creation_date else None,
                "author_id": ann.author_id,
            }
            for ann in recent_activity
        ],
    }


@router.get("/{project_id}")
def read_project(project_id: int, db: Session = Depends(get_session)):
    """Get a specific project by ID"""
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/join/{project_code}")
def join_project_by_code(
    project_code: str, db: Session = Depends(get_session), current_user: User = Depends(get_current_clerk_user)
):
    """Join a project using a project code/name"""
    statement = select(Project).where(Project.name == project_code)
    project = db.exec(statement).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found with this code")

    # Check if user is already in the project
    link_statement = select(ProjectUserLink).where(
        ProjectUserLink.project_id == project.id, ProjectUserLink.user_id == current_user.id
    )
    existing_link = db.exec(link_statement).first()

    if existing_link:
        raise HTTPException(status_code=400, detail="You are already a member of this project")

    # Add user to project
    link = ProjectUserLink(project_id=project.id, user_id=current_user.id)
    db.add(link)
    db.commit()

    return {"message": "Successfully joined project", "project_id": project.id}


@router.post("/fetch", tags=["projects"])
def get_project_id(data: dict = Body(...), db: Session = Depends(get_session)):
    """Legacy endpoint - get project ID by name"""
    statement = select(Project).where(Project.name == data["project_name"])
    project = db.exec(statement).first()
    if project:
        return {"message": "Project found", "project_id": project.id}
    raise HTTPException(status_code=404, detail="Project not found")


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
