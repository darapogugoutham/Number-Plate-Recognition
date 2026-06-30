from fastapi import APIRouter, File, HTTPException, Request, UploadFile

from app.models.response_models import DetectionResponse


router = APIRouter(prefix="/recognize", tags=["recognition"])


@router.post("/image", response_model=DetectionResponse)
async def recognize_image(request: Request, file: UploadFile = File(...)) -> dict:
    try:
        image_path = await request.app.state.storage.save_upload(file)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except OverflowError as exc:
        raise HTTPException(status_code=413, detail=str(exc)) from exc

    crop_path = request.app.state.storage.crop_path_for(image_path)
    record = request.app.state.recognition.recognize(image_path, crop_path)
    request.app.state.history.save(record)
    return record
