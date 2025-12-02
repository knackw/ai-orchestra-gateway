from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "AI Legal Ops Gateway is running"}

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    # Check that new comprehensive health check response has the expected structure
    assert "status" in data
    assert "database" in data
    assert "uptime_seconds" in data
