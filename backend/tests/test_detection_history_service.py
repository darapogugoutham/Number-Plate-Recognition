from app.services.detection_history_service import DetectionHistoryService


def test_history_save_search_delete(tmp_path):
    service = DetectionHistoryService(tmp_path / "detections.json")
    service.save({"id": "1", "plate_number": "TXABC1234", "status": "success", "processing_time_ms": 20})

    assert service.get("1")["plate_number"] == "TXABC1234"
    assert len(service.list(plate="abc")) == 1
    assert service.metrics()["successful_detections"] == 1
    assert service.delete("1")
    assert service.get("1") is None
