from __future__ import annotations

import time
import uuid
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw

from app.config import settings
from app.models.schemas import (
    CurrentModelInfo,
    DetectionBox,
    DetectionResult,
    HistoryItem,
    ModelArtifact,
    TargetItem,
)
from app.services.minio_service import minio_service
from app.utils.file_utils import get_file_url


class DetectionService:
    def __init__(self):
        self._history: dict[str, DetectionResult] = {}
        self._model = None
        self._using_mock = True
        self._current_model = CurrentModelInfo(
            object_name=None,
            version=None,
            description="Mock detector",
            source="mock",
            loaded=False,
        )
        self._targets = [
            TargetItem(id=0, name="aircraft", chinese_name="飞机", description="遥感影像中的各类飞机目标"),
            TargetItem(id=1, name="oiltank", chinese_name="油罐", description="圆形储油罐与相关工业储罐目标"),
            TargetItem(id=2, name="overpass", chinese_name="立交桥", description="道路立交桥、跨线桥等复杂交通结构"),
            TargetItem(id=3, name="playground", chinese_name="操场", description="学校或公共区域中的操场与运动场地"),
        ]
        self.reload_model()

    def _import_yolo(self):
        try:
            from ultralytics import YOLO
        except ImportError:
            return None
        return YOLO

    def list_models(self) -> list[ModelArtifact]:
        return minio_service.list_models()

    def get_latest_model_artifact(self) -> ModelArtifact | None:
        return minio_service.get_latest_model()

    def get_current_model_info(self) -> CurrentModelInfo:
        return self._current_model

    def _load_yolo_model(self, model_path: Path) -> bool:
        yolo_cls = self._import_yolo()
        if yolo_cls is None or not model_path.exists():
            return False

        try:
            self._model = yolo_cls(str(model_path))
            self._using_mock = False
            return True
        except Exception:
            self._model = None
            self._using_mock = True
            return False

    def reload_model(self, object_name: str | None = None) -> CurrentModelInfo:
        artifact = None
        local_path = None

        if object_name:
            local_path = minio_service.download_model(object_name)
            artifact = next((item for item in minio_service.list_models() if item.object_name == object_name), None)
        else:
            artifact = minio_service.get_latest_model()
            if artifact:
                local_path = minio_service.download_model(artifact.object_name)

        candidate_path = local_path
        if candidate_path is None and settings.YOLO_MODEL_PATH.exists():
            candidate_path = settings.YOLO_MODEL_PATH

        if candidate_path and self._load_yolo_model(Path(candidate_path)):
            version = artifact.metadata.version if artifact and artifact.metadata else None
            description = artifact.metadata.description if artifact and artifact.metadata else "Loaded local YOLO model"
            public_url = artifact.public_url if artifact else None
            object_label = artifact.object_name if artifact else Path(candidate_path).name
            self._current_model = CurrentModelInfo(
                object_name=object_label,
                version=version,
                description=description,
                source=artifact.source if artifact else "local-base",
                loaded=True,
                public_url=public_url,
                local_path=str(candidate_path),
            )
            return self._current_model

        self._model = None
        self._using_mock = True
        self._current_model = CurrentModelInfo(
            object_name=None,
            version=None,
            description="Mock detector",
            source="mock",
            loaded=False,
            local_path=str(candidate_path) if candidate_path else None,
        )
        return self._current_model

    def _mock_boxes(self, width: int, height: int) -> list[DetectionBox]:
        presets = [
            ("aircraft", 0.96, 0, 0.10, 0.08, 0.42, 0.34),
            ("oiltank", 0.89, 1, 0.54, 0.18, 0.80, 0.42),
            ("playground", 0.85, 3, 0.25, 0.56, 0.73, 0.87),
        ]
        items: list[DetectionBox] = []
        for class_name, confidence, class_id, left, top, right, bottom in presets:
            items.append(
                DetectionBox(
                    x1=round(width * left, 2),
                    y1=round(height * top, 2),
                    x2=round(width * right, 2),
                    y2=round(height * bottom, 2),
                    confidence=confidence,
                    class_id=class_id,
                    class_name=class_name,
                )
            )
        return items

    def _save_mock_result(self, image_path: Path, boxes: list[DetectionBox]) -> str:
        result_filename = f"{uuid.uuid4().hex}_result.jpg"
        result_path = settings.RESULT_DIR / result_filename

        image = Image.open(image_path).convert("RGB")
        draw = ImageDraw.Draw(image)
        colors = ["#1f8f55", "#2563eb", "#f59e0b", "#dc2626"]

        for index, box in enumerate(boxes):
            color = colors[index % len(colors)]
            draw.rectangle([(box.x1, box.y1), (box.x2, box.y2)], outline=color, width=4)
            label = f"{box.class_name} {box.confidence:.2f}"
            text_top = max(0, box.y1 - 24)
            draw.rectangle([(box.x1, text_top), (min(box.x1 + 180, image.width), box.y1)], fill=color)
            draw.text((box.x1 + 6, text_top + 5), label, fill="white")

        image.save(result_path, quality=92)
        return result_filename

    def _run_yolo(self, image_path: Path) -> tuple[list[DetectionBox], str]:
        results = self._model.predict(
            source=str(image_path),
            conf=settings.CONFIDENCE_THRESHOLD,
            iou=settings.IOU_THRESHOLD,
            save=False,
            verbose=False,
        )
        result = results[0]
        names = result.names if hasattr(result, "names") else getattr(self._model, "names", {})

        boxes: list[DetectionBox] = []
        if result.boxes is not None:
            for box in result.boxes:
                x1, y1, x2, y2 = [float(value) for value in box.xyxy[0].tolist()]
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                if isinstance(names, dict):
                    class_name = str(names.get(class_id, class_id))
                else:
                    class_name = str(names[class_id])
                boxes.append(
                    DetectionBox(
                        x1=x1,
                        y1=y1,
                        x2=x2,
                        y2=y2,
                        confidence=confidence,
                        class_id=class_id,
                        class_name=class_name,
                    )
                )

        annotated = result.plot()
        result_filename = f"{uuid.uuid4().hex}_result.jpg"
        result_path = settings.RESULT_DIR / result_filename
        Image.fromarray(annotated[:, :, ::-1]).save(result_path, quality=92)
        return boxes, result_filename

    def detect_single_image(self, image_path: str | Path, model_name: str = "pest-v1") -> DetectionResult:
        image_path = Path(image_path)
        start_time = time.time()

        if self._model is not None and not self._using_mock:
            boxes, result_filename = self._run_yolo(image_path)
        else:
            image = Image.open(image_path).convert("RGB")
            boxes = self._mock_boxes(image.width, image.height)
            result_filename = self._save_mock_result(image_path, boxes)

        result = DetectionResult(
            detection_id=str(uuid.uuid4()),
            image_url=get_file_url("uploads", image_path.name),
            result_image_url=get_file_url("results", result_filename),
            boxes=boxes,
            total_objects=len(boxes),
            detection_time=round(time.time() - start_time, 3),
            detector_name=model_name,
            created_at=datetime.now(),
        )
        self._history[result.detection_id] = result
        return result

    def get_history(self) -> list[HistoryItem]:
        items = sorted(self._history.values(), key=lambda item: item.created_at, reverse=True)
        return [
            HistoryItem(
                id=item.detection_id,
                image_url=item.image_url,
                result_image_url=item.result_image_url,
                total_objects=item.total_objects,
                created_at=item.created_at,
                detector_name=item.detector_name,
                labels=sorted({box.class_name for box in item.boxes}),
            )
            for item in items
        ]

    def get_detail(self, detection_id: str) -> DetectionResult | None:
        return self._history.get(detection_id)

    def get_targets(self) -> list[TargetItem]:
        return list(self._targets)


detection_service = DetectionService()
