from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ApiModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, protected_namespaces=())


class DetectionBox(ApiModel):
    x1: float
    y1: float
    x2: float
    y2: float
    confidence: float
    class_id: int
    class_name: str


class DetectionResult(ApiModel):
    detection_id: str
    image_url: str
    result_image_url: str
    boxes: List[DetectionBox]
    total_objects: int
    detection_time: float
    detector_name: str = Field(alias="model_name", serialization_alias="model_name")
    created_at: datetime


class SingleDetectionResponse(ApiModel):
    success: bool
    message: str
    data: Optional[DetectionResult] = None


class HistoryItem(ApiModel):
    id: str
    image_url: str
    result_image_url: str
    total_objects: int
    created_at: datetime
    detector_name: str = Field(alias="model_name", serialization_alias="model_name")
    labels: List[str] = Field(default_factory=list)


class HistoryResponse(ApiModel):
    success: bool
    message: str
    data: List[HistoryItem]
    total: int


class TargetItem(ApiModel):
    id: int
    name: str
    chinese_name: str
    description: Optional[str] = None


class TargetListResponse(ApiModel):
    success: bool
    message: str
    data: List[TargetItem]


class ModelMetrics(ApiModel):
    map50: float = 0.0
    map50_95: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1: float = 0.0


class TrainingConfigInfo(ApiModel):
    epochs: int = 0
    batch: int = 0
    imgsz: int = 640
    device: str = "cpu"
    lr0: float = 0.01
    patience: int = 20
    data: str = ""
    base_model: str = ""


class ModelMetadata(ApiModel):
    name: str
    version: str
    created_at: datetime
    description: str
    metrics: ModelMetrics = Field(default_factory=ModelMetrics)
    config: TrainingConfigInfo = Field(default_factory=TrainingConfigInfo)
    extra: dict[str, Any] = Field(default_factory=dict)


class ModelArtifact(ApiModel):
    object_name: str
    metadata: Optional[ModelMetadata] = None
    public_url: Optional[str] = None
    source: str = "local"
    local_path: Optional[str] = None


class ModelListResponse(ApiModel):
    success: bool
    message: str
    data: List[ModelArtifact]
    latest: Optional[ModelArtifact] = None


class CurrentModelInfo(ApiModel):
    object_name: Optional[str] = None
    version: Optional[str] = None
    description: Optional[str] = None
    source: str = "mock"
    loaded: bool = False
    public_url: Optional[str] = None
    local_path: Optional[str] = None


class CurrentModelResponse(ApiModel):
    success: bool
    message: str
    data: Optional[CurrentModelInfo] = None


class ModelReloadRequest(ApiModel):
    object_name: Optional[str] = None


class ModelReloadResponse(ApiModel):
    success: bool
    message: str
    data: Optional[CurrentModelInfo] = None
