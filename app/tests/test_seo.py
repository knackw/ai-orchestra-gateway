"""
Unit tests for SEO API endpoints.

Tests:
- robots.txt generation
- sitemap.xml generation
- Meta information
- Structured data
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.api.v1.seo import router, SEO_CONFIG
from fastapi import FastAPI


@pytest.fixture
def client():
    """Create test client."""
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


class TestRobotsTxt:
    """Tests for robots.txt endpoint."""

    def test_returns_plain_text(self, client):
        """Should return plain text content type."""
        response = client.get("/robots.txt")
        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]

    def test_contains_user_agent(self, client):
        """Should contain User-agent directive."""
        response = client.get("/robots.txt")
        assert "User-agent:" in response.text

    def test_contains_sitemap(self, client):
        """Should contain sitemap reference."""
        response = client.get("/robots.txt")
        assert "Sitemap:" in response.text

    def test_disallows_admin(self, client):
        """Should disallow admin endpoints."""
        response = client.get("/robots.txt")
        assert "Disallow: /admin/" in response.text

    def test_disallows_api(self, client):
        """Should disallow API endpoints."""
        response = client.get("/robots.txt")
        assert "Disallow: /api/" in response.text

    def test_allows_docs(self, client):
        """Should allow docs page."""
        response = client.get("/robots.txt")
        assert "Allow: /docs" in response.text


class TestSitemapXml:
    """Tests for sitemap.xml endpoint."""

    def test_returns_xml(self, client):
        """Should return XML content type."""
        response = client.get("/sitemap.xml")
        assert response.status_code == 200
        assert "application/xml" in response.headers["content-type"]

    def test_valid_xml_structure(self, client):
        """Should return valid XML structure."""
        response = client.get("/sitemap.xml")
        assert '<?xml version="1.0"' in response.text
        assert "<urlset" in response.text
        assert "</urlset>" in response.text

    def test_contains_homepage(self, client):
        """Should contain homepage URL."""
        response = client.get("/sitemap.xml")
        assert "<loc>" in response.text

    def test_contains_priority(self, client):
        """Should contain priority elements."""
        response = client.get("/sitemap.xml")
        assert "<priority>" in response.text

    def test_contains_changefreq(self, client):
        """Should contain changefreq elements."""
        response = client.get("/sitemap.xml")
        assert "<changefreq>" in response.text

    def test_contains_lastmod(self, client):
        """Should contain lastmod elements."""
        response = client.get("/sitemap.xml")
        assert "<lastmod>" in response.text


class TestMetaInfo:
    """Tests for meta information endpoint."""

    def test_default_meta(self, client):
        """Should return default meta for homepage."""
        response = client.get("/meta")
        assert response.status_code == 200
        data = response.json()

        assert "title" in data
        assert "meta" in data
        assert "openGraph" in data
        assert "twitter" in data
        assert "canonical" in data

    def test_meta_for_docs(self, client):
        """Should return specific meta for docs page."""
        response = client.get("/meta?path=/docs")
        data = response.json()

        assert "Documentation" in data["title"]
        assert "documentation" in data["meta"]["description"].lower()

    def test_meta_for_pricing(self, client):
        """Should return specific meta for pricing page."""
        response = client.get("/meta?path=/pricing")
        data = response.json()

        assert "Pricing" in data["title"]

    def test_meta_for_developers(self, client):
        """Should return specific meta for developers page."""
        response = client.get("/meta?path=/developers")
        data = response.json()

        assert "Developer" in data["title"]

    def test_meta_description(self, client):
        """Should include meta description."""
        response = client.get("/meta")
        data = response.json()

        assert "description" in data["meta"]
        assert len(data["meta"]["description"]) > 10

    def test_meta_keywords(self, client):
        """Should include meta keywords."""
        response = client.get("/meta")
        data = response.json()

        assert "keywords" in data["meta"]

    def test_open_graph_data(self, client):
        """Should include Open Graph data."""
        response = client.get("/meta")
        data = response.json()

        og = data["openGraph"]
        assert "type" in og
        assert "site_name" in og
        assert "title" in og
        assert "description" in og
        assert "url" in og
        assert "image" in og

    def test_twitter_card_data(self, client):
        """Should include Twitter card data."""
        response = client.get("/meta")
        data = response.json()

        twitter = data["twitter"]
        assert "card" in twitter
        assert "site" in twitter
        assert "title" in twitter
        assert "description" in twitter

    def test_canonical_url(self, client):
        """Should include canonical URL."""
        response = client.get("/meta?path=/docs")
        data = response.json()

        assert "/docs" in data["canonical"]

    def test_language_parameter(self, client):
        """Should respect language parameter."""
        response = client.get("/meta?lang=de")
        data = response.json()

        assert "de" in data["openGraph"]["locale"]

    def test_unknown_path_uses_defaults(self, client):
        """Should use defaults for unknown paths."""
        response = client.get("/meta?path=/unknown-page")
        data = response.json()

        assert "title" in data
        assert "AI Orchestra Gateway" in data["title"]


class TestStructuredData:
    """Tests for structured data endpoint."""

    def test_organization_data(self, client):
        """Should return organization structured data."""
        response = client.get("/structured-data?page_type=organization")
        assert response.status_code == 200
        data = response.json()

        assert data["@type"] == "Organization"
        assert "@context" in data
        assert "name" in data
        assert "url" in data
        assert "contactPoint" in data

    def test_software_data(self, client):
        """Should return software application structured data."""
        response = client.get("/structured-data?page_type=software")
        data = response.json()

        assert data["@type"] == "SoftwareApplication"
        assert "applicationCategory" in data
        assert "offers" in data
        assert "featureList" in data

    def test_faq_data(self, client):
        """Should return FAQ structured data."""
        response = client.get("/structured-data?page_type=faq")
        data = response.json()

        assert data["@type"] == "FAQPage"
        assert "mainEntity" in data
        assert len(data["mainEntity"]) > 0

        # Check FAQ structure
        question = data["mainEntity"][0]
        assert question["@type"] == "Question"
        assert "name" in question
        assert "acceptedAnswer" in question

    def test_breadcrumb_data(self, client):
        """Should return breadcrumb structured data."""
        response = client.get("/structured-data?page_type=breadcrumb")
        data = response.json()

        assert data["@type"] == "BreadcrumbList"
        assert "itemListElement" in data

    def test_default_webpage_data(self, client):
        """Should return generic WebPage for unknown type."""
        response = client.get("/structured-data?page_type=unknown")
        data = response.json()

        assert data["@type"] == "WebPage"

    def test_structured_data_has_context(self, client):
        """All structured data should have @context."""
        for page_type in ["organization", "software", "faq", "breadcrumb"]:
            response = client.get(f"/structured-data?page_type={page_type}")
            data = response.json()
            assert data["@context"] == "https://schema.org"


class TestSecurityTxt:
    """Tests for security.txt endpoint."""

    def test_returns_plain_text(self, client):
        """Should return plain text content type."""
        response = client.get("/security.txt")
        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]

    def test_contains_contact(self, client):
        """Should contain contact information."""
        response = client.get("/security.txt")
        assert "Contact:" in response.text

    def test_contains_expires(self, client):
        """Should contain expiration date."""
        response = client.get("/security.txt")
        assert "Expires:" in response.text

    def test_contains_preferred_languages(self, client):
        """Should contain preferred languages."""
        response = client.get("/security.txt")
        assert "Preferred-Languages:" in response.text


class TestHumansTxt:
    """Tests for humans.txt endpoint."""

    def test_returns_plain_text(self, client):
        """Should return plain text content type."""
        response = client.get("/humans.txt")
        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]

    def test_contains_team_section(self, client):
        """Should contain TEAM section."""
        response = client.get("/humans.txt")
        assert "TEAM" in response.text

    def test_contains_site_section(self, client):
        """Should contain SITE section."""
        response = client.get("/humans.txt")
        assert "SITE" in response.text

    def test_contains_thanks_section(self, client):
        """Should contain THANKS section."""
        response = client.get("/humans.txt")
        assert "THANKS" in response.text


class TestSEOConfig:
    """Tests for SEO configuration."""

    def test_config_has_site_name(self):
        """Config should have site name."""
        assert "site_name" in SEO_CONFIG
        assert len(SEO_CONFIG["site_name"]) > 0

    def test_config_has_site_description(self):
        """Config should have site description."""
        assert "site_description" in SEO_CONFIG
        assert len(SEO_CONFIG["site_description"]) > 0

    def test_config_has_site_url(self):
        """Config should have site URL."""
        assert "site_url" in SEO_CONFIG
        assert SEO_CONFIG["site_url"].startswith("http")

    def test_config_has_language(self):
        """Config should have default language."""
        assert "site_language" in SEO_CONFIG

    def test_config_has_contact(self):
        """Config should have contact email."""
        assert "contact_email" in SEO_CONFIG
        assert "@" in SEO_CONFIG["contact_email"]


class TestLlmsTxt:
    """Tests for llms.txt endpoint."""

    def test_returns_plain_text(self, client):
        """Should return plain text content type."""
        response = client.get("/llms.txt")
        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]

    def test_contains_site_name(self, client):
        """Should contain site name."""
        response = client.get("/llms.txt")
        assert "AI Orchestra Gateway" in response.text

    def test_contains_overview_section(self, client):
        """Should contain overview section."""
        response = client.get("/llms.txt")
        assert "## Overview" in response.text

    def test_contains_features_section(self, client):
        """Should contain features section."""
        response = client.get("/llms.txt")
        assert "## Core Features" in response.text
        assert "Privacy Shield" in response.text

    def test_contains_api_endpoints(self, client):
        """Should contain API endpoints section."""
        response = client.get("/llms.txt")
        assert "## API Endpoints" in response.text
        assert "/v1/generate" in response.text

    def test_contains_authentication_info(self, client):
        """Should contain authentication information."""
        response = client.get("/llms.txt")
        assert "## Authentication" in response.text
        assert "X-License-Key" in response.text

    def test_contains_documentation_links(self, client):
        """Should contain documentation links."""
        response = client.get("/llms.txt")
        assert "## Documentation" in response.text
        assert "/docs" in response.text
        assert "/developers" in response.text

    def test_contains_contact_info(self, client):
        """Should contain contact information."""
        response = client.get("/llms.txt")
        assert "## Contact" in response.text


class TestMetaForAllPages:
    """Tests for meta information across all defined pages."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        app = FastAPI()
        app.include_router(router)
        return TestClient(app)

    @pytest.mark.parametrize("path", [
        "/",
        "/docs",
        "/developers",
        "/pricing",
        "/changelog",
        "/help",
        "/status",
        "/blog",
        "/contact",
    ])
    def test_meta_for_page(self, client, path):
        """Each defined page should have valid meta."""
        response = client.get(f"/meta?path={path}")
        assert response.status_code == 200

        data = response.json()
        assert "title" in data
        assert len(data["title"]) > 0
        assert "meta" in data
        assert "description" in data["meta"]
