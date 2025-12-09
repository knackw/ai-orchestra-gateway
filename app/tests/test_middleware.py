import pytest
import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestMiddleware:
    
    def test_request_id_header_present(self):
        """Test that X-Request-ID header is added to responses."""
        response = client.get("/health")
        assert response.status_code == 200
        
        request_id = response.headers.get("X-Request-ID")
        assert request_id is not None
        assert len(request_id) > 0
        
        # Verify it's a valid UUID
        try:
            val = uuid.UUID(request_id, version=4)
        except ValueError:
            pytest.fail(f"X-Request-ID is not a valid UUID: {request_id}")

    def test_request_id_unique(self):
        """Test that request IDs are unique per request."""
        res1 = client.get("/health")
        res2 = client.get("/health")
        
        id1 = res1.headers.get("X-Request-ID")
        id2 = res2.headers.get("X-Request-ID")
        
        assert id1 != id2
