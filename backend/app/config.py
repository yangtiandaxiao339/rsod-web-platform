import os
from pathlib import Path

from pydantic import BaseModel, ConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[1]
STATIC_DIR = BACKEND_DIR / "static"
DATA_DIR = BACKEND_DIR / "data"
RSOD_DIR = DATA_DIR / "rsod"
MODELS_DIR = BACKEND_DIR / "models"


class Settings(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    APP_NAME: str = os.getenv("APP_NAME", "RSOD Detection Platform")
    APP_VERSION: str = os.getenv("APP_VERSION", "0.3.0")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() in {"1", "true", "yes"}

    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    BACKEND_DIR: Path = BACKEND_DIR
    STATIC_DIR: Path = STATIC_DIR
    UPLOAD_DIR: Path = STATIC_DIR / "uploads"
    RESULT_DIR: Path = STATIC_DIR / "results"

    DATA_DIR: Path = DATA_DIR
    RSOD_DIR: Path = RSOD_DIR
    RSOD_IMAGES_DIR: Path = RSOD_DIR / "images"
    RSOD_ANNOTATIONS_DIR: Path = RSOD_DIR / "annotations"
    RSOD_YOLO_DIR: Path = RSOD_DIR / "yolo_dataset"
    RSOD_YAML_PATH: Path = RSOD_YOLO_DIR / "rsod.yaml"

    MODELS_DIR: Path = MODELS_DIR
    BASE_MODEL_DIR: Path = MODELS_DIR / "rsod_yolo11n"
    BASE_MODEL_WEIGHTS_DIR: Path = BASE_MODEL_DIR / "weights"
    YOLO_MODEL_PATH: Path = BASE_MODEL_WEIGHTS_DIR / "yolo11n.pt"
    TRAIN_RUNS_DIR: Path = MODELS_DIR / "runs"
    MODEL_RELEASES_DIR: Path = MODELS_DIR / "releases"
    MODEL_CACHE_DIR: Path = MODELS_DIR / "cache"
    MODEL_PREFIX: str = os.getenv("MODEL_PREFIX", "rsod-yolo11n")

    CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.25"))
    IOU_THRESHOLD: float = float(os.getenv("IOU_THRESHOLD", "0.45"))

    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    MINIO_BUCKET: str = os.getenv("MINIO_BUCKET", "rsod-models")
    MINIO_SECURE: bool = os.getenv("MINIO_SECURE", "false").lower() in {"1", "true", "yes"}
    MINIO_AUTO_UPLOAD: bool = os.getenv("MINIO_AUTO_UPLOAD", "true").lower() in {"1", "true", "yes"}

    CORS_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
        if origin.strip()
    ]


settings = Settings()
