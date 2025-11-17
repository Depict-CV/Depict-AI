from datetime import datetime

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlmodel import Session, desc, select

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
        creation_date=datetime.now(),
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


@router.post("/batch")
def read_annotation_by_score(
    data: dict = Body(...),
    db: Session = Depends(get_session),
):
    """
    {
      "offset": 0,
      "limit": 50,
      "project_id": 1,
      "selected_labels": ["dog", "car"],
      "sort_by": "score",        // or "date"
      "sort_order": "asc"        // or "desc"
    }
    """
    offset = data.get("offset", 0)
    limit = data.get("limit", 50)
    project_id = data["project_id"]  # required
    selected_labels = data.get("selected_labels", [])

    sort_by = data.get("sort_by", "score")  # default score
    sort_order = data.get("sort_order", "asc")  # default asc

    # ---- BASE QUERY ----
    query = select(Annotation).where(Annotation.project_id == project_id)

    # ---- FILTER BY LABELS ----
    if selected_labels:
        query = query.where(Annotation.label.in_(selected_labels))

    # ---- SORTING ----
    if sort_by == "score":
        field = Annotation.annotation_score
    elif sort_by == "date":
        field = Annotation.creation_date
    else:
        raise HTTPException(status_code=400, detail=f"Invalid sort_by: {sort_by}")

    # ASC / DESC
    if sort_order == "desc":
        query = query.order_by(desc(field))
    else:
        query = query.order_by(field)

    # ---- EXECUTE ----
    results = db.exec(query.offset(offset).limit(limit)).all()

    return results


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
