from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from app.config import settings
from app.models.schemas import ModelArtifact, ModelMetadata
from app.utils.file_utils import copy_into_directory, read_json, write_json
from app.utils.versioning import get_next_version_from_names, parse_artifact_name


class MinIOService:
    def __init__(self):
        self._client = None
        self._enabled = False
        self._init_client()

    def _init_client(self):
        try:
            from minio import Minio
        except ImportError:
            self._client = None
            self._enabled = False
            return

        try:
            self._client = Minio(
                settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=settings.MINIO_SECURE,
            )
            self._enabled = True
            self._ensure_bucket()
        except Exception:
            self._client = None
            self._enabled = False

    @property
    def enabled(self) -> bool:
        return self._enabled and self._client is not None

    def _ensure_bucket(self):
        if not self.enabled:
            return
        if not self._client.bucket_exists(settings.MINIO_BUCKET):
            self._client.make_bucket(settings.MINIO_BUCKET)

    def get_public_url(self, object_name: str) -> str:
        scheme = "https" if settings.MINIO_SECURE else "http"
        return f"{scheme}://{settings.MINIO_ENDPOINT}/{settings.MINIO_BUCKET}/{object_name}"

    def _metadata_path_for(self, model_path: Path) -> Path:
        return model_path.with_suffix(".json")

    def save_local_artifact(self, source_model_path: Path, object_name: str, metadata: dict[str, Any]) -> ModelArtifact:
        local_model_path = copy_into_directory(source_model_path, settings.MODEL_RELEASES_DIR, object_name)
        metadata_path = self._metadata_path_for(local_model_path)
        write_json(metadata_path, metadata)
        return ModelArtifact(
            object_name=local_model_path.name,
            metadata=ModelMetadata.model_validate(metadata),
            public_url=None,
            source="local",
            local_path=str(local_model_path),
        )

    def upload_artifact(self, source_model_path: Path, object_name: str, metadata: dict[str, Any]) -> ModelArtifact:
        artifact = self.save_local_artifact(source_model_path, object_name, metadata)

        if self.enabled and settings.MINIO_AUTO_UPLOAD:
            metadata_path = Path(artifact.local_path).with_suffix(".json")
            self._client.fput_object(settings.MINIO_BUCKET, object_name, str(artifact.local_path))
            self._client.fput_object(settings.MINIO_BUCKET, metadata_path.name, str(metadata_path))
            artifact.public_url = self.get_public_url(object_name)
            artifact.source = "minio"

        return artifact

    def list_local_models(self) -> list[ModelArtifact]:
        artifacts: list[ModelArtifact] = []
        for model_path in sorted(settings.MODEL_RELEASES_DIR.glob("*.pt")):
            metadata_path = self._metadata_path_for(model_path)
            metadata = None
            if metadata_path.exists():
                metadata = ModelMetadata.model_validate(read_json(metadata_path))
            artifacts.append(
                ModelArtifact(
                    object_name=model_path.name,
                    metadata=metadata,
                    source="local",
                    local_path=str(model_path),
                )
            )
        return artifacts

    def list_remote_models(self) -> list[ModelArtifact]:
        if not self.enabled:
            return []

        artifacts: list[ModelArtifact] = []
        for obj in self._client.list_objects(settings.MINIO_BUCKET, recursive=True):
            if not obj.object_name.endswith(".pt"):
                continue

            metadata = None
            local_meta_path = settings.MODEL_CACHE_DIR / f"{Path(obj.object_name).stem}.json"
            try:
                self._client.fget_object(settings.MINIO_BUCKET, f"{Path(obj.object_name).stem}.json", str(local_meta_path))
                metadata = ModelMetadata.model_validate(read_json(local_meta_path))
            except Exception:
                metadata = None

            artifacts.append(
                ModelArtifact(
                    object_name=obj.object_name,
                    metadata=metadata,
                    public_url=self.get_public_url(obj.object_name),
                    source="minio",
                )
            )
        return artifacts

    def _sort_key(self, object_name: str):
        parsed = parse_artifact_name(object_name)
        if not parsed:
            return ((0, 0, 0), "", 0)
        best_rank = 1 if "-best_" in object_name else 0
        return (parsed.version_tuple, parsed.timestamp, best_rank)

    def list_models(self) -> list[ModelArtifact]:
        remote = {artifact.object_name: artifact for artifact in self.list_remote_models()}
        local = {artifact.object_name: artifact for artifact in self.list_local_models()}
        merged = {**local, **remote}
        return sorted(merged.values(), key=lambda artifact: self._sort_key(artifact.object_name), reverse=True)

    def get_latest_model(self) -> ModelArtifact | None:
        models = self.list_models()
        if not models:
            return None
        return models[0]

    def download_model(self, object_name: str) -> Path | None:
        local_path = settings.MODEL_RELEASES_DIR / Path(object_name).name
        if local_path.exists():
            return local_path

        if not self.enabled:
            return None

        try:
            self._client.fget_object(settings.MINIO_BUCKET, object_name, str(local_path))
        except Exception:
            return None

        metadata_name = f"{Path(object_name).stem}.json"
        try:
            self._client.fget_object(
                settings.MINIO_BUCKET,
                metadata_name,
                str(settings.MODEL_RELEASES_DIR / metadata_name),
            )
        except Exception:
            pass
        return local_path

    def get_next_version(self) -> str:
        file_names = [artifact.object_name for artifact in self.list_models()]
        return get_next_version_from_names(file_names)


minio_service = MinIOService()
