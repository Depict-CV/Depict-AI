import os
from datetime import datetime
from pathlib import Path
from typing import List

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlmodel import Session, select

from src.backend.api.deps import get_session
from src.backend.db.tables import Annotation, Data, Project, User

router = APIRouter(prefix="/data", tags=["data"])


class ScanDirectoryRequest(BaseModel):
    directory_path: str


# Supported image extensions
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".tiff", ".tif", ".ico"}


def parse_creation_date(data: dict, metadata: dict | None) -> datetime | None:
    date_value = data.get("creation_date")
    if not date_value and metadata:
        date_value = metadata.get("image_datetime")

    if not date_value:
        return None

    if isinstance(date_value, datetime):
        return date_value

    if not isinstance(date_value, str):
        return None

    normalized = date_value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def parse_metadata(data: dict) -> dict | None:
    metadata = data.get("metadata")
    if not isinstance(metadata, dict):
        metadata = data.get("data_metadata")
    if isinstance(metadata, dict):
        return metadata
    return None


@router.post("/scan-directory")
def scan_directory(request: ScanDirectoryRequest):
    """Scan a directory recursively for image files"""
    directory_path = request.directory_path

    # Validate directory exists
    if not os.path.exists(directory_path):
        raise HTTPException(status_code=404, detail=f"Directory not found: {directory_path}")

    if not os.path.isdir(directory_path):
        raise HTTPException(status_code=400, detail=f"Path is not a directory: {directory_path}")

    # Scan for images
    image_files = []
    try:
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                # Check if file has image extension
                file_ext = Path(file).suffix.lower()
                if file_ext in IMAGE_EXTENSIONS:
                    full_path = os.path.join(root, file)
                    # Normalize path separators
                    normalized_path = full_path.replace("\\", "/")
                    image_files.append(normalized_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scanning directory: {str(e)}")

    return {"directory": directory_path, "images": image_files, "count": len(image_files)}


###############
#    create   #
###############
@router.post("/")
def create_data(data: dict = Body(...), db: Session = Depends(get_session)):
    location = data.get("location")
    user_id = data.get("user_id")
    project_id = data.get("project_id")
    data_type = data.get("type")
    if not location or not user_id or not project_id or not data_type:
        raise HTTPException(
            status_code=400,
            detail="location, user_id, project_id, and type are required",
        )
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    metadata = parse_metadata(data)
    creation_date = parse_creation_date(data, metadata)

    new_data = Data(
        location=location,
        author_id=user_id,
        project_id=project_id,
        type=data_type,
        creation_date=creation_date,
        data_metadata=metadata,
    )
    db.add(new_data)
    db.commit()
    db.refresh(new_data)
    return new_data


@router.post("/add_batch")
def create_data_batch(data_list: List[dict] = Body(...), db: Session = Depends(get_session)):
    created_items = []
    skipped_items = []
    for data in data_list:
        location = data.get("location")
        user_id = data.get("user_id")
        project_id = data.get("project_id")
        data_type = data.get("type")
        if not location or not user_id or not project_id or not data_type:
            raise HTTPException(
                status_code=400,
                detail="location, user_id, project_id, and type are required",
            )
        statement = select(Data).where((Data.location == location) & (Data.project_id == project_id))
        existing_data = db.exec(statement).first()
        if existing_data:
            skipped_items.append({"location": location, "reason": "already exists"})
            continue

        # Try to get user by ID (integer) first, then by oauth_id (string)
        user = db.get(User, user_id) if isinstance(user_id, int) else None
        if not user:
            # Try to find by oauth_id
            user_statement = select(User).where(User.oauth_id == str(user_id))
            user = db.exec(user_statement).first()
        if not user:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")

        project = db.get(Project, project_id)
        if not project:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

        metadata = parse_metadata(data)
        creation_date = parse_creation_date(data, metadata)

        new_data = Data(
            location=location,
            author_id=user.id,
            project_id=project_id,
            type=data_type,
            creation_date=creation_date,
            data_metadata=metadata,
        )
        db.add(new_data)
        created_items.append(new_data)

    db.commit()
    for item in created_items:
        db.refresh(item)

    return {
        "created": len(created_items),
        "skipped": len(skipped_items),
        "created_items": created_items,
        "skipped_items": skipped_items,
    }


###############
#    read     #
###############
@router.get("/")
def read_data_paginated(
    project_id: int = Query(..., description="Project ID to fetch data for"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
    db: Session = Depends(get_session),
):
    """Get paginated data for a project"""
    statement = select(Data).where(Data.project_id == project_id).offset(skip).limit(limit)
    data_list = db.exec(statement).all()
    print(f"Found {len(data_list)} records")
    return data_list


@router.get("/non_labeled")
def read_non_labeled_data(project_id: int = Query(...), db: Session = Depends(get_session)):
    statement = select(Data).where(
        (Data.project_id == project_id)
        & (~Data.id.in_(select(Annotation.data_id).where(Annotation.project_id == project_id)))
    )
    data_list = db.exec(statement).all()
    return data_list


@router.post("/batch")
def read_data_batch(data_ids: dict = Body(...), db: Session = Depends(get_session)):
    ids = data_ids["data_ids"]
    if not ids or not isinstance(ids, list):
        raise HTTPException(status_code=400, detail="data_ids must be a non-empty list")
    statement = select(Data).where(Data.id.in_(ids))
    data_list = db.exec(statement).all()
    return data_list


###############
#   update    #
###############
@router.put("/{data_id}")
def update_data(data_id: int, updated_data: Data, db: Session = Depends(get_session)):
    data = db.get(Data, data_id)
    if not data:
        raise HTTPException(status_code=404, detail="Data not found")
    db.commit()
    db.refresh(updated_data)
    return data


###############
#   delete    #
###############
@router.delete("/{data_id}")
def delete_data(data_id: int, db: Session = Depends(get_session)):
    statement = select(Data).where(Data.id == data_id)
    data = db.exec(statement).first()
    if not data:
        raise HTTPException(status_code=404, detail="Data not found")
    db.delete(data)
    db.commit()
    return {"message": f"Data with id {data_id} deleted"}
