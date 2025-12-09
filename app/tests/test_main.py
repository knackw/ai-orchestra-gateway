from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_read_main():
    """Test landing page returns HTML."""
    response = client.get("/")
    assert response.status_code == 200
    # Landing page now returns HTML
    assert "text/html" in response.headers["content-type"]


def test_health_check():
    """Test health endpoint returns JSON with expected structure."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    # Check that new comprehensive health check response has the expected structure
    assert "status" in data
    assert "database" in data
    assert "uptime_seconds" in data


def test_privacy_page():
    """Test privacy page returns HTML."""
    response = client.get("/privacy")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_terms_page():
    """Test terms page returns HTML."""
    response = client.get("/terms")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
