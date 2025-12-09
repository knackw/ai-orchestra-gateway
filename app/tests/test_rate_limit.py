
import pytest
from fastapi import Request
from fastapi.testclient import TestClient
from app.main import app
from app.core.rate_limit import limiter

client = TestClient(app)

# Helper route with strict limit
@app.get("/test-limit")
@limiter.limit("1/minute")
async def limited_route(request: Request):
    return {"message": "ok"}

class TestRateLimit:
    
    def test_rate_limit_integration(self):
        """
        Verify that hitting the limit triggers 429.
        """
        # First request: OK
        res1 = client.get("/test-limit")
        assert res1.status_code == 200
        
        # Second request: Blocked
        res2 = client.get("/test-limit")
        assert res2.status_code == 429
        data = res2.json()
        assert "Rate limit exceeded" in data["detail"]
        
    def test_get_project_key_logic(self):
        from app.core.rate_limit import get_project_key
        # Simple unit test for the key extraction function
        req = Request(scope={"type": "http", "headers": [(b"x-license-key", b"my-key")]})
        assert get_project_key(req) == "my-key"
