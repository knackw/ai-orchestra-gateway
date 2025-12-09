"""
Settings API endpoints for user self-service.

Provides:
- API Key Management
- User preferences
- Notification settings
- Security settings
"""

import logging
import secrets
import hashlib
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.core.security import get_current_license, LicenseInfo

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Settings"])


# ============================================================================
# Request/Response Models
# ============================================================================

class APIKeyCreate(BaseModel):
    """Request model for creating an API key."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    scopes: list[str] = Field(default_factory=lambda: ["read", "write"])
    expires_in_days: Optional[int] = Field(None, ge=1, le=365)


class APIKeyResponse(BaseModel):
    """Response model for API key (without secret)."""
    id: str
    name: str
    description: Optional[str]
    prefix: str  # First 8 chars for identification
    scopes: list[str]
    is_active: bool
    created_at: str
    expires_at: Optional[str]
    last_used_at: Optional[str]


class APIKeyCreatedResponse(APIKeyResponse):
    """Response model when creating API key (includes secret once)."""
    secret: str  # Only returned once at creation


class APIKeyUpdate(BaseModel):
    """Request model for updating an API key."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    scopes: Optional[list[str]] = None
    is_active: Optional[bool] = None


class APIKeyListResponse(BaseModel):
    """Response model for listing API keys."""
    keys: list[APIKeyResponse]
    total: int


class UserPreferences(BaseModel):
    """User preferences settings."""
    theme: str = "system"  # light, dark, system
    language: str = "en"
    timezone: str = "UTC"
    date_format: str = "YYYY-MM-DD"
    items_per_page: int = 25


class NotificationSettings(BaseModel):
    """Notification settings."""
    email_notifications: bool = True
    usage_alerts: bool = True
    usage_threshold: int = 80  # Percentage
    security_alerts: bool = True
    newsletter: bool = False
    weekly_summary: bool = True


class SecuritySettings(BaseModel):
    """Security settings."""
    two_factor_enabled: bool = False
    session_timeout_minutes: int = 60
    ip_whitelist_enabled: bool = False
    allowed_ips: list[str] = Field(default_factory=list)
    require_key_rotation: bool = False
    key_rotation_days: int = 90


class SettingsResponse(BaseModel):
    """Complete settings response."""
    preferences: UserPreferences
    notifications: NotificationSettings
    security: SecuritySettings


# ============================================================================
# In-Memory Storage (Mock for demo - replace with DB in production)
# ============================================================================

# Mock storage for API keys (in production, use database)
_api_keys_store: dict[str, list[dict]] = {}
_settings_store: dict[str, dict] = {}


def _generate_api_key() -> tuple[str, str]:
    """Generate a new API key with prefix and secret."""
    prefix = "aog_" + secrets.token_hex(4)  # aog_12345678
    secret_part = secrets.token_hex(24)  # 48 chars
    full_key = f"{prefix}_{secret_part}"
    # Hash for storage
    key_hash = hashlib.sha256(full_key.encode()).hexdigest()
    return full_key, key_hash


def _get_tenant_keys(tenant_id: str) -> list[dict]:
    """Get API keys for a tenant."""
    return _api_keys_store.get(tenant_id, [])


def _get_tenant_settings(tenant_id: str) -> dict:
    """Get settings for a tenant."""
    if tenant_id not in _settings_store:
        _settings_store[tenant_id] = {
            "preferences": UserPreferences().model_dump(),
            "notifications": NotificationSettings().model_dump(),
            "security": SecuritySettings().model_dump(),
        }
    return _settings_store[tenant_id]


# ============================================================================
# API Key Management Endpoints
# ============================================================================

@router.get("/api-keys", response_model=APIKeyListResponse)
async def list_api_keys(
    license: LicenseInfo = Depends(get_current_license),
) -> APIKeyListResponse:
    """
    List all API keys for the current tenant.

    Returns keys without their secrets.
    """
    keys = _get_tenant_keys(license.tenant_id)

    return APIKeyListResponse(
        keys=[
            APIKeyResponse(
                id=k["id"],
                name=k["name"],
                description=k.get("description"),
                prefix=k["prefix"],
                scopes=k["scopes"],
                is_active=k["is_active"],
                created_at=k["created_at"],
                expires_at=k.get("expires_at"),
                last_used_at=k.get("last_used_at"),
            )
            for k in keys
        ],
        total=len(keys),
    )


@router.post("/api-keys", response_model=APIKeyCreatedResponse, status_code=201)
async def create_api_key(
    key_data: APIKeyCreate,
    license: LicenseInfo = Depends(get_current_license),
) -> APIKeyCreatedResponse:
    """
    Create a new API key.

    IMPORTANT: The secret is only returned once. Store it securely.
    """
    # Validate scopes
    valid_scopes = {"read", "write", "admin", "billing", "analytics"}
    for scope in key_data.scopes:
        if scope not in valid_scopes:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid scope: {scope}. Valid scopes: {valid_scopes}"
            )

    # Generate key
    full_key, key_hash = _generate_api_key()
    prefix = full_key.split("_")[0] + "_" + full_key.split("_")[1][:8]

    now = datetime.now(timezone.utc)
    expires_at = None
    if key_data.expires_in_days:
        from datetime import timedelta
        expires_at = (now + timedelta(days=key_data.expires_in_days)).isoformat()

    key_record = {
        "id": secrets.token_hex(16),
        "name": key_data.name,
        "description": key_data.description,
        "prefix": prefix,
        "key_hash": key_hash,
        "scopes": key_data.scopes,
        "is_active": True,
        "created_at": now.isoformat(),
        "expires_at": expires_at,
        "last_used_at": None,
    }

    # Store
    if license.tenant_id not in _api_keys_store:
        _api_keys_store[license.tenant_id] = []
    _api_keys_store[license.tenant_id].append(key_record)

    logger.info(f"Created API key {prefix} for tenant {license.tenant_id}")

    return APIKeyCreatedResponse(
        id=key_record["id"],
        name=key_record["name"],
        description=key_record["description"],
        prefix=prefix,
        scopes=key_record["scopes"],
        is_active=True,
        created_at=key_record["created_at"],
        expires_at=expires_at,
        last_used_at=None,
        secret=full_key,  # Only returned once!
    )


@router.get("/api-keys/{key_id}", response_model=APIKeyResponse)
async def get_api_key(
    key_id: str,
    license: LicenseInfo = Depends(get_current_license),
) -> APIKeyResponse:
    """Get details of a specific API key."""
    keys = _get_tenant_keys(license.tenant_id)

    for k in keys:
        if k["id"] == key_id:
            return APIKeyResponse(
                id=k["id"],
                name=k["name"],
                description=k.get("description"),
                prefix=k["prefix"],
                scopes=k["scopes"],
                is_active=k["is_active"],
                created_at=k["created_at"],
                expires_at=k.get("expires_at"),
                last_used_at=k.get("last_used_at"),
            )

    raise HTTPException(status_code=404, detail="API key not found")


@router.put("/api-keys/{key_id}", response_model=APIKeyResponse)
async def update_api_key(
    key_id: str,
    update_data: APIKeyUpdate,
    license: LicenseInfo = Depends(get_current_license),
) -> APIKeyResponse:
    """Update an API key's metadata or status."""
    keys = _get_tenant_keys(license.tenant_id)

    for k in keys:
        if k["id"] == key_id:
            if update_data.name is not None:
                k["name"] = update_data.name
            if update_data.description is not None:
                k["description"] = update_data.description
            if update_data.scopes is not None:
                # Validate scopes
                valid_scopes = {"read", "write", "admin", "billing", "analytics"}
                for scope in update_data.scopes:
                    if scope not in valid_scopes:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Invalid scope: {scope}"
                        )
                k["scopes"] = update_data.scopes
            if update_data.is_active is not None:
                k["is_active"] = update_data.is_active

            logger.info(f"Updated API key {key_id} for tenant {license.tenant_id}")

            return APIKeyResponse(
                id=k["id"],
                name=k["name"],
                description=k.get("description"),
                prefix=k["prefix"],
                scopes=k["scopes"],
                is_active=k["is_active"],
                created_at=k["created_at"],
                expires_at=k.get("expires_at"),
                last_used_at=k.get("last_used_at"),
            )

    raise HTTPException(status_code=404, detail="API key not found")


@router.delete("/api-keys/{key_id}", status_code=204)
async def delete_api_key(
    key_id: str,
    license: LicenseInfo = Depends(get_current_license),
) -> None:
    """
    Revoke and delete an API key.

    This action is irreversible.
    """
    keys = _get_tenant_keys(license.tenant_id)

    for i, k in enumerate(keys):
        if k["id"] == key_id:
            del keys[i]
            logger.info(f"Deleted API key {key_id} for tenant {license.tenant_id}")
            return

    raise HTTPException(status_code=404, detail="API key not found")


@router.post("/api-keys/{key_id}/rotate", response_model=APIKeyCreatedResponse)
async def rotate_api_key(
    key_id: str,
    license: LicenseInfo = Depends(get_current_license),
) -> APIKeyCreatedResponse:
    """
    Rotate an API key.

    Creates a new key with the same settings and revokes the old one.
    The new secret is only returned once.
    """
    keys = _get_tenant_keys(license.tenant_id)

    old_key = None
    for i, k in enumerate(keys):
        if k["id"] == key_id:
            old_key = k
            del keys[i]
            break

    if not old_key:
        raise HTTPException(status_code=404, detail="API key not found")

    # Generate new key
    full_key, key_hash = _generate_api_key()
    prefix = full_key.split("_")[0] + "_" + full_key.split("_")[1][:8]

    now = datetime.now(timezone.utc)

    key_record = {
        "id": secrets.token_hex(16),
        "name": old_key["name"],
        "description": old_key.get("description"),
        "prefix": prefix,
        "key_hash": key_hash,
        "scopes": old_key["scopes"],
        "is_active": True,
        "created_at": now.isoformat(),
        "expires_at": old_key.get("expires_at"),
        "last_used_at": None,
    }

    keys.append(key_record)

    logger.info(f"Rotated API key {key_id} -> {key_record['id']} for tenant {license.tenant_id}")

    return APIKeyCreatedResponse(
        id=key_record["id"],
        name=key_record["name"],
        description=key_record["description"],
        prefix=prefix,
        scopes=key_record["scopes"],
        is_active=True,
        created_at=key_record["created_at"],
        expires_at=key_record.get("expires_at"),
        last_used_at=None,
        secret=full_key,
    )


# ============================================================================
# User Preferences Endpoints
# ============================================================================

@router.get("/preferences", response_model=UserPreferences)
async def get_preferences(
    license: LicenseInfo = Depends(get_current_license),
) -> UserPreferences:
    """Get user preferences."""
    settings = _get_tenant_settings(license.tenant_id)
    return UserPreferences(**settings["preferences"])


@router.put("/preferences", response_model=UserPreferences)
async def update_preferences(
    preferences: UserPreferences,
    license: LicenseInfo = Depends(get_current_license),
) -> UserPreferences:
    """Update user preferences."""
    # Validate theme
    if preferences.theme not in ["light", "dark", "system"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid theme. Choose from: light, dark, system"
        )

    # Validate language
    valid_languages = ["en", "de", "fr", "es"]
    if preferences.language not in valid_languages:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid language. Choose from: {valid_languages}"
        )

    settings = _get_tenant_settings(license.tenant_id)
    settings["preferences"] = preferences.model_dump()

    logger.info(f"Updated preferences for tenant {license.tenant_id}")

    return preferences


# ============================================================================
# Notification Settings Endpoints
# ============================================================================

@router.get("/notifications", response_model=NotificationSettings)
async def get_notification_settings(
    license: LicenseInfo = Depends(get_current_license),
) -> NotificationSettings:
    """Get notification settings."""
    settings = _get_tenant_settings(license.tenant_id)
    return NotificationSettings(**settings["notifications"])


@router.put("/notifications", response_model=NotificationSettings)
async def update_notification_settings(
    notifications: NotificationSettings,
    license: LicenseInfo = Depends(get_current_license),
) -> NotificationSettings:
    """Update notification settings."""
    # Validate threshold
    if not 0 <= notifications.usage_threshold <= 100:
        raise HTTPException(
            status_code=400,
            detail="Usage threshold must be between 0 and 100"
        )

    settings = _get_tenant_settings(license.tenant_id)
    settings["notifications"] = notifications.model_dump()

    logger.info(f"Updated notification settings for tenant {license.tenant_id}")

    return notifications


# ============================================================================
# Security Settings Endpoints
# ============================================================================

@router.get("/security", response_model=SecuritySettings)
async def get_security_settings(
    license: LicenseInfo = Depends(get_current_license),
) -> SecuritySettings:
    """Get security settings."""
    settings = _get_tenant_settings(license.tenant_id)
    return SecuritySettings(**settings["security"])


@router.put("/security", response_model=SecuritySettings)
async def update_security_settings(
    security: SecuritySettings,
    license: LicenseInfo = Depends(get_current_license),
) -> SecuritySettings:
    """Update security settings."""
    # Validate session timeout
    if not 5 <= security.session_timeout_minutes <= 1440:
        raise HTTPException(
            status_code=400,
            detail="Session timeout must be between 5 and 1440 minutes"
        )

    # Validate key rotation days
    if not 7 <= security.key_rotation_days <= 365:
        raise HTTPException(
            status_code=400,
            detail="Key rotation days must be between 7 and 365"
        )

    settings = _get_tenant_settings(license.tenant_id)
    settings["security"] = security.model_dump()

    logger.info(f"Updated security settings for tenant {license.tenant_id}")

    return security


# ============================================================================
# Combined Settings Endpoint
# ============================================================================

@router.get("/all", response_model=SettingsResponse)
async def get_all_settings(
    license: LicenseInfo = Depends(get_current_license),
) -> SettingsResponse:
    """Get all settings at once."""
    settings = _get_tenant_settings(license.tenant_id)

    return SettingsResponse(
        preferences=UserPreferences(**settings["preferences"]),
        notifications=NotificationSettings(**settings["notifications"]),
        security=SecuritySettings(**settings["security"]),
    )
