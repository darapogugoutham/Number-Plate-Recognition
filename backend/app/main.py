from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes_detections import router as detections_router
from app.api.routes_health import router as health_router
from app.api.routes_recognition import router as recognition_router
from app.config import get_settings
from app.core.logging_config import configure_logging
from app.db.repositories import create_history_service
from app.services.image_storage_service import ImageStorageService
from app.services.recognition_service import RecognitionService


def create_app() -> FastAPI:
    configure_logging()
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version="0.1.0")
    app.state.settings = settings
    app.state.storage = ImageStorageService(settings)
    app.state.history = create_history_service(settings)
    app.state.recognition = RecognitionService(settings)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")
    app.include_router(health_router, prefix=settings.api_prefix)
    app.include_router(recognition_router, prefix=settings.api_prefix)
    app.include_router(detections_router, prefix=settings.api_prefix)
    return app


app = create_app()
