from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.config import settings
from app.models.schemas import HistoryResponse, SingleDetectionResponse, TargetListResponse
from app.services.detection_service import detection_service
from app.utils.file_utils import ensure_directories, save_upload_file

router = APIRouter(prefix="/detection", tags=["detection"])
ensure_directories()


@router.post("/single", response_model=SingleDetectionResponse)
async def detect_single_image(
    file: UploadFile = File(...),
    requested_model_name: str = Form("pest-v1", alias="model_name"),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")

    try:
        filename = await save_upload_file(file, settings.UPLOAD_DIR)
        image_path = Path(settings.UPLOAD_DIR) / filename
        result = detection_service.detect_single_image(image_path, requested_model_name)
        return SingleDetectionResponse(success=True, message="Detection completed", data=result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Detection failed: {exc}") from exc


@router.get("/history", response_model=HistoryResponse)
async def get_detection_history():
    history = detection_service.get_history()
    return HistoryResponse(
        success=True,
        message="History loaded",
        data=history,
        total=len(history),
    )


@router.get("/detail/{detection_id}", response_model=SingleDetectionResponse)
async def get_detection_detail(detection_id: str):
    result = detection_service.get_detail(detection_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Detection record not found")
    return SingleDetectionResponse(success=True, message="Detection detail loaded", data=result)


@router.get("/targets/list", response_model=TargetListResponse)
async def get_target_list():
    return TargetListResponse(
        success=True,
        message="Target list loaded",
        data=detection_service.get_targets(),
    )
