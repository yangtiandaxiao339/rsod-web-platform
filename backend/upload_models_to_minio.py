#!/usr/bin/env python3
"""
Upload local model artifacts to MinIO or list registered models.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from app.config import settings
from app.models.schemas import ModelMetadata, ModelMetrics, TrainingConfigInfo
from app.services.minio_service import minio_service
from app.utils.versioning import parse_artifact_name


def default_metadata(version: str) -> ModelMetadata:
    return ModelMetadata(
        name=settings.MODEL_PREFIX,
        version=version,
        created_at=datetime.now(),
        description="Manually uploaded model artifact",
        metrics=ModelMetrics(),
        config=TrainingConfigInfo(base_model=str(settings.YOLO_MODEL_PATH)),
    )


def upload_file(model_path: Path):
    parsed = parse_artifact_name(model_path.name)
    version = parsed.version if parsed else minio_service.get_next_version()
    metadata_path = model_path.with_suffix(".json")
    if metadata_path.exists():
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    else:
        metadata = default_metadata(version).model_dump(mode="json")
    artifact = minio_service.upload_artifact(model_path, model_path.name, metadata)
    print(json.dumps(artifact.model_dump(mode="json"), ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Upload trained model artifacts to MinIO.")
    parser.add_argument("model_path", nargs="?", help="Optional specific model file to upload.")
    parser.add_argument("--list", action="store_true", help="List registered models.")
    args = parser.parse_args()

    if args.list:
        models = [artifact.model_dump(mode="json") for artifact in minio_service.list_models()]
        print(json.dumps(models, ensure_ascii=False, indent=2))
        return

    if args.model_path:
        upload_file(Path(args.model_path))
        return

    for model_path in sorted(settings.MODEL_RELEASES_DIR.glob("*.pt")):
        upload_file(model_path)


if __name__ == "__main__":
    main()
