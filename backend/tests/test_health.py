"""Tests for health check endpoint."""

from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """Test health check endpoint returns healthy status."""
    response = client.get("/api/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "0.1.0"


def test_health_check_alternate_path(client: TestClient):
    """Test health check endpoint with trailing slash."""
    response = client.get("/api/health/")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_root_endpoint(client: TestClient):
    """Test root endpoint returns application info."""
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "brand_engineer"
    assert data["version"] == "0.1.0"
    assert data["docs"] == "/docs"
