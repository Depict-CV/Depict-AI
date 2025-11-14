from fastapi import APIRouter, Body, HTTPException

from ml.main import infer_resnet50

router = APIRouter(prefix="/infer", tags=["ML_Inference"])


@router.post("/resnet50")
def infer_image(payload: dict = Body(...)):
    image_path = payload.get("image_path")
    if not image_path:
        raise HTTPException(status_code=400, detail="Missing image_path in request body")
    try:
        result = infer_resnet50(image_path)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
