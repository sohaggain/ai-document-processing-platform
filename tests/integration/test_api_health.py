"""Integration test for the health endpoint (no auth, no DB dependency)."""
from fastapi.testclient import TestClient

from src.main import app


def test_health_check():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
