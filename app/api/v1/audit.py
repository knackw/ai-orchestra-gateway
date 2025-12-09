"""
SEC-020: Frontend Audit Logging API

This module provides endpoints for logging security-relevant frontend events
to the security_audit_events table. Events are immutable and used for
security auditing, compliance, and threat detection.

Supported event types:
- Authentication: LOGIN_SUCCESS, LOGIN_FAILURE, LOGOUT, SESSION_TIMEOUT
- Authorization: API_KEY_CREATE, API_KEY_DELETE, API_KEY_ROTATE, PERMISSION_DENIED
- Settings: PASSWORD_CHANGE, EMAIL_CHANGE, 2FA_ENABLE, 2FA_DISABLE, PROFILE_UPDATE
- Admin: TENANT_CREATE, TENANT_DELETE, LICENSE_CREATE, LICENSE_DELETE, USER_ROLE_CHANGE
- Security: SUSPICIOUS_ACTIVITY, RATE_LIMIT_EXCEEDED, IP_BLOCKED, MFA_CHALLENGE
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, Field, ConfigDict
from app.core.security import get_supabase_client
from app.core.rate_limit import limiter

router = APIRouter()
logger = logging.getLogger(__name__)

# Event type categories for validation
EVENT_CATEGORIES = {
    "authentication": [
        "LOGIN_SUCCESS",
        "LOGIN_FAILURE",
        "LOGOUT",
        "SESSION_TIMEOUT",
        "SESSION_REFRESH",
    ],
    "authorization": [
        "API_KEY_CREATE",
        "API_KEY_DELETE",
        "API_KEY_ROTATE",
        "PERMISSION_DENIED",
        "ACCESS_TOKEN_REFRESH",
    ],
    "settings": [
        "PASSWORD_CHANGE",
        "EMAIL_CHANGE",
        "2FA_ENABLE",
        "2FA_DISABLE",
        "PROFILE_UPDATE",
        "NOTIFICATION_SETTINGS_CHANGE",
        "LANGUAGE_CHANGE",
    ],
    "admin": [
        "TENANT_CREATE",
        "TENANT_DELETE",
        "TENANT_UPDATE",
        "LICENSE_CREATE",
        "LICENSE_DELETE",
        "LICENSE_UPDATE",
        "USER_ROLE_CHANGE",
        "USER_DELETE",
        "APP_CREATE",
        "APP_DELETE",
    ],
    "security": [
        "SUSPICIOUS_ACTIVITY",
        "RATE_LIMIT_EXCEEDED",
        "IP_BLOCKED",
        "MFA_CHALLENGE",
        "CSRF_TOKEN_MISMATCH",
        "INVALID_SESSION",
    ],
}

# Flatten for validation
VALID_EVENT_TYPES = set()
for category, events in EVENT_CATEGORIES.items():
    VALID_EVENT_TYPES.update(events)


class AuditEventRequest(BaseModel):
    """Request model for logging an audit event."""

    event_type: str = Field(
        ...,
        description="Type of security event (e.g., LOGIN_SUCCESS, API_KEY_CREATE)",
    )
    user_id: Optional[str] = Field(
        None,
        description="User ID (UUID) if authenticated, None for unauthenticated events",
    )
    tenant_id: Optional[str] = Field(
        None,
        description="Tenant ID (UUID) if associated with a tenant",
    )
    details: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional event context as JSON",
    )
    success: bool = Field(
        True,
        description="Whether the action succeeded",
    )
    error_message: Optional[str] = Field(
        None,
        description="Error message if action failed",
    )
    client_version: Optional[str] = Field(
        None,
        description="Frontend application version",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "event_type": "LOGIN_SUCCESS",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "tenant_id": "550e8400-e29b-41d4-a716-446655440001",
                "details": {"method": "email", "remember_me": True},
                "success": True,
                "client_version": "1.0.0",
            }
        }
    )


class AuditEventResponse(BaseModel):
    """Response model for audit event logging."""

    id: str
    created_at: datetime
    event_type: str
    success: bool

    model_config = ConfigDict(from_attributes=True)


def _get_event_category(event_type: str) -> str:
    """Determine event category from event type."""
    for category, events in EVENT_CATEGORIES.items():
        if event_type in events:
            return category
    return "other"


def _get_event_severity(event_type: str, success: bool) -> str:
    """Determine event severity based on type and success."""
    # Critical events
    critical_events = [
        "LOGIN_FAILURE",
        "PERMISSION_DENIED",
        "SUSPICIOUS_ACTIVITY",
        "IP_BLOCKED",
        "CSRF_TOKEN_MISMATCH",
        "INVALID_SESSION",
    ]

    # Warning events
    warning_events = [
        "RATE_LIMIT_EXCEEDED",
        "SESSION_TIMEOUT",
        "MFA_CHALLENGE",
    ]

    if event_type in critical_events:
        return "critical"
    elif event_type in warning_events:
        return "warning"
    elif not success:
        return "warning"
    else:
        return "info"


@router.post("/audit/log", response_model=AuditEventResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("100/minute")  # Prevent audit log flooding
async def log_audit_event(request: Request, event: AuditEventRequest):
    """
    Log a security audit event.

    This endpoint is called by the frontend to record security-relevant actions
    such as login attempts, API key creation, settings changes, and admin actions.

    **Rate Limit:** 100 requests per minute per IP

    **Event Types:**
    - **Authentication:** LOGIN_SUCCESS, LOGIN_FAILURE, LOGOUT, SESSION_TIMEOUT
    - **Authorization:** API_KEY_CREATE, API_KEY_DELETE, PERMISSION_DENIED
    - **Settings:** PASSWORD_CHANGE, EMAIL_CHANGE, 2FA_ENABLE, PROFILE_UPDATE
    - **Admin:** TENANT_CREATE, LICENSE_CREATE, USER_ROLE_CHANGE
    - **Security:** SUSPICIOUS_ACTIVITY, RATE_LIMIT_EXCEEDED, IP_BLOCKED

    **Examples:**

    Login Success:
    ```json
    {
        "event_type": "LOGIN_SUCCESS",
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
        "tenant_id": "550e8400-e29b-41d4-a716-446655440001",
        "details": {"method": "email", "remember_me": true},
        "success": true
    }
    ```

    Login Failure:
    ```json
    {
        "event_type": "LOGIN_FAILURE",
        "user_id": null,
        "tenant_id": null,
        "details": {"email": "user@example.com", "reason": "invalid_password"},
        "success": false,
        "error_message": "Invalid credentials"
    }
    ```

    API Key Creation:
    ```json
    {
        "event_type": "API_KEY_CREATE",
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
        "tenant_id": "550e8400-e29b-41d4-a716-446655440001",
        "details": {"key_name": "Production API Key", "permissions": ["read", "write"]},
        "success": true
    }
    ```

    **Returns:**
    - **201 Created:** Event logged successfully
    - **400 Bad Request:** Invalid event type
    - **422 Validation Error:** Invalid request format
    - **429 Too Many Requests:** Rate limit exceeded
    - **500 Internal Server Error:** Database error
    """
    # Validate event type
    if event.event_type not in VALID_EVENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid event_type '{event.event_type}'. "
            f"Must be one of: {', '.join(sorted(VALID_EVENT_TYPES))}",
        )

    # Extract client metadata from request
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    # Determine event category and severity
    event_category = _get_event_category(event.event_type)
    severity = _get_event_severity(event.event_type, event.success)

    try:
        # Use service role to bypass RLS (audit events are system-level)
        client = get_supabase_client(use_service_role=True)

        # Insert audit event
        result = client.table("security_audit_events").insert({
            "user_id": event.user_id,
            "tenant_id": event.tenant_id,
            "event_type": event.event_type,
            "event_category": event_category,
            "severity": severity,
            "ip_address": client_ip,
            "user_agent": user_agent,
            "client_version": event.client_version,
            "details": event.details or {},
            "success": event.success,
            "error_message": event.error_message,
        }).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to log audit event",
            )

        audit_event = result.data[0]

        # Log to application logs (without PII - already filtered by PrivacyLogFilter)
        log_message = (
            f"Security audit event logged: {event.event_type} "
            f"(category={event_category}, severity={severity}, success={event.success})"
        )

        if severity == "critical":
            logger.warning(log_message)
        else:
            logger.info(log_message)

        return AuditEventResponse(
            id=audit_event["id"],
            created_at=audit_event["created_at"],
            event_type=audit_event["event_type"],
            success=audit_event["success"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to log audit event: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to log audit event: {str(e)}",
        )


@router.get("/audit/event-types")
async def get_event_types():
    """
    Get all valid event types organized by category.

    This endpoint returns the complete list of supported security audit event types,
    organized by category. Useful for frontend validation and documentation.

    **Returns:**
    ```json
    {
        "authentication": ["LOGIN_SUCCESS", "LOGIN_FAILURE", "LOGOUT", ...],
        "authorization": ["API_KEY_CREATE", "API_KEY_DELETE", ...],
        "settings": ["PASSWORD_CHANGE", "EMAIL_CHANGE", ...],
        "admin": ["TENANT_CREATE", "LICENSE_CREATE", ...],
        "security": ["SUSPICIOUS_ACTIVITY", "RATE_LIMIT_EXCEEDED", ...]
    }
    ```
    """
    return EVENT_CATEGORIES
