from pathlib import Path
from io import BytesIO

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse, StreamingResponse
from sqlmodel import Session, select
from minio import Minio

from src.backend.api.deps import get_session
from src.backend.db.tables import MinIOConfig

router = APIRouter(prefix="/images", tags=["images"])


@router.get("/serve")
async def serve_image(path: str):
    """Serve an image from the local file system"""
    try:
        file_path = Path(path)
        
        # Security check: ensure the file exists and is actually a file
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Image not found")
        
        if not file_path.is_file():
            raise HTTPException(status_code=400, detail="Path is not a file")
        
        # Check if it's an image file by extension
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
        if file_path.suffix.lower() not in allowed_extensions:
            raise HTTPException(status_code=400, detail="File is not an image")
        
        return FileResponse(
            path=str(file_path),
            media_type=f"image/{file_path.suffix[1:]}",
            headers={"Cache-Control": "public, max-age=3600"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/minio/{project_id}")
async def serve_minio_image(
    project_id: int,
    object_path: str,
    db: Session = Depends(get_session)
):
    """Serve an image from MinIO storage
    
    Args:
        project_id: Project ID to get MinIO credentials
        object_path: Full MinIO object path in format 'bucket/path/to/image.jpg'
    """
    try:
        # Get MinIO config for this project
        minio_config = db.exec(
            select(MinIOConfig).where(MinIOConfig.project_id == project_id)
        ).first()
        
        if not minio_config:
            raise HTTPException(status_code=404, detail="MinIO not configured for this project")
        
        # Parse bucket and object path
        parts = object_path.split('/', 1)
        if len(parts) != 2:
            raise HTTPException(status_code=400, detail="Invalid object path format. Expected: bucket/path/to/file")
        
        bucket_name, file_path = parts
        
        # Initialize MinIO client
        endpoint = minio_config.endpoint.replace('http://', '').replace('https://', '')
        client = Minio(
            endpoint,
            access_key=minio_config.access_key,
            secret_key=minio_config.secret_key,
            secure=minio_config.use_ssl
        )
        
        # Get object from MinIO
        response = client.get_object(bucket_name, file_path)
        image_data = response.read()
        response.close()
        response.release_conn()
        
        # Determine content type from file extension
        file_ext = Path(file_path).suffix.lower()
        content_type_map = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.webp': 'image/webp',
            '.svg': 'image/svg+xml'
        }
        content_type = content_type_map.get(file_ext, 'image/jpeg')
        
        return StreamingResponse(
            BytesIO(image_data),
            media_type=content_type,
            headers={"Cache-Control": "public, max-age=3600"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch image from MinIO: {str(e)}")
