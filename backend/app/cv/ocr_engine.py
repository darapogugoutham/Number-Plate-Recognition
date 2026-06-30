import re

import cv2
import numpy as np
import pytesseract


OCR_CONFIG = "--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


def run_tesseract_ocr(plate_image: np.ndarray) -> tuple[str, float]:
    data = pytesseract.image_to_data(
        plate_image,
        config=OCR_CONFIG,
        output_type=pytesseract.Output.DICT,
    )
    text = " ".join(part for part in data.get("text", []) if part.strip())
    confidences = [
        float(conf)
        for conf in data.get("conf", [])
        if re.fullmatch(r"-?\d+(\.\d+)?", str(conf)) and float(conf) >= 0
    ]
    confidence = (sum(confidences) / len(confidences) / 100) if confidences else 0.0

    if not text.strip():
        text = pytesseract.image_to_string(plate_image, config=OCR_CONFIG)
    return text.strip(), round(confidence, 2)


def run_easyocr(_plate_image: np.ndarray) -> tuple[str, float]:
    raise NotImplementedError("EasyOCR is an optional upgrade path and is not enabled by default.")
