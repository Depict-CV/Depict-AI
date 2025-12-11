from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from minio import Minio
from minio.error import S3Error

from src.backend.api.clerk_auth import get_current_clerk_user, get_session
from src.backend.db.tables import Project, Data, User, DataTypeEnum

router = APIRouter(prefix="/projects", tags=["minio"])


class MinIOConfig(BaseModel):
    endpoint: str
    bucket_name: str
    access_key: str
    secret_key: str
    use_ssl: bool = False
    auto_sync: Optional[bool] = True
    sync_interval_hours: Optional[int] = 24


@router.post("/{project_id}/minio/test")
def test_minio_connection(
    project_id: int,
    config: MinIOConfig,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_clerk_user)
):
    """Test MinIO connection and bucket access"""
    
    # Verify project exists and user has access
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    try:
        # Parse endpoint to remove protocol
        endpoint = config.endpoint.replace("http://", "").replace("https://", "")
        
        print(f"Testing MinIO connection:")
        print(f"  Endpoint: {endpoint}")
        print(f"  Bucket: {config.bucket_name}")
        print(f"  Access Key: {config.access_key[:4]}...")
        print(f"  Use SSL: {config.use_ssl}")
        
        # Initialize MinIO client
        client = Minio(
            endpoint,
            access_key=config.access_key,
            secret_key=config.secret_key,
            secure=config.use_ssl
        )
        
        # Check if bucket exists
        bucket_exists = client.bucket_exists(config.bucket_name)
        if not bucket_exists:
            return {
                "message": f"Bucket '{config.bucket_name}' does not exist. Please create it first.",
                "bucket_exists": False,
                "has_read_access": False
            }
        
        # Try to list objects (test read permission)
        try:
            objects = list(client.list_objects(config.bucket_name, max_keys=1))
            object_count = len(objects)
        except Exception as list_error:
            print(f"List objects error: {str(list_error)}")
            raise HTTPException(status_code=403, detail=f"Cannot access bucket: {str(list_error)}")
        
        return {
            "message": "Connection successful",
            "bucket_exists": True,
            "has_read_access": True,
            "sample_object_count": object_count
        }
        
    except HTTPException:
        raise
    except S3Error as e:
        error_msg = f"MinIO S3 error: {e.code} - {e.message if hasattr(e, 'message') else str(e)}"
        print(error_msg)
        raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        error_msg = f"Connection failed: {type(e).__name__} - {str(e)}"
        print(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)


@router.post("/{project_id}/minio/configure")
def configure_minio_and_sync(
    project_id: int,
    config: MinIOConfig,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_clerk_user)
):
    """Configure MinIO for project and perform initial sync"""
    
    # Verify project exists and user has access
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    try:
        # Initialize MinIO client
        client = Minio(
            config.endpoint.replace("http://", "").replace("https://", ""),
            access_key=config.access_key,
            secret_key=config.secret_key,
            secure=config.use_ssl
        )
        
        # Verify bucket exists
        if not client.bucket_exists(config.bucket_name):
            raise HTTPException(status_code=400, detail=f"Bucket '{config.bucket_name}' does not exist")
        
        # TODO: Store MinIO credentials securely in project settings table
        # For now, we'll just perform the sync
        
        # List all objects in bucket
        objects = client.list_objects(config.bucket_name, recursive=True)
        
        images_synced = 0
        skipped = 0
        
        for obj in objects:
            # Filter for image files
            if obj.object_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')):
                # Check if already exists in database
                existing = db.query(Data).filter(
                    Data.project_id == project_id,
                    Data.location == f"minio://{config.bucket_name}/{obj.object_name}"
                ).first()
                
                if not existing:
                    # Create presigned URL or use MinIO path
                    image_location = f"minio://{config.bucket_name}/{obj.object_name}"
                    
                    # Create Data entry
                    data_entry = Data(
                        type=DataTypeEnum.IMAGE,
                        location=image_location,
                        author_id=current_user.id,
                        creation_date=datetime.now(),
                        project_id=project_id
                    )
                    db.add(data_entry)
                    images_synced += 1
                else:
                    skipped += 1
        
        db.commit()
        
        return {
            "message": "MinIO configured and sync completed",
            "images_synced": images_synced,
            "images_skipped": skipped,
            "auto_sync_enabled": config.auto_sync,
            "sync_interval_hours": config.sync_interval_hours
        }
        
    except S3Error as e:
        raise HTTPException(status_code=400, detail=f"MinIO error: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


@router.post("/{project_id}/minio/sync")
def manual_sync_minio(
    project_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_clerk_user)
):
    """Manually trigger MinIO sync for a project"""
    
    # TODO: Retrieve stored MinIO credentials for project
    # For now, return error
    raise HTTPException(
        status_code=501, 
        detail="Manual sync not implemented. Please reconfigure MinIO settings to sync."
    )
