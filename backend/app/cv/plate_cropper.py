from pathlib import Path

import cv2
import numpy as np


def crop_plate(image: np.ndarray, bbox: tuple[int, int, int, int], padding: int = 6) -> np.ndarray:
    x, y, w, h = bbox
    img_h, img_w = image.shape[:2]
    left = max(0, x - padding)
    top = max(0, y - padding)
    right = min(img_w, x + w + padding)
    bottom = min(img_h, y + h + padding)
    return image[top:bottom, left:right]


def save_plate_crop(crop: np.ndarray, output_path: str | Path) -> None:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output), crop)
