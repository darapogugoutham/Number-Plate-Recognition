from pathlib import Path

import cv2
import numpy as np

from app.core.exceptions import InvalidImageError


def load_image(path: str | Path) -> np.ndarray:
    image = cv2.imread(str(path))
    if image is None:
        raise InvalidImageError("The uploaded file could not be decoded as an image.")
    return image


def resize_image(image: np.ndarray, max_width: int = 1280) -> np.ndarray:
    height, width = image.shape[:2]
    if width <= max_width:
        return image
    scale = max_width / width
    return cv2.resize(image, (max_width, int(height * scale)), interpolation=cv2.INTER_AREA)


def preprocess_for_detection(image: np.ndarray) -> np.ndarray:
    resized = resize_image(image)
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    blur = cv2.bilateralFilter(gray, 11, 17, 17)
    return cv2.Canny(blur, 30, 200)


def preprocess_for_ocr(plate_crop: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(plate_crop, cv2.COLOR_BGR2GRAY)
    enlarged = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    denoised = cv2.fastNlMeansDenoising(enlarged, h=30)
    return cv2.adaptiveThreshold(
        denoised,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        2,
    )
