from datetime import datetime

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlmodel import Session, select

from src.backend.api.deps import get_session
from src.backend.db.tables import Annotation, AnnotationStatus, Data, Project
from src.ml.main import infer_resnet50

router = APIRouter(prefix="/infer", tags=["ML_Inference"])


@router.post("/resnet50")
def infer_image(payload: dict = Body(...)):
    """Infer single image using ResNet50"""
    image_path = payload.get("image_path")
    if not image_path:
        raise HTTPException(status_code=400, detail="Missing image_path in request body")
    try:
        result = infer_resnet50(image_path)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/resnet50/batch")
def infer_batch(payload: dict = Body(...), db: Session = Depends(get_session)):
    """Infer multiple images and optionally save as annotations"""
    image_paths = payload.get("image_paths", [])
    data_ids = payload.get("data_ids", [])
    project_id = payload.get("project_id")
    save_annotations = payload.get("save_annotations", False)
    
    if not image_paths and not data_ids:
        raise HTTPException(status_code=400, detail="Must provide either image_paths or data_ids")
    
    results = []
    
    # If data_ids provided, fetch from database
    if data_ids:
        statement = select(Data).where(Data.id.in_(data_ids))
        data_items = db.exec(statement).all()
        
        for data_item in data_items:
            try:
                result = infer_resnet50(data_item.location)
                results.append({
                    "data_id": data_item.id,
                    "location": data_item.location,
                    "prediction": result,
                    "status": "success"
                })
                
                # Save as annotation if requested
                if save_annotations and project_id:
                    annotation = Annotation(
                        status=AnnotationStatus.ML_ANNOTATION,
                        label=result["class_name"],
                        annotation_score=0,
                        data_id=data_item.id,
                        project_id=project_id,
                        creation_date=datetime.now()
                    )
                    db.add(annotation)
                    
            except Exception as e:
                results.append({
                    "data_id": data_item.id,
                    "location": data_item.location,
                    "error": str(e),
                    "status": "failed"
                })
        
        if save_annotations:
            db.commit()
    
    # If image_paths provided, process directly
    else:
        for image_path in image_paths:
            try:
                result = infer_resnet50(image_path)
                results.append({
                    "location": image_path,
                    "prediction": result,
                    "status": "success"
                })
            except Exception as e:
                results.append({
                    "location": image_path,
                    "error": str(e),
                    "status": "failed"
                })
    
    successful = len([r for r in results if r["status"] == "success"])
    failed = len([r for r in results if r["status"] == "failed"])
    
    return {
        "total": len(results),
        "successful": successful,
        "failed": failed,
        "results": results,
        "annotations_saved": save_annotations
    }


@router.post("/resnet50/project")
def infer_project(payload: dict = Body(...), db: Session = Depends(get_session)):
    """Infer all non-annotated images in a project"""
    project_id = payload.get("project_id")
    save_annotations = payload.get("save_annotations", True)
    limit = payload.get("limit")  # Optional limit for batch size
    
    if not project_id:
        raise HTTPException(status_code=400, detail="Missing project_id")
    
    # Verify project exists
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get non-annotated data items
    statement = select(Data).where(
        (Data.project_id == project_id) &
        (~Data.id.in_(select(Annotation.data_id).where(Annotation.project_id == project_id)))
    )
    
    if limit:
        statement = statement.limit(limit)
    
    data_items = db.exec(statement).all()
    
    if not data_items:
        return {
            "total": 0,
            "successful": 0,
            "failed": 0,
            "results": [],
            "message": "No unannotated images found in project"
        }
    
    results = []
    
    for data_item in data_items:
        try:
            result = infer_resnet50(data_item.location)
            results.append({
                "data_id": data_item.id,
                "location": data_item.location,
                "prediction": result,
                "status": "success"
            })
            
            # Save as annotation
            if save_annotations:
                annotation = Annotation(
                    status=AnnotationStatus.ML_ANNOTATION,
                    label=result["class_name"],
                    annotation_score=None,
                    data_id=data_item.id,
                    project_id=project_id,
                    creation_date=datetime.now()
                )
                db.add(annotation)
                
        except Exception as e:
            results.append({
                "data_id": data_item.id,
                "location": data_item.location,
                "error": str(e),
                "status": "failed"
            })
    
    if save_annotations:
        db.commit()
    
    successful = len([r for r in results if r["status"] == "success"])
    failed = len([r for r in results if r["status"] == "failed"])
    
    return {
        "total": len(results),
        "successful": successful,
        "failed": failed,
        "results": results,
        "annotations_saved": save_annotations,
        "project_id": project_id,
        "project_name": project.name
    }
