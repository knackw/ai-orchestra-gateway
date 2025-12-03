from datetime import datetime, timezone

from fastapi import FastAPI

from app.api.v1 import generate
from app.core.health import HealthChecker

# Track application start time for uptime calculation
APP_START_TIME = datetime.now(timezone.utc)

app = FastAPI(
    title="AI Legal Ops Gateway",
    description="Multi-tenant middleware for AI orchestration with privacy enforcement",
    version="0.1.5",
)

# Initialize health checker
health_checker = HealthChecker(start_time=APP_START_TIME)

# Include API routers
app.include_router(generate.router, prefix="/v1", tags=["AI Generation"])


@app.get("/")
async def root():
    return {"message": "AI Legal Ops Gateway is running"}


@app.get("/health")
async def health_check():
    """
    Comprehensive health check endpoint.

    Returns system status including:
    - Overall health status
    - Database connectivity
    - Uptime metrics
    - Application version

    Used by Docker healthcheck and monitoring systems.
    """
    health_response = await health_checker.check_health(version=app.version)
    return health_response
