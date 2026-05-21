#!/usr/bin/env python3
"""
Train, evaluate, and predict with an RSOD YOLO model.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from app.config import settings
from app.models.schemas import ModelMetadata, ModelMetrics, TrainingConfigInfo
from app.services.minio_service import minio_service
from app.utils.file_utils import ensure_directories
from app.utils.versioning import get_next_version_from_names


@dataclass
class TrainConfig:
    epochs: int = 100
    batch: int = 16
    imgsz: int = 640
    device: str = "cpu"
    lr0: float = 0.01
    patience: int = 20
    data: str = str(settings.RSOD_YAML_PATH)
    model: str = str(settings.YOLO_MODEL_PATH)


class YOLOTrainer:
    def __init__(self):
        ensure_directories()
        self._yolo_cls = self._import_yolo()

    def _import_yolo(self):
        try:
            from ultralytics import YOLO
        except ImportError as exc:
            raise RuntimeError(
                "ultralytics is not installed. Install backend requirements before training."
            ) from exc
        return YOLO

    def _timestamp(self) -> str:
        return datetime.now().strftime("%Y%m%d%H%M%S")

    def _next_version(self) -> str:
        existing_files = [path.name for path in settings.MODEL_RELEASES_DIR.glob("*.pt")]
        return get_next_version_from_names(existing_files)

    def _build_object_name(self, variant: str, version: str, timestamp: str) -> str:
        return f"{settings.MODEL_PREFIX}-{variant}_v{version}_{timestamp}.pt"

    def _save_metadata(self, version: str, metrics: ModelMetrics, config: TrainConfig) -> ModelMetadata:
        return ModelMetadata(
            name=settings.MODEL_PREFIX,
            version=version,
            created_at=datetime.now(),
            description="RSOD YOLO model trained from the Day3 training pipeline",
            metrics=metrics,
            config=TrainingConfigInfo(
                epochs=config.epochs,
                batch=config.batch,
                imgsz=config.imgsz,
                device=config.device,
                lr0=config.lr0,
                patience=config.patience,
                data=config.data,
                base_model=config.model,
            ),
        )

    def _extract_metrics(self, results) -> ModelMetrics:
        box_metrics = getattr(results, "box", None)
        precision = float(getattr(box_metrics, "mp", 0.0) or 0.0)
        recall = float(getattr(box_metrics, "mr", 0.0) or 0.0)
        map50 = float(getattr(box_metrics, "map50", 0.0) or 0.0)
        map50_95 = float(getattr(box_metrics, "map", 0.0) or 0.0)
        f1 = 0.0
        if precision + recall > 0:
            f1 = 2 * precision * recall / (precision + recall)
        return ModelMetrics(
            map50=round(map50, 6),
            map50_95=round(map50_95, 6),
            precision=round(precision, 6),
            recall=round(recall, 6),
            f1=round(f1, 6),
        )

    def train(self, config: TrainConfig, version: str | None = None) -> dict:
        version = version or self._next_version()
        timestamp = self._timestamp()
        run_name = f"{settings.MODEL_PREFIX}_v{version}_{timestamp}"

        model = self._yolo_cls(config.model)
        train_results = model.train(
            data=config.data,
            epochs=config.epochs,
            batch=config.batch,
            imgsz=config.imgsz,
            device=config.device,
            lr0=config.lr0,
            patience=config.patience,
            project=str(settings.TRAIN_RUNS_DIR),
            name=run_name,
            exist_ok=True,
        )

        run_dir = Path(getattr(train_results, "save_dir", settings.TRAIN_RUNS_DIR / run_name))
        weights_dir = run_dir / "weights"
        best_path = weights_dir / "best.pt"
        last_path = weights_dir / "last.pt"
        if not best_path.exists():
            raise FileNotFoundError(f"Training completed but {best_path} was not found.")

        val_model = self._yolo_cls(str(best_path))
        metrics = self._extract_metrics(val_model.val(data=config.data, imgsz=config.imgsz, device=config.device))
        metadata = self._save_metadata(version, metrics, config)
        metadata_payload = metadata.model_dump(mode="json")

        best_object_name = self._build_object_name("best", version, timestamp)
        best_artifact = minio_service.upload_artifact(best_path, best_object_name, metadata_payload)

        last_artifact = None
        if last_path.exists():
            last_object_name = self._build_object_name("last", version, timestamp)
            last_artifact = minio_service.upload_artifact(last_path, last_object_name, metadata_payload)

        summary = {
            "version": version,
            "run_dir": str(run_dir),
            "best_model": best_artifact.model_dump(mode="json"),
            "last_model": last_artifact.model_dump(mode="json") if last_artifact else None,
            "metrics": metadata.metrics.model_dump(mode="json"),
        }
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return summary

    def evaluate(self, model_path: str, data: str, imgsz: int = 640, device: str = "cpu") -> dict:
        model = self._yolo_cls(model_path)
        metrics = self._extract_metrics(model.val(data=data, imgsz=imgsz, device=device))
        payload = metrics.model_dump(mode="json")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return payload

    def predict(self, model_path: str, image_path: str, conf: float = 0.3) -> str:
        model = self._yolo_cls(model_path)
        results = model.predict(
            source=image_path,
            conf=conf,
            save=True,
            project=str(settings.RESULT_DIR),
            name="predict",
            exist_ok=True,
        )
        output_dir = Path(getattr(results[0], "save_dir", settings.RESULT_DIR / "predict"))
        print(str(output_dir))
        return str(output_dir)


def build_parser():
    parser = argparse.ArgumentParser(description="Train or evaluate an RSOD YOLO model.")
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--lr0", type=float, default=0.01)
    parser.add_argument("--patience", type=int, default=20)
    parser.add_argument("--data", default=str(settings.RSOD_YAML_PATH))
    parser.add_argument("--model", default=str(settings.YOLO_MODEL_PATH))
    parser.add_argument("--version", default=None)
    parser.add_argument("--evaluate", action="store_true")
    parser.add_argument("--model-path", default=None)
    parser.add_argument("--predict", default=None)
    parser.add_argument("--conf", type=float, default=0.3)
    return parser


def main():
    args = build_parser().parse_args()
    trainer = YOLOTrainer()

    if args.evaluate:
        model_path = args.model_path or args.model
        trainer.evaluate(model_path=model_path, data=args.data, imgsz=args.imgsz, device=args.device)
        return

    if args.predict:
        model_path = args.model_path or args.model
        trainer.predict(model_path=model_path, image_path=args.predict, conf=args.conf)
        return

    config = TrainConfig(
        epochs=args.epochs,
        batch=args.batch,
        imgsz=args.imgsz,
        device=args.device,
        lr0=args.lr0,
        patience=args.patience,
        data=args.data,
        model=args.model,
    )
    trainer.train(config=config, version=args.version)


if __name__ == "__main__":
    main()
