import logging
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.api.v1 import generate, vision, embeddings, audio, gdpr
from app.api.v1 import seo, pages, ui, legal, auth
from app.api.v1 import settings as settings_router
from app.api.v1 import audit
from app.core import config
from app.core.health import HealthChecker
from app.core.middleware import RequestIDMiddleware
from app.core.logging import PrivacyLogFilter, RequestIdFilter
from app.core.rate_limit import limiter, custom_rate_limit_exceeded_handler, RateLimitExceeded
from app.core.csrf import CSRFMiddleware, get_csrf_token_endpoint
from app.core.error_handling import register_error_handlers
from app.core.timeout import TimeoutMiddleware
from app.core.cors import configure_cors, validate_cors_configuration
from app.core.trusted_proxy import TrustedProxyMiddleware, parse_trusted_proxies
from slowapi.middleware import SlowAPIMiddleware
import sentry_sdk
from prometheus_fastapi_instrumentator import Instrumentator

# Configure logging with privacy and request ID
# Use a custom formatter that handles missing request_id gracefully
class SafeRequestIdFormatter(logging.Formatter):
    """Formatter that provides a default request_id if not present."""
    def format(self, record):
        if not hasattr(record, 'request_id'):
            record.request_id = 'system'
        return super().format(record)

handler = logging.StreamHandler()
handler.setFormatter(SafeRequestIdFormatter('%(asctime)s - [%(request_id)s] - %(name)s - %(levelname)s - %(message)s'))

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.handlers = [handler]
logger.addFilter(PrivacyLogFilter())
logger.addFilter(RequestIdFilter())

# Track application start time
APP_START_TIME = datetime.now(timezone.utc)

settings = config.settings

# Initialize Sentry
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
    )

# Disable Swagger/ReDoc in production for security
# Only expose API documentation in development environment
# Public API docs for customers are served via Frontend (/developers)
app = FastAPI(
    title="AI Legal Ops Gateway",
    description="Multi-tenant middleware for AI orchestration with privacy enforcement",
    version="0.8.10",
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
    openapi_url="/openapi.json" if settings.is_development else None,
)

# Initialize Templates
templates = Jinja2Templates(directory="app/templates")

# Initialize Prometheus
Instrumentator().instrument(app).expose(app)

# SEC-015: Validate and configure CORS
validate_cors_configuration()
configure_cors(app)

# Connect Limiter to App
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, custom_rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Add Middleware (order matters - outer first)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(CSRFMiddleware)  # SEC-002: CSRF Protection
app.add_middleware(TimeoutMiddleware)  # SEC-017: Request Timeout

# SEC-011: Trusted Proxy Middleware for X-Forwarded-For validation
trusted_proxies = parse_trusted_proxies(settings.TRUSTED_PROXIES)
app.add_middleware(TrustedProxyMiddleware, trusted_proxies=trusted_proxies)

# SEC-010: Register custom error handlers for production safety
register_error_handlers(app)

# Initialize health checker
health_checker = HealthChecker(start_time=APP_START_TIME)

# Include API routers
app.include_router(generate.router, prefix=config.settings.API_V1_STR, tags=["AI Generation"])
app.include_router(vision.router, prefix=config.settings.API_V1_STR, tags=["AI Vision"])
app.include_router(embeddings.router, prefix=config.settings.API_V1_STR, tags=["AI Embeddings"])
app.include_router(audio.router, prefix=config.settings.API_V1_STR, tags=["AI Audio"])
app.include_router(gdpr.router, prefix=config.settings.API_V1_STR, tags=["GDPR Compliance"])

# Include Auth routers (SEC-019: Logout functionality)
app.include_router(auth.router, prefix=config.settings.API_V1_STR, tags=["Authentication"])

# Include Legal routers (no auth required, public documents)
app.include_router(legal.router, prefix=config.settings.API_V1_STR, tags=["Legal & GDPR"])

# Include SEO routers (no auth required)
app.include_router(seo.router, prefix=config.settings.API_V1_STR, tags=["SEO"])

# Include Pages routers (no auth required)
app.include_router(pages.router, prefix=config.settings.API_V1_STR, tags=["Pages"])

# Include Settings routers (auth required)
app.include_router(
    settings_router.router,
    prefix=f"{config.settings.API_V1_STR}/settings",
    tags=["Settings"]
)

# Include UI routers (auth required)
app.include_router(
    ui.router,
    prefix=f"{config.settings.API_V1_STR}/ui",
    tags=["UI"]
)

# Include Audit routers (SEC-020: Frontend Audit Logging)
app.include_router(
    audit.router,
    prefix=config.settings.API_V1_STR,
    tags=["Audit"]
)

# Include admin routers
from app.api.admin import licenses, tenants, apps as admin_apps

app.include_router(
    admin_apps.router,
    prefix=f"{settings.API_V1_STR}/admin",
    tags=["admin-apps"]
)
app.include_router(
    tenants.router,
    prefix=f"{settings.API_V1_STR}/admin",
    tags=["admin-tenants"]
)
app.include_router(
    licenses.router,
    prefix=f"{settings.API_V1_STR}/admin",
    tags=["admin-licenses"]
)

# Include webhook routers
from app.api.webhooks import stripe
app.include_router(
    stripe.router,
    prefix=f"{settings.API_V1_STR}/webhooks",
    tags=["webhooks"]
)

# Include analytics router
from app.api.admin import analytics
app.include_router(
    analytics.router,
    prefix=f"{settings.API_V1_STR}/admin/analytics",
    tags=["admin-analytics"]
)

# Include audit logs router
from app.api.admin import audit_logs
app.include_router(
    audit_logs.router,
    prefix=f"{settings.API_V1_STR}/admin",
    tags=["admin-audit"]
)


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """
    Serve the landing page with Cookie Consent Banner.
    DO NOT rate limit the landing page (or keep it high).
    """
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "title": "Welcome"}
    )


@app.get("/privacy", response_class=HTMLResponse)
async def privacy_policy(request: Request):
    """Serve the DSGVO-compliant Privacy Policy."""
    return templates.TemplateResponse(
        "privacy.html",
        {"request": request, "title": "Datenschutz"}
    )


@app.get("/terms", response_class=HTMLResponse)
async def terms_of_service(request: Request):
    """Serve the Terms of Service."""
    return templates.TemplateResponse(
        "terms.html",
        {"request": request, "title": "AGB"}
    )



@app.get("/health")
async def health_check():
    """
    Comprehensive health check endpoint.
    """
    health_response = await health_checker.check_health(version=app.version)
    return health_response


@app.get(f"{config.settings.API_V1_STR}/csrf-token")
async def csrf_token(request: Request):
    """
    SEC-002: CSRF Token Endpoint

    Returns a CSRF token for use in forms and AJAX requests.
    Frontend should include this token in X-CSRF-Token header.
    """
    return get_csrf_token_endpoint(request)
