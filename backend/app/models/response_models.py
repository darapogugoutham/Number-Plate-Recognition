from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    x: int
    y: int
    width: int
    height: int


class DetectionResponse(BaseModel):
    id: str
    plate_number: str | None = None
    raw_ocr_text: str | None = None
    cleaned_text: str | None = None
    status: Literal["success", "no_plate_detected", "ocr_failed", "invalid_image"]
    message: str
    detection_confidence: float = Field(ge=0.0, le=1.0)
    ocr_confidence: float = Field(ge=0.0, le=1.0)
    bounding_box: BoundingBox | None = None
    original_image_path: str
    plate_crop_path: str | None = None
    model_version: str
    processing_time_ms: int
    created_at: datetime


class HealthResponse(BaseModel):
    status: str
    app: str


class MetricsResponse(BaseModel):
    total_requests: int
    successful_detections: int
    failed_detections: int
    average_processing_time_ms: float
