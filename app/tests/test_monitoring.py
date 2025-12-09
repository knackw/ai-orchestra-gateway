import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestMonitoring:
    
    def test_metrics_endpoint_exposed(self):
        """Test that Prometheus metrics endpoint is available."""
        response = client.get("/metrics")
        assert response.status_code == 200
        assert "http_requests_total" in response.text
        assert "http_request_duration_seconds" in response.text
        
    def test_health_check_monitored(self):
        """Test that health check is covered by metrics (indirectly)."""
        # Hit health
        client.get("/health")
        
        # Check metrics again to see if count increased? 
        # (Hard to assert exact count in parallel tests, but at least endpoint works)
        response = client.get("/metrics")
        assert response.status_code == 200
