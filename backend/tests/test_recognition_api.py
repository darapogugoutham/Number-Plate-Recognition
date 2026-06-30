from fastapi.testclient import TestClient

from app.main import create_app


def test_health_endpoint():
    client = TestClient(create_app())
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_invalid_upload_extension():
    client = TestClient(create_app())
    response = client.post(
        "/api/v1/recognize/image",
        files={"file": ("plate.txt", b"not-an-image", "text/plain")},
    )
    assert response.status_code == 400
