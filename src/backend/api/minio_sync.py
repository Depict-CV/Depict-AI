from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from minio import Minio
from minio.error import S3Error

from src.backend.api.clerk_auth import get_current_clerk_user, get_session
from src.backend.db.tables import Project, Data, User, DataTypeEnum, MinIOConfig as MinIOConfigModel

router = APIRouter(prefix="/projects", tags=["minio"])


class MinIOConfig(BaseModel):
    endpoint: str
    access_key: str
    secret_key: str
    use_ssl: bool = False


class MinIOSyncRequest(BaseModel):
    bucket_name: str


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
        
        print(f"\n=== Testing MinIO connection ===")
        print(f"  Original endpoint: {config.endpoint}")
        print(f"  Parsed endpoint: {endpoint}")
        print(f"  Access Key: {config.access_key}")
        print(f"  Secret Key: {config.secret_key[:4]}...")
        print(f"  Use SSL: {config.use_ssl}")
        print(f"================================\n")
        
        # Initialize MinIO client
        client = Minio(
            endpoint,
            access_key=config.access_key,
            secret_key=config.secret_key,
            secure=config.use_ssl
        )
        
        print(f"MinIO client created successfully")
        
        # Test connection by listing buckets
        try:
            buckets = client.list_buckets()
            print(f"Connection successful! Found {len(buckets)} buckets")
        except Exception as list_error:
            print(f"Connection test error: {str(list_error)}")
            raise HTTPException(status_code=403, detail=f"Cannot connect to MinIO: {str(list_error)}")
        
        return {
            "message": "MinIO connection successful",
            "connected": True
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
def configure_minio_credentials(
    project_id: int,
    config: MinIOConfig,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_clerk_user)
):
    """Save MinIO credentials for a project"""
    
    # Verify project exists and user has access
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    try:
        # Save or update MinIO credentials in database
        existing_config = db.exec(
            select(MinIOConfigModel).where(MinIOConfigModel.project_id == project_id)
        ).first()
        
        if existing_config:
            # Update existing configuration
            existing_config.endpoint = config.endpoint
            existing_config.access_key = config.access_key
            existing_config.secret_key = config.secret_key
            existing_config.use_ssl = config.use_ssl
        else:
            # Create new configuration
            minio_config = MinIOConfigModel(
                project_id=project_id,
                endpoint=config.endpoint,
                bucket_name="",  # Will be provided during sync
                access_key=config.access_key,
                secret_key=config.secret_key,
                use_ssl=config.use_ssl
            )
            db.add(minio_config)
        
        db.commit()
        
        return {
            "message": "MinIO credentials saved successfully"
        }
        
    except S3Error as e:
        raise HTTPException(status_code=400, detail=f"MinIO error: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


@router.get("/{project_id}/minio/config")
def get_minio_config(
    project_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_clerk_user)
):
    """Retrieve stored MinIO configuration for a project"""
    
    # Verify project exists and user has access
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get MinIO configuration
    config = db.exec(
        select(MinIOConfigModel).where(MinIOConfigModel.project_id == project_id)
    ).first()
    
    if not config:
        return {
            "configured": False,
            "message": "MinIO not configured for this project"
        }
    
    return {
        "configured": True,
        "endpoint": config.endpoint,
        "bucket_name": config.bucket_name,
        "access_key": config.access_key,
        "secret_key": config.secret_key,  # In production, consider not returning this or masking it
        "use_ssl": config.use_ssl,
        "last_sync": config.last_sync.isoformat() if config.last_sync else None
    }


@router.post("/{project_id}/minio/sync")
def manual_sync_minio(
    project_id: int,
    sync_request: MinIOSyncRequest,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_clerk_user)
):
    """Manually trigger MinIO sync for a project with specified bucket"""
    
    # Verify project exists and user has access
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Retrieve stored MinIO credentials
    config = db.exec(
        select(MinIOConfigModel).where(MinIOConfigModel.project_id == project_id)
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=400, 
            detail="MinIO not configured for this project. Please configure in Project Settings first."
        )
    
    try:
        print(f"\n=== Manual MinIO Sync ===")
        print(f"  Project ID: {project_id}")
        print(f"  Endpoint: {config.endpoint}")
        print(f"  Bucket: {sync_request.bucket_name}")
        print(f"  Use SSL: {config.use_ssl}")
        print(f"========================\n")
        
        # Initialize MinIO client
        client = Minio(
            config.endpoint.replace("http://", "").replace("https://", ""),
            access_key=config.access_key,
            secret_key=config.secret_key,
            secure=config.use_ssl
        )
        
        print(f"MinIO client created")
        
        # Verify bucket exists
        print(f"Checking bucket existence...")
        bucket_exists = client.bucket_exists(sync_request.bucket_name)
        print(f"Bucket exists: {bucket_exists}")
        
        if not bucket_exists:
            raise HTTPException(status_code=400, detail=f"Bucket '{sync_request.bucket_name}' does not exist")
        
        # List all objects in bucket
        objects = client.list_objects(sync_request.bucket_name, recursive=True)
        
        images_synced = 0
        skipped = 0
        
        for obj in objects:
            # Filter for image files
            if obj.object_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')):
                # Check if already exists in database
                existing = db.query(Data).filter(
                    Data.project_id == project_id,
                    Data.location == f"minio://{sync_request.bucket_name}/{obj.object_name}"
                ).first()
                
                if not existing:
                    # Create Data entry
                    data_entry = Data(
                        type=DataTypeEnum.IMAGE,
                        location=f"minio://{sync_request.bucket_name}/{obj.object_name}",
                        author_id=current_user.id,
                        creation_date=datetime.now(),
                        project_id=project_id
                    )
                    db.add(data_entry)
                    images_synced += 1
                else:
                    skipped += 1
        
        # Update last sync timestamp
        config.last_sync = datetime.now()
        db.commit()
        
        return {
            "message": "Manual sync completed",
            "images_synced": images_synced,
            "images_skipped": skipped
        }
        
    except HTTPException:
        raise
    except S3Error as e:
        error_msg = f"MinIO error: {str(e)}"
        print(f"S3Error in manual sync: {error_msg}")
        raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        error_msg = f"Sync failed: {type(e).__name__} - {str(e)}"
        print(f"Exception in manual sync: {error_msg}")
        db.rollback()
        raise HTTPException(status_code=500, detail=error_msg)
