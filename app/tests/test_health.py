"""
Unit tests for health check functionality.
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.core.health import (
    DatabaseHealth,
    HealthChecker,
    HealthCheckResponse,
    HealthStatus,
)
from app.main import app

client = TestClient(app)


class TestHealthCheckEndpoint:
    """Tests for the /health endpoint."""

    def test_health_endpoint_returns_200(self):
        """Test that health endpoint returns 200 OK."""
        with patch("app.core.health.get_supabase_client"):
            response = client.get("/health")
            assert response.status_code == 200

    def test_health_endpoint_response_structure(self):
        """Test that health endpoint returns correct response structure."""
        mock_client = MagicMock()
        mock_execute = MagicMock()
        (
            mock_client.table.return_value.select.return_value.limit
            .return_value.execute.return_value
        ) = mock_execute

        with patch("app.core.health.get_supabase_client", return_value=mock_client):
            response = client.get("/health")
            data = response.json()

            # Check required fields
            assert "status" in data
            assert "timestamp" in data
            assert "uptime_seconds" in data
            assert "database" in data
            assert "version" in data

            # Check database field structure
            assert "status" in data["database"]
            assert "message" in data["database"]

    def test_health_endpoint_when_database_healthy(self):
        """Test health endpoint when database is healthy."""
        mock_client = MagicMock()
        mock_execute = MagicMock()
        (
            mock_client.table.return_value.select.return_value.limit
            .return_value.execute.return_value
        ) = mock_execute

        with patch("app.core.health.get_supabase_client", return_value=mock_client):
            response = client.get("/health")
            data = response.json()

            assert data["status"] == "healthy"
            assert data["database"]["status"] == "healthy"

    def test_health_endpoint_when_database_fails(self):
        """Test health endpoint when database connection fails."""
        with patch(
            "app.core.health.get_supabase_client",
            side_effect=Exception("Connection failed"),
        ):
            response = client.get("/health")
            data = response.json()

            # Endpoint should still return 200 but with unhealthy status
            assert response.status_code == 200
            assert data["status"] == "unhealthy"
            assert data["database"]["status"] == "unhealthy"


class TestHealthChecker:
    """Tests for HealthChecker class."""

    def test_uptime_calculation(self):
        """Test uptime calculation."""
        start_time = datetime.now(timezone.utc)
        checker = HealthChecker(start_time=start_time)

        uptime = checker.get_uptime()

        # Uptime should be close to 0 (just started)
        assert uptime >= 0
        assert uptime < 1  # Should be less than 1 second

    @pytest.mark.asyncio
    async def test_check_database_success(self):
        """Test database check when connection succeeds."""
        mock_client = MagicMock()
        mock_execute = MagicMock()
        (
            mock_client.table.return_value.select.return_value.limit
            .return_value.execute.return_value
        ) = mock_execute

        start_time = datetime.now(timezone.utc)
        checker = HealthChecker(start_time=start_time)

        with patch("app.core.health.get_supabase_client", return_value=mock_client):
            result = await checker.check_database()

            assert result.status == HealthStatus.HEALTHY
            assert "successful" in result.message.lower()
            assert result.response_time_ms is not None
            assert result.response_time_ms >= 0

    @pytest.mark.asyncio
    async def test_check_database_failure(self):
        """Test database check when connection fails."""
        start_time = datetime.now(timezone.utc)
        checker = HealthChecker(start_time=start_time)

        with patch(
            "app.core.health.get_supabase_client",
            side_effect=Exception("Connection timeout"),
        ):
            result = await checker.check_database()

            assert result.status == HealthStatus.UNHEALTHY
            assert "failed" in result.message.lower()
            assert result.response_time_ms is None

    @pytest.mark.asyncio
    async def test_check_health_overall_status(self):
        """Test overall health status determination."""
        mock_client = MagicMock()
        mock_execute = MagicMock()
        (
            mock_client.table.return_value.select.return_value.limit
            .return_value.execute.return_value
        ) = mock_execute

        start_time = datetime.now(timezone.utc)
        checker = HealthChecker(start_time=start_time)

        with patch("app.core.health.get_supabase_client", return_value=mock_client):
            result = await checker.check_health(version="0.1.1")

            assert isinstance(result, HealthCheckResponse)
            assert result.status == HealthStatus.HEALTHY
            assert result.version == "0.1.1"
            assert result.uptime_seconds >= 0
            assert result.database.status == HealthStatus.HEALTHY

    @pytest.mark.asyncio
    async def test_check_health_unhealthy_database(self):
        """Test overall health when database is unhealthy."""
        start_time = datetime.now(timezone.utc)
        checker = HealthChecker(start_time=start_time)

        with patch(
            "app.core.health.get_supabase_client",
            side_effect=Exception("Connection failed"),
        ):
            result = await checker.check_health(version="0.1.1")

            # Overall status should be unhealthy if database is unhealthy
            assert result.status == HealthStatus.UNHEALTHY
            assert result.database.status == HealthStatus.UNHEALTHY


class TestHealthCheckModels:
    """Tests for health check Pydantic models."""

    def test_database_health_model(self):
        """Test DatabaseHealth model validation."""
        db_health = DatabaseHealth(
            status=HealthStatus.HEALTHY,
            message="Connection successful",
            response_time_ms=15.5,
        )

        assert db_health.status == HealthStatus.HEALTHY
        assert db_health.message == "Connection successful"
        assert db_health.response_time_ms == 15.5

    def test_health_check_response_model(self):
        """Test HealthCheckResponse model validation."""
        db_health = DatabaseHealth(
            status=HealthStatus.HEALTHY, message="OK", response_time_ms=10.0
        )

        response = HealthCheckResponse(
            status=HealthStatus.HEALTHY,
            uptime_seconds=123.45,
            database=db_health,
            version="0.1.1",
        )

        assert response.status == HealthStatus.HEALTHY
        assert response.uptime_seconds == 123.45
        assert response.version == "0.1.1"
        assert response.timestamp is not None
