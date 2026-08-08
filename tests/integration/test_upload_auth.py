"""Integration tests for API-key auth enforcement on protected endpoints."""
from fastapi.testclient import TestClient

from src.main import app


def test_upload_without_api_key_rejected():
    client = TestClient(app)
    response = client.post("/documents/upload", files={"file": ("test.pdf", b"%PDF-1.4 fake", "application/pdf")})
    assert response.status_code == 422 or response.status_code == 401


def test_get_document_without_api_key_rejected():
    client = TestClient(app)
    response = client.get("/documents/some-id")
    assert response.status_code in (401, 422)
