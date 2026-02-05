from datetime import datetime

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlmodel import Session, desc, select

from src.backend.api.deps import get_session
from src.backend.db.tables import Annotation, AnnotationHistoryStatus, Data, Project, User

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
    description = data.get("description")

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
    # Label is optional - can be None for general annotations
    new_annotation = Annotation(
        data_id=data_id,
        author_id=user_id,
        project_id=project_id,
        status=status,
        annotation_score=annotation_score,
        label=label,
        description=description,
        creation_date=datetime.now(),
    )
    db.add(new_annotation)
    db.commit()
    db.refresh(new_annotation)
    return new_annotation


###############
#    read     #
###############
@router.get("/")
def get_annotations(
    project_id: int = Query(..., description="Project ID to fetch annotations for"),
    history_status: str = Query("CURRENT", description="Filter annotations by history status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(1000, ge=1, le=10000, description="Maximum number of records to return"),
    db: Session = Depends(get_session),
):
    """Get all annotations for a project with pagination"""
    statement = select(Annotation).where(Annotation.project_id == project_id).offset(skip).limit(limit)
    if history_status:
        statement = statement.where(Annotation.history_status == history_status)
    annotations = db.exec(statement).all()
    return annotations


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
@router.post("/update-status/{data_id}")
def update_data_annotations_status(data_id: int, data: dict = Body(...), db: Session = Depends(get_session)):
    """Update status for all annotations of a specific data item.

    Body: {
      "status": "certified" | "rejected" | "to review"
    }
    """
    new_status = data.get("status")
    if not new_status:
        raise HTTPException(status_code=400, detail="status is required")

    valid_statuses = ["certified", "rejected", "to review"]
    if new_status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}")

    # Get all annotations for this data item
    statement = select(Annotation).where(Annotation.data_id == data_id)
    annotations = db.exec(statement).all()

    if not annotations:
        raise HTTPException(status_code=404, detail=f"No annotations found for data ID {data_id}")

    # Update all annotations with new status
    for annotation in annotations:
        annotation.status = new_status
        # If status is being changed to 'rejected', mark as HISTORY
        if new_status == "rejected" and annotation.history_status == AnnotationHistoryStatus.CURRENT:
            annotation.history_status = AnnotationHistoryStatus.HISTORY

    db.commit()

    return {
        "message": f"Updated {len(annotations)} annotation(s) for data ID {data_id}",
        "data_id": data_id,
        "updated_count": len(annotations),
        "status": new_status,
    }


@router.patch("/")
def update_annotation(data: dict = Body(...), db: Session = Depends(get_session)):
    annotation_id = data["id"]
    annotation = db.get(Annotation, annotation_id)
    if not annotation:
        raise HTTPException(status_code=404, detail="Annotation not found")

    # If this is a modification (updating label, description, coordinates, etc.)
    # Mark the current annotation as HISTORY and create a new one as CURRENT
    is_modification = any(key in data for key in ["label", "description", "x1", "y1", "x2", "y2", "annotation_score"])

    if is_modification and annotation.history_status == AnnotationHistoryStatus.CURRENT:
        # Mark current annotation as HISTORY
        annotation.history_status = AnnotationHistoryStatus.HISTORY
        db.commit()

        # Create a new annotation as CURRENT with updated values
        new_annotation_data = {
            "data_id": annotation.data_id,
            "author_id": annotation.author_id,
            "project_id": annotation.project_id,
            "status": annotation.status,
            "history_status": AnnotationHistoryStatus.CURRENT,
            "label": data.get("label", annotation.label),
            "description": data.get("description", annotation.description),
            "x1": data.get("x1", annotation.x1),
            "y1": data.get("y1", annotation.y1),
            "x2": data.get("x2", annotation.x2),
            "y2": data.get("y2", annotation.y2),
            "annotation_score": data.get("annotation_score", annotation.annotation_score),
            "creation_date": datetime.now(),
        }
        new_annotation = Annotation(**new_annotation_data)
        db.add(new_annotation)
        db.commit()
        db.refresh(new_annotation)
        return new_annotation
    else:
        # Just update status or other non-modification fields
        if "annotation_score" in data:
            annotation.annotation_score = data["annotation_score"]
        if "status" in data:
            annotation.status = data["status"]
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
