from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.config import Settings


class ImageStorageService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.settings.original_dir.mkdir(parents=True, exist_ok=True)
        self.settings.crop_dir.mkdir(parents=True, exist_ok=True)

    async def save_upload(self, file: UploadFile) -> Path:
        suffix = Path(file.filename or "").suffix.lower()
        if suffix not in self.settings.allowed_extensions:
            allowed = ", ".join(sorted(self.settings.allowed_extensions))
            raise ValueError(f"Invalid file type. Allowed extensions: {allowed}")

        content = await file.read()
        if len(content) > self.settings.max_upload_size_bytes:
            raise OverflowError("Uploaded image exceeds the configured size limit.")

        output_path = self.settings.original_dir / f"{uuid4().hex}{suffix}"
        output_path.write_bytes(content)
        return output_path

    def crop_path_for(self, original_path: Path) -> Path:
        return self.settings.crop_dir / f"{original_path.stem}_plate.jpg"
