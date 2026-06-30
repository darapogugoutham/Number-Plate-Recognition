from dataclasses import dataclass

import cv2
import numpy as np


@dataclass(frozen=True)
class PlateDetection:
    bbox: tuple[int, int, int, int]
    confidence: float


def detect_plate_opencv(image: np.ndarray, edges: np.ndarray) -> PlateDetection | None:
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    candidates: list[tuple[float, tuple[int, int, int, int]]] = []
    image_area = image.shape[0] * image.shape[1]

    for contour in sorted(contours, key=cv2.contourArea, reverse=True)[:40]:
        x, y, w, h = cv2.boundingRect(contour)
        if h == 0:
            continue
        aspect_ratio = w / h
        area = w * h
        area_ratio = area / image_area
        if 2.0 <= aspect_ratio <= 6.5 and 0.002 <= area_ratio <= 0.20 and w >= 60 and h >= 15:
            rectangularity = min(1.0, cv2.contourArea(contour) / float(area))
            aspect_score = 1.0 - min(abs(aspect_ratio - 4.0) / 4.0, 1.0)
            score = 0.45 + (0.35 * aspect_score) + (0.20 * rectangularity)
            candidates.append((score, (x, y, w, h)))

    if not candidates:
        return None
    score, bbox = max(candidates, key=lambda candidate: candidate[0])
    return PlateDetection(bbox=bbox, confidence=round(float(score), 2))
