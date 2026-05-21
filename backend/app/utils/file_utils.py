import json
import shutil
import uuid
from pathlib import Path
from typing import Any

from fastapi import UploadFile

from app.config import settings


def ensure_directories():
    for directory in (
        settings.STATIC_DIR,
        settings.UPLOAD_DIR,
        settings.RESULT_DIR,
        settings.DATA_DIR,
        settings.RSOD_DIR,
        settings.RSOD_IMAGES_DIR,
        settings.RSOD_ANNOTATIONS_DIR,
        settings.RSOD_YOLO_DIR,
        settings.MODELS_DIR,
        settings.BASE_MODEL_DIR,
        settings.BASE_MODEL_WEIGHTS_DIR,
        settings.TRAIN_RUNS_DIR,
        settings.MODEL_RELEASES_DIR,
        settings.MODEL_CACHE_DIR,
    ):
        Path(directory).mkdir(parents=True, exist_ok=True)


async def save_upload_file(file: UploadFile, upload_dir: Path) -> str:
    ensure_directories()
    suffix = Path(file.filename or "upload.bin").suffix or ".bin"
    filename = f"{uuid.uuid4().hex}{suffix.lower()}"
    destination = Path(upload_dir) / filename
    destination.write_bytes(await file.read())
    return filename


def get_file_url(folder: str, filename: str) -> str:
    return f"/static/{folder}/{filename}"


def write_json(path: Path, payload: dict[str, Any]):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def copy_into_directory(source: Path, target_dir: Path, target_name: str | None = None) -> Path:
    target_dir.mkdir(parents=True, exist_ok=True)
    destination = target_dir / (target_name or source.name)
    if source.resolve() != destination.resolve():
        shutil.copy2(source, destination)
    return destination
