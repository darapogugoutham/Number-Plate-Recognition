from fastapi import APIRouter, Request

from app.models.response_models import HealthResponse, MetricsResponse


router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health(request: Request) -> HealthResponse:
    return HealthResponse(status="ok", app=request.app.state.settings.app_name)


@router.get("/metrics", response_model=MetricsResponse)
def metrics(request: Request) -> dict:
    return request.app.state.history.metrics()
