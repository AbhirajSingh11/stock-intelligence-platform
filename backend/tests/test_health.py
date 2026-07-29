"""Contract tests for the initial service endpoints."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_returns_service_navigation() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "name": "Stock Intelligence API",
        "docs": "/docs",
        "health": "/health",
    }


def test_health_reports_service_is_ready() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "stock-intelligence-backend",
    }

