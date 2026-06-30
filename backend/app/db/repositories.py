from datetime import datetime

from app.config import Settings
from app.services.detection_history_service import DetectionHistoryService


class MongoDetectionHistoryService:
    def __init__(self, settings: Settings):
        from pymongo import MongoClient

        self.client = MongoClient(settings.mongodb_url)
        self.collection = self.client[settings.mongodb_database][settings.mongodb_collection]
        self.collection.create_index("plate_number")
        self.collection.create_index("created_at")
        self.collection.create_index("status")

    def list(self, plate: str | None = None, status: str | None = None) -> list[dict]:
        query = {}
        if plate:
            query["plate_number"] = {"$regex": plate.upper(), "$options": "i"}
        if status:
            query["status"] = status
        return [self._clean(record) for record in self.collection.find(query).sort("created_at", -1)]

    def get(self, detection_id: str) -> dict | None:
        record = self.collection.find_one({"id": detection_id})
        return self._clean(record) if record else None

    def save(self, record: dict) -> dict:
        self.collection.insert_one(record.copy())
        return record

    def delete(self, detection_id: str) -> bool:
        return self.collection.delete_one({"id": detection_id}).deleted_count == 1

    def metrics(self) -> dict:
        records = list(self.collection.find({}, {"processing_time_ms": 1, "status": 1}))
        total = len(records)
        successes = len([record for record in records if record.get("status") == "success"])
        avg = sum(record.get("processing_time_ms", 0) for record in records) / total if total else 0
        return {
            "total_requests": total,
            "successful_detections": successes,
            "failed_detections": total - successes,
            "average_processing_time_ms": round(avg, 2),
        }

    def _clean(self, record: dict) -> dict:
        record.pop("_id", None)
        if isinstance(record.get("created_at"), datetime):
            record["created_at"] = record["created_at"].isoformat()
        return record


def create_history_service(settings: Settings):
    if settings.mongodb_url:
        return MongoDetectionHistoryService(settings)
    return DetectionHistoryService(settings.history_file)


__all__ = ["DetectionHistoryService", "MongoDetectionHistoryService", "create_history_service"]
