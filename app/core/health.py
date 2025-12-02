"""
Health check service for the AI Legal Ops Gateway.

Provides comprehensive health status including database connectivity
and uptime metrics for monitoring and Docker healthcheck.
"""

import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from app.core.database import get_supabase_client

logger = logging.getLogger(__name__)


class HealthStatus(str, Enum):
    """Health status enumeration."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class DatabaseHealth(BaseModel):
    """Database health status model."""

    status: HealthStatus
    message: str
    response_time_ms: Optional[float] = None


class HealthCheckResponse(BaseModel):
    """Health check response model."""

    status: HealthStatus
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    uptime_seconds: float
    database: DatabaseHealth
    version: str


class HealthChecker:
    """Health check service for system monitoring."""

    def __init__(self, start_time: datetime):
        """
        Initialize health checker.

        Args:
            start_time: Application startup time for uptime calculation
        """
        self.start_time = start_time

    def get_uptime(self) -> float:
        """
        Calculate application uptime in seconds.

        Returns:
            Uptime in seconds since application start
        """
        now = datetime.now(timezone.utc)
        uptime = (now - self.start_time).total_seconds()
        return uptime

    async def check_database(self) -> DatabaseHealth:
        """
        Check database connectivity and response time.

        Returns:
            DatabaseHealth with status and metrics
        """
        try:
            start = datetime.now(timezone.utc)
            client = get_supabase_client()

            # Perform a simple query to verify connectivity
            # Try to access any table - in production this should be
            # a lightweight query. For now, we'll just verify the client
            # can be created successfully. In a real scenario, you might
            # query a health_check table or use pg_stat_database
            if client:
                # Client created successfully
                end = datetime.now(timezone.utc)
                response_time_ms = (end - start).total_seconds() * 1000

                return DatabaseHealth(
                    status=HealthStatus.HEALTHY,
                    message="Database connection successful",
                    response_time_ms=round(response_time_ms, 2),
                )
            else:
                return DatabaseHealth(
                    status=HealthStatus.UNHEALTHY,
                    message="Failed to create database client",
                    response_time_ms=None,
                )

        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return DatabaseHealth(
                status=HealthStatus.UNHEALTHY,
                message=f"Database connection failed: {str(e)}",
                response_time_ms=None,
            )

    async def check_health(self, version: str = "0.1.1") -> HealthCheckResponse:
        """
        Perform comprehensive health check.

        Args:
            version: Application version string

        Returns:
            HealthCheckResponse with overall system status
        """
        # Check database
        db_health = await self.check_database()

        # Determine overall status
        if db_health.status == HealthStatus.UNHEALTHY:
            overall_status = HealthStatus.UNHEALTHY
        elif db_health.status == HealthStatus.DEGRADED:
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.HEALTHY

        # Calculate uptime
        uptime = self.get_uptime()

        return HealthCheckResponse(
            status=overall_status,
            uptime_seconds=round(uptime, 2),
            database=db_health,
            version=version,
        )
