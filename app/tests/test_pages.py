"""
Unit tests for Pages Content API.

Tests:
- Documentation endpoint
- Developer portal endpoint
- Changelog endpoint
- Contact endpoint
- Help center endpoint
- System status endpoint
- Blog endpoint
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.api.v1.pages import router


@pytest.fixture
def client():
    """Create test client."""
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


class TestDocumentation:
    """Tests for documentation endpoint."""

    def test_get_documentation(self, client):
        """Should return documentation content."""
        response = client.get("/documentation")
        assert response.status_code == 200

        data = response.json()
        assert "categories" in data
        assert "last_updated" in data
        assert "version" in data

    def test_docs_has_categories(self, client):
        """Should have multiple documentation categories."""
        response = client.get("/documentation")
        data = response.json()

        assert len(data["categories"]) > 0

    def test_docs_category_structure(self, client):
        """Each category should have proper structure."""
        response = client.get("/documentation")
        data = response.json()

        for category in data["categories"]:
            assert "id" in category
            assert "title" in category
            assert "description" in category
            assert "icon" in category
            assert "sections" in category

    def test_docs_section_structure(self, client):
        """Each section should have proper structure."""
        response = client.get("/documentation")
        data = response.json()

        for category in data["categories"]:
            for section in category["sections"]:
                assert "id" in section
                assert "title" in section
                assert "content" in section

    def test_docs_has_code_examples(self, client):
        """Some sections should have code examples."""
        response = client.get("/documentation")
        data = response.json()

        has_code = False
        for category in data["categories"]:
            for section in category["sections"]:
                if section.get("code_example"):
                    has_code = True
                    break

        assert has_code

    def test_docs_language_parameter(self, client):
        """Should accept language parameter."""
        response = client.get("/documentation?lang=de")
        assert response.status_code == 200


class TestDeveloperPortal:
    """Tests for developer portal endpoint."""

    def test_get_developer_portal(self, client):
        """Should return developer portal content."""
        response = client.get("/developers")
        assert response.status_code == 200

        data = response.json()
        assert "sdks" in data
        assert "code_examples" in data
        assert "api_reference" in data
        assert "resources" in data

    def test_sdks_structure(self, client):
        """SDKs should have proper structure."""
        response = client.get("/developers")
        data = response.json()

        for sdk in data["sdks"]:
            assert "name" in sdk
            assert "language" in sdk
            assert "version" in sdk
            assert "install" in sdk

    def test_code_examples_structure(self, client):
        """Code examples should have proper structure."""
        response = client.get("/developers")
        data = response.json()

        for example in data["code_examples"]:
            assert "title" in example
            assert "description" in example
            assert "language" in example
            assert "code" in example

    def test_api_reference_has_openapi(self, client):
        """API reference should include OpenAPI URL."""
        response = client.get("/developers")
        data = response.json()

        assert "openapi_url" in data["api_reference"]


class TestChangelog:
    """Tests for changelog endpoint."""

    def test_get_changelog(self, client):
        """Should return changelog entries."""
        response = client.get("/changelog")
        assert response.status_code == 200

        data = response.json()
        assert "entries" in data
        assert "total" in data
        assert "has_more" in data

    def test_changelog_entry_structure(self, client):
        """Entries should have proper structure."""
        response = client.get("/changelog")
        data = response.json()

        for entry in data["entries"]:
            assert "version" in entry
            assert "date" in entry
            assert "title" in entry
            assert "description" in entry
            assert "changes" in entry

    def test_changelog_change_structure(self, client):
        """Changes should have type and text."""
        response = client.get("/changelog")
        data = response.json()

        for entry in data["entries"]:
            for change in entry["changes"]:
                assert "type" in change
                assert "text" in change

    def test_changelog_pagination_limit(self, client):
        """Should respect limit parameter."""
        response = client.get("/changelog?limit=2")
        data = response.json()

        assert len(data["entries"]) <= 2

    def test_changelog_pagination_offset(self, client):
        """Should respect offset parameter."""
        response1 = client.get("/changelog?limit=2&offset=0")
        response2 = client.get("/changelog?limit=2&offset=2")

        data1 = response1.json()
        data2 = response2.json()

        # Should be different entries (if enough exist)
        if data1["total"] > 2:
            assert data1["entries"][0] != data2["entries"][0] if data2["entries"] else True


class TestContact:
    """Tests for contact endpoint."""

    def test_get_contact_info(self, client):
        """Should return contact information."""
        response = client.get("/contact")
        assert response.status_code == 200

        data = response.json()
        assert "email" in data
        assert "support_email" in data
        assert "address" in data
        assert "social" in data
        assert "form_fields" in data

    def test_address_structure(self, client):
        """Address should have proper structure."""
        response = client.get("/contact")
        data = response.json()

        address = data["address"]
        assert "company" in address
        assert "city" in address
        assert "country" in address

    def test_form_fields_structure(self, client):
        """Form fields should have proper structure."""
        response = client.get("/contact")
        data = response.json()

        for field in data["form_fields"]:
            assert "name" in field
            assert "label" in field
            assert "type" in field
            assert "required" in field

    def test_social_links(self, client):
        """Should have social media links."""
        response = client.get("/contact")
        data = response.json()

        social = data["social"]
        assert len(social) > 0


class TestHelpCenter:
    """Tests for help center endpoint."""

    def test_get_help_center(self, client):
        """Should return help center content."""
        response = client.get("/help")
        assert response.status_code == 200

        data = response.json()
        assert "faqs" in data
        assert "categories" in data
        assert "total" in data

    def test_faq_structure(self, client):
        """FAQs should have proper structure."""
        response = client.get("/help")
        data = response.json()

        for faq in data["faqs"]:
            assert "id" in faq
            assert "question" in faq
            assert "answer" in faq
            assert "category" in faq

    def test_category_filter(self, client):
        """Should filter by category."""
        response = client.get("/help?category=billing")
        data = response.json()

        for faq in data["faqs"]:
            assert faq["category"] == "billing"

    def test_search_filter(self, client):
        """Should filter by search term."""
        response = client.get("/help?search=privacy")
        data = response.json()

        # All results should contain "privacy"
        for faq in data["faqs"]:
            assert "privacy" in faq["question"].lower() or "privacy" in faq["answer"].lower()

    def test_categories_structure(self, client):
        """Categories should have proper structure."""
        response = client.get("/help")
        data = response.json()

        for category in data["categories"]:
            assert "id" in category
            assert "name" in category
            assert "icon" in category


class TestSystemStatus:
    """Tests for system status endpoint."""

    def test_get_system_status(self, client):
        """Should return system status."""
        response = client.get("/status")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert "components" in data
        assert "incidents" in data
        assert "last_updated" in data

    def test_component_structure(self, client):
        """Components should have proper structure."""
        response = client.get("/status")
        data = response.json()

        for component in data["components"]:
            assert "name" in component
            assert "status" in component
            assert "uptime_percent" in component

    def test_overall_status_values(self, client):
        """Overall status should be valid value."""
        response = client.get("/status")
        data = response.json()

        valid_statuses = ["operational", "degraded", "outage", "maintenance"]
        assert data["status"] in valid_statuses

    def test_component_status_values(self, client):
        """Component status should be valid value."""
        response = client.get("/status")
        data = response.json()

        valid_statuses = ["operational", "degraded", "outage", "maintenance"]
        for component in data["components"]:
            assert component["status"] in valid_statuses

    def test_incidents_structure(self, client):
        """Incidents should have proper structure."""
        response = client.get("/status")
        data = response.json()

        for incident in data["incidents"]:
            assert "id" in incident
            assert "title" in incident
            assert "status" in incident


class TestBlog:
    """Tests for blog endpoint."""

    def test_get_blog_posts(self, client):
        """Should return blog posts."""
        response = client.get("/blog")
        assert response.status_code == 200

        data = response.json()
        assert "posts" in data
        assert "total" in data
        assert "has_more" in data
        assert "tags" in data

    def test_blog_post_structure(self, client):
        """Blog posts should have proper structure."""
        response = client.get("/blog")
        data = response.json()

        for post in data["posts"]:
            assert "id" in post
            assert "slug" in post
            assert "title" in post
            assert "excerpt" in post
            assert "author" in post
            assert "published_at" in post
            assert "tags" in post
            assert "read_time_minutes" in post

    def test_blog_tag_filter(self, client):
        """Should filter by tag."""
        response = client.get("/blog?tag=privacy")
        data = response.json()

        for post in data["posts"]:
            assert "privacy" in post["tags"]

    def test_blog_search(self, client):
        """Should search blog posts."""
        response = client.get("/blog?search=gateway")
        data = response.json()

        for post in data["posts"]:
            assert "gateway" in post["title"].lower() or "gateway" in post["excerpt"].lower()

    def test_blog_pagination(self, client):
        """Should paginate blog posts."""
        response = client.get("/blog?limit=2")
        data = response.json()

        assert len(data["posts"]) <= 2

    def test_get_single_post(self, client):
        """Should return single blog post."""
        response = client.get("/blog/introducing-ai-orchestra-gateway")
        assert response.status_code == 200

        data = response.json()
        assert "title" in data
        assert "content" in data
        assert "author" in data

    def test_get_single_post_not_found(self, client):
        """Should return 404 for non-existent post."""
        response = client.get("/blog/non-existent-post")
        assert response.status_code == 404


class TestAllEndpoints:
    """General tests for all endpoints."""

    @pytest.mark.parametrize("endpoint", [
        "/documentation",
        "/developers",
        "/changelog",
        "/contact",
        "/help",
        "/status",
        "/blog",
    ])
    def test_endpoint_returns_json(self, client, endpoint):
        """All endpoints should return valid JSON."""
        response = client.get(endpoint)
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        # Should not raise
        data = response.json()
        assert isinstance(data, dict)
