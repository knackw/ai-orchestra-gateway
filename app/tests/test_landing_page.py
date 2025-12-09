
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestLandingPage:
    
    def test_rendering_landing_page(self):
        """Test suitable HTML rendering of the landing page."""
        response = client.get("/")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "AI Legal Ops" in response.text
        assert "Secure AI Orchestration" in response.text
        
    def test_cookie_banner_present(self):
        """Test that the cookie banner HTML is present in the response."""
        response = client.get("/")
        
        # Check for banner container
        assert 'id="cookie-banner"' in response.text
        
        # Check for buttons
        assert 'id="btn-accept"' in response.text
        assert 'id="btn-essential"' in response.text


class TestLegalPages:
    
    def test_privacy_policy_page(self):
        """Test that /privacy returns the privacy policy."""
        response = client.get("/privacy")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "Datenschutzerklärung" in response.text
        assert "DSGVO" in response.text
        
    def test_terms_of_service_page(self):
        """Test that /terms returns the terms of service."""
        response = client.get("/terms")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "Allgemeine Geschäftsbedingungen" in response.text

