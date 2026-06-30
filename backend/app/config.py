from functools import lru_cache
from pathlib import Path
import os


BACKEND_DIR = Path(__file__).resolve().parents[1]


class Settings:
    app_name = "Number Plate Recognition System"
    api_prefix = "/api/v1"
    max_upload_size_bytes = int(os.getenv("MAX_UPLOAD_SIZE_BYTES", str(8 * 1024 * 1024)))
    allowed_extensions = {".jpg", ".jpeg", ".png"}
    upload_dir = Path(os.getenv("UPLOAD_DIR", str(BACKEND_DIR / "uploads")))
    original_dir = upload_dir / "original"
    crop_dir = upload_dir / "crops"
    history_file = Path(os.getenv("HISTORY_FILE", str(upload_dir / "detections.json")))
    mongodb_url = os.getenv("MONGODB_URL", "")
    mongodb_database = os.getenv("MONGODB_DATABASE", "anpr")
    mongodb_collection = os.getenv("MONGODB_COLLECTION", "detections")
    model_version = os.getenv("MODEL_VERSION", "opencv-contour-v1")


@lru_cache
def get_settings() -> Settings:
    return Settings()
