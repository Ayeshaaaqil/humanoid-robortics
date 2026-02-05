import pytest
from fastapi.testclient import TestClient
from backend.src.api.main import app


def test_read_root():
    """
    Test the root endpoint of the API.
    """
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "RAG Chatbot API" in response.json()["message"]
    assert "status" in response.json()
    assert response.json()["status"] == "running"


def test_chat_endpoint_exists():
    """
    Test that the chat endpoint exists.
    """
    client = TestClient(app)
    # This should return 422 (validation error) because we didn't provide the required body
    # rather than 404 (not found), which confirms the endpoint exists
    response = client.post("/api/v1/chat")
    assert response.status_code == 422


def test_ingest_endpoint_exists():
    """
    Test that the ingest endpoint exists.
    """
    client = TestClient(app)
    # This should return 422 (validation error) because we didn't provide the required body
    # rather than 404 (not found), which confirms the endpoint exists
    response = client.post("/api/v1/ingest")
    assert response.status_code == 422