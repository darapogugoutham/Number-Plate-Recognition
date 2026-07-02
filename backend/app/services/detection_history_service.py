from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
from threading import Lock


class DetectionHistoryService:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()

    def list(self, plate: str | None = None, status: str | None = None) -> list[dict]:
        records = self._read()
        if plate:
            records = [record for record in records if plate.upper() in (record.get("plate_number") or "")]
        if status:
            records = [record for record in records if record.get("status") == status]
        return sorted(records, key=lambda record: record.get("created_at", ""), reverse=True)

    def get(self, detection_id: str) -> dict | None:
        return next((record for record in self._read() if record.get("id") == detection_id), None)

    def save(self, record: dict) -> dict:
        with self._lock:
            records = self._read()
            records.append(record)
            self.path.write_text(json.dumps(records, indent=2, default=_json_default), encoding="utf-8")
        return record

    def delete(self, detection_id: str) -> bool:
        with self._lock:
            records = self._read()
            kept = [record for record in records if record.get("id") != detection_id]
            if len(kept) == len(records):
                return False
            self.path.write_text(json.dumps(kept, indent=2, default=_json_default), encoding="utf-8")
            return True

    def metrics(self) -> dict:
        records = self._read()
        total = len(records)
        successes = len([record for record in records if record.get("status") == "success"])
        avg = sum(record.get("processing_time_ms", 0) for record in records) / total if total else 0
        return {
            "total_requests": total,
            "successful_detections": successes,
            "failed_detections": total - successes,
            "average_processing_time_ms": round(avg, 2),
        }

    def _read(self) -> list[dict]:
        if not self.path.exists():
            return []
        return json.loads(self.path.read_text(encoding="utf-8") or "[]")


def _json_default(value):
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)
