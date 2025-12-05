"""
Admin API endpoints for license management.

Internal endpoints for creating and managing licenses with secure API key generation.
"""

import logging
import secrets
from typing import List, Optional
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from app.core.admin_auth import get_admin_key
from app.core.database import get_supabase_client

logger = logging.getLogger(__name__)

router = APIRouter()


def generate_license_key() -> str:
    """
    Generate a secure license key with format: lic_<32 random chars>.
    
    Returns:
        License key string
    """
    # Generate 32 cryptographically secure random bytes
    random_bytes = secrets.token_urlsafe(24)  # 24 bytes = ~32 chars base64
    return f"lic_{random_bytes}"


# Request/Response Models
class LicenseCreate(BaseModel):
    """Request model for creating a license."""
    tenant_id: UUID
    credits: int = Field(default=1000, ge=0)
    expires_at: Optional[datetime] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
                "credits": 10000,
                "expires_at": "2025-12-31T23:59:59Z"
            }
        }
    )


class LicenseResponse(BaseModel):
    """Response model for license."""
    id: UUID
    tenant_id: UUID
    license_key: Optional[str] = None  # Only shown on creation
    credits_remaining: int
    is_active: bool
    expires_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class LicenseUpdate(BaseModel):
    """Request model for updating a license."""
    credits_remaining: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    expires_at: Optional[datetime] = None


@router.post("/licenses", response_model=LicenseResponse, status_code=201)
async def create_license(
    license: LicenseCreate,
    _admin: str = Depends(get_admin_key)
):
    """
    Create a new license with generated API key.
    
    Returns the license key ONLY on creation. It cannot be retrieved later.
    Requires X-Admin-Key header for authentication.
    """
    client = get_supabase_client()
    
    try:
        # Verify tenant exists
        tenant = client.table("tenants").select("id").eq("id", str(license.tenant_id)).execute()
        if not tenant.data:
            raise HTTPException(
                status_code=404,
                detail=f"Tenant {license.tenant_id} not found"
            )
        
        # Generate unique license key
        license_key = generate_license_key()
        
        # Create license
        license_data = {
            "tenant_id": str(license.tenant_id),
            "license_key": license_key,  # Store plaintext for MVP (hash in production)
            "credits_remaining": license.credits,
            "is_active": True,
            "expires_at": license.expires_at.isoformat() if license.expires_at else None
        }
        
        result = client.table("licenses").insert(license_data).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=500,
                detail="Failed to create license"
            )
        
        response_data = result.data[0]
        logger.info(f"Created license for tenant {license.tenant_id}")
        
        # Return license key only on creation
        return LicenseResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating license: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.get("/licenses/{license_id}", response_model=LicenseResponse)
async def get_license(
    license_id: UUID,
    _admin: str = Depends(get_admin_key)
):
    """Get license by ID (without showing license key)."""
    client = get_supabase_client()
    
    try:
        result = client.table("licenses").select("*").eq("id", str(license_id)).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=404,
                detail=f"License {license_id} not found"
            )
        
        license_data = result.data[0]
        # Don't include license key in response
        license_data["license_key"] = None
        
        return LicenseResponse(**license_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching license: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.get("/licenses", response_model=List[LicenseResponse])
async def list_licenses(
    tenant_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100,
    _admin: str = Depends(get_admin_key)
):
    """List licenses with optional tenant filter and pagination."""
    client = get_supabase_client()
    
    try:
        query = client.table("licenses").select("*")
        
        if tenant_id:
            query = query.eq("tenant_id", str(tenant_id))
        
        result = query.range(skip, skip + limit - 1).execute()
        
        # Hide license keys in list view
        for lic in result.data:
            lic["license_key"] = None
        
        return [LicenseResponse(**lic) for lic in result.data]
        
    except Exception as e:
        logger.error(f"Error listing licenses: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.put("/licenses/{license_id}", response_model=LicenseResponse)
async def update_license(
    license_id: UUID,
    license_update: LicenseUpdate,
    _admin: str = Depends(get_admin_key)
):
    """Update license (credits, expiry, active status)."""
    client = get_supabase_client()
    
    try:
        # Build update data
        update_data = {k: v for k, v in license_update.model_dump().items() if v is not None}
        
        if not update_data:
            raise HTTPException(
                status_code=400,
                detail="No fields to update"
            )
        
        # Convert datetime to ISO format if present
        if "expires_at" in update_data and update_data["expires_at"]:
            update_data["expires_at"] = update_data["expires_at"].isoformat()
        
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        result = client.table("licenses").update(update_data).eq("id", str(license_id)).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=404,
                detail=f"License {license_id} not found"
            )
        
        logger.info(f"Updated license: {license_id}")
        
        license_data = result.data[0]
        license_data["license_key"] = None
        
        return LicenseResponse(**license_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating license: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.delete("/licenses/{license_id}", status_code=204)
async def revoke_license(
    license_id: UUID,
    _admin: str = Depends(get_admin_key)
):
    """
    Revoke a license (mark as inactive).
    
    This does not delete the license, just marks it as inactive.
    """
    client = get_supabase_client()
    
    try:
        result = client.table("licenses").update({
            "is_active": False,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }).eq("id", str(license_id)).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=404,
                detail=f"License {license_id} not found"
            )
        
        logger.info(f"Revoked license: {license_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error revoking license: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
