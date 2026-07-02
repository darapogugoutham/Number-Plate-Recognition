from datetime import datetime, timezone
import logging
import time
from pathlib import Path
from uuid import uuid4

from app.config import Settings
from app.core.exceptions import InvalidImageError


logger = logging.getLogger(__name__)


class RecognitionService:
    def __init__(self, settings: Settings):
        self.settings = settings

    def recognize(self, image_path: Path, crop_path: Path) -> dict:
        from app.cv.ocr_engine import run_tesseract_ocr
        from app.cv.plate_cropper import crop_plate, save_plate_crop
        from app.cv.plate_detector import detect_plate_opencv
        from app.cv.postprocessing import clean_plate_text, correct_common_ocr_errors, validate_plate
        from app.cv.preprocessing import load_image, preprocess_for_detection, preprocess_for_ocr

        start = time.perf_counter()
        created_at = datetime.now(timezone.utc)
        record = {
            "id": uuid4().hex,
            "plate_number": None,
            "raw_ocr_text": None,
            "cleaned_text": None,
            "status": "invalid_image",
            "message": "",
            "detection_confidence": 0.0,
            "ocr_confidence": 0.0,
            "bounding_box": None,
            "original_image_path": str(image_path),
            "plate_crop_path": None,
            "model_version": self.settings.model_version,
            "processing_time_ms": 0,
            "created_at": created_at,
        }

        try:
            image = load_image(image_path)
            edges = preprocess_for_detection(image)
        except InvalidImageError as exc:
            return self._finish(record, start, "invalid_image", str(exc))

        detection = detect_plate_opencv(image, edges)
        if detection is None:
            return self._finish(record, start, "no_plate_detected", "No license plate was detected in the uploaded image.")

        x, y, width, height = detection.bbox
        record["bounding_box"] = {"x": x, "y": y, "width": width, "height": height}
        record["detection_confidence"] = detection.confidence

        crop = crop_plate(image, detection.bbox)
        save_plate_crop(crop, crop_path)
        record["plate_crop_path"] = str(crop_path)

        try:
            ocr_ready = preprocess_for_ocr(crop)
            raw_text, ocr_confidence = run_tesseract_ocr(ocr_ready)
        except Exception as exc:  # Tesseract availability differs by machine.
            logger.exception("OCR failed")
            return self._finish(record, start, "ocr_failed", f"OCR failed: {exc}")

        cleaned = clean_plate_text(raw_text)
        corrected = correct_common_ocr_errors(cleaned)
        record["raw_ocr_text"] = raw_text
        record["cleaned_text"] = corrected
        record["plate_number"] = corrected if validate_plate(corrected) else cleaned or None
        record["ocr_confidence"] = ocr_confidence

        if not record["plate_number"]:
            return self._finish(record, start, "ocr_failed", "OCR did not return a valid plate candidate.")
        return self._finish(record, start, "success", "Plate recognized successfully.")

    def _finish(self, record: dict, start: float, status: str, message: str) -> dict:
        record["status"] = status
        record["message"] = message
        record["processing_time_ms"] = int((time.perf_counter() - start) * 1000)
        logger.info(
            "plate_recognition_completed",
            extra={
                "status": status,
                "plate_number": record.get("plate_number"),
                "processing_time_ms": record["processing_time_ms"],
            },
        )
        return record
