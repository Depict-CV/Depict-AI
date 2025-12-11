from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

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
