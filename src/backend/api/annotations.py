from fastapi import APIRouter, Body, Depends, HTTPException
from sqlmodel import Session, select

from src.backend.api.deps import get_session
from src.backend.db.tables import Annotation, Data, Project, User

router = APIRouter(prefix="/annotations", tags=["annotations"])


###############
#    create   #
###############
@router.post("/")
def create_annotation(data: dict = Body(...), db: Session = Depends(get_session)):
    data_id = data.get("data_id")
    user_id = data.get("author_id")
    project_id = data.get("project_id")
    status = data.get("status")
    annotation_score = data.get("annotation_score")
    label = data.get("label")

    # Validate required fields
    if not data_id or not user_id or not project_id:
        raise HTTPException(status_code=400, detail="data_id, author_id, and project_id are required")
    data_obj = db.get(Data, data_id)
    if not data_obj:
        raise HTTPException(status_code=404, detail="Data not found")
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not label:
        raise HTTPException(status_code=400, detail="label is required")
    new_annotation = Annotation(
        data_id=data_id,
        author_id=user_id,
        project_id=project_id,
        status=status,
        annotation_score=annotation_score,
        label=label,
    )
    db.add(new_annotation)
    db.commit()
    db.refresh(new_annotation)
    return new_annotation


###############
#    read     #
###############
@router.get("/{annotation_id}")
def read_annotation(annotation_id: int, db: Session = Depends(get_session)):
    return db.get(Annotation, annotation_id)


@router.post("/score")
def read_annotation_by_score(data: dict = Body(...), db: Session = Depends(get_session)):
    offset = data["offset"]
    limit = data["limit"]
    project_id = data["project_id"]
    filtered_annotations = db.exec(select(Annotation).where(Annotation.project_id == project_id)).all()
    sorted_annotations = sorted(filtered_annotations, key=lambda x: x.annotation_score)
    return sorted_annotations[offset : offset + limit]


@router.post("/filter")
def read_all_annotations_status(data: dict = Body(...), db: Session = Depends(get_session)):
    project_id = data["project_id"]
    status = data["status"]

    statement = select(Annotation).where((Annotation.project_id == project_id) & (Annotation.status == status))
    return db.exec(statement).all()


###############
#   update    #
###############
@router.patch("/")
def update_annotation(data: dict = Body(...), db: Session = Depends(get_session)):
    annotation_id = data["id"]
    if "annotation_score" in data:
        annotation_score = data["annotation_score"]
        annotation = db.get(Annotation, annotation_id)
        if not annotation:
            raise HTTPException(status_code=404, detail="Annotation not found")
        if annotation_score:
            annotation.annotation_score = annotation_score
    if "status" in data:
        new_status = data["status"]
        annotation = db.get(Annotation, annotation_id)
        if not annotation:
            raise HTTPException(status_code=404, detail="Annotation not found")
        annotation.status = new_status
    db.commit()
    db.refresh(annotation)
    return annotation


###############
#   delete    #
###############
@router.delete("/{annotation_id}")
def delete_annotation(annotation_id: int, db: Session = Depends(get_session)):
    statement = select(Annotation).where(Annotation.id == annotation_id)
    annotation = db.exec(statement).first()
    if not annotation:
        raise HTTPException(status_code=404, detail="Annotation not found")
    db.delete(annotation)
    db.commit()
    return {"message": f"Annotation with id {annotation_id} deleted"}
