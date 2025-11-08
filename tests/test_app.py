"""
Test suite for FastAPI application
"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_metrics_endpoint():
    """Test that metrics endpoint returns 200 and Prometheus format"""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers.get("content-type", "")
    # Check for Prometheus metric format
    assert "http_requests_total" in response.text or "# HELP" in response.text


def test_health_endpoint():
    """Test that health endpoint returns 200 and healthy status"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data


def test_metrics_content_type():
    """Test that metrics endpoint uses correct content type"""
    response = client.get("/metrics")
    assert response.status_code == 200
    # Should use Prometheus content type
    content_type = response.headers.get("content-type", "")
    assert "text/plain" in content_type or "version=0.0.4" in content_type

