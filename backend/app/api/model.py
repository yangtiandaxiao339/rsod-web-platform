from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    CurrentModelResponse,
    ModelListResponse,
    ModelReloadRequest,
    ModelReloadResponse,
)
from app.services.detection_service import detection_service

router = APIRouter(prefix="/model", tags=["model"])


@router.get("/list", response_model=ModelListResponse)
async def list_models():
    models = detection_service.list_models()
    latest = detection_service.get_latest_model_artifact()
    return ModelListResponse(
        success=True,
        message="Model list loaded",
        data=models,
        latest=latest,
    )


@router.get("/current", response_model=CurrentModelResponse)
async def get_current_model():
    return CurrentModelResponse(
        success=True,
        message="Current model loaded",
        data=detection_service.get_current_model_info(),
    )


@router.post("/reload", response_model=ModelReloadResponse)
async def reload_model(payload: ModelReloadRequest):
    info = detection_service.reload_model(payload.object_name)
    if not info.loaded:
        raise HTTPException(status_code=500, detail="Unable to load the requested model")
    return ModelReloadResponse(
        success=True,
        message="Model reloaded",
        data=info,
    )
