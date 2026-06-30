from fastapi import APIRouter, HTTPException, Query, Request

router = APIRouter(prefix="/detections", tags=["detections"])


@router.get("")
def list_detections(
    request: Request,
    plate: str | None = Query(default=None),
    status: str | None = Query(default=None),
) -> list[dict]:
    return request.app.state.history.list(plate=plate, status=status)


@router.get("/search")
def search_detections(request: Request, plate: str = Query(min_length=1)) -> list[dict]:
    return request.app.state.history.list(plate=plate)


@router.get("/{detection_id}")
def get_detection(request: Request, detection_id: str) -> dict:
    record = request.app.state.history.get(detection_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Detection not found")
    return record


@router.delete("/{detection_id}")
def delete_detection(request: Request, detection_id: str) -> dict:
    if not request.app.state.history.delete(detection_id):
        raise HTTPException(status_code=404, detail="Detection not found")
    return {"deleted": True, "id": detection_id}
