"""
Admin API endpoints for tenant management.

Internal endpoints for creating and managing tenants.
"""

import logging
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import List, Optional

from app.core.admin_auth import get_admin_user
from app.core.database import get_supabase_client
from app.core.rbac import UserRole

logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response Models
class TenantCreate(BaseModel):
    """Request model for creating a tenant."""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "ACME Corp",
                "email": "admin@acme.com"
            }
        }
    )


class TenantResponse(BaseModel):
    """Response model for tenant."""
    id: UUID
    name: str
    email: str
    is_active: bool
    avv_signed_at: datetime | None = None
    avv_version: str | None = None
    allowed_ips: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime


class TenantUpdate(BaseModel):
    """Request model for updating a tenant."""
    name: str | None = Field(None, max_length=100)
    email: EmailStr | None = None
    is_active: bool | None = None
    allowed_ips: Optional[List[str]] = None


class AVVUpdate(BaseModel):
    """Request model for recording AVV signature."""
    avv_version: str = Field(..., description="Version of the signed AVV")
    signed_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp of signature"
    )



@router.post("/tenants", response_model=TenantResponse, status_code=201)
async def create_tenant(
    tenant: TenantCreate,
    admin_user: UserRole = Depends(get_admin_user)
):
    """
    Create a new tenant.

    SEC-009: Requires X-Admin-Key header AND admin/owner role.
    """
    # Use service role to bypass RLS
    client = get_supabase_client(use_service_role=True)
    
    try:
        # Check if email already exists
        existing = client.table("tenants").select("id").eq("email", tenant.email).execute()
        if existing.data:
            raise HTTPException(
                status_code=400,
                detail=f"Tenant with email {tenant.email} already exists"
            )
        
        # Create tenant
        result = client.table("tenants").insert({
            "name": tenant.name,
            "email": tenant.email,
            "is_active": True
        }).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=500,
                detail="Failed to create tenant"
            )
        
        tenant_data = result.data[0]
        logger.info(f"Created tenant: {tenant_data['id']}")
        
        return TenantResponse(**tenant_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating tenant: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.get("/tenants/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: UUID,
    admin_user: UserRole = Depends(get_admin_user)
):
    """
    Get tenant by ID.

    SEC-009: Requires X-Admin-Key header AND admin/owner role.
    """
    # Use service role to bypass RLS
    client = get_supabase_client(use_service_role=True)
    
    try:
        result = client.table("tenants").select("*").eq("id", str(tenant_id)).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=404,
                detail=f"Tenant {tenant_id} not found"
            )
        
        return TenantResponse(**result.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching tenant: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.get("/tenants", response_model=list[TenantResponse])
async def list_tenants(
    skip: int = 0,
    limit: int = 100,
    admin_user: UserRole = Depends(get_admin_user)
):
    """
    List all tenants with pagination.

    SEC-009: Requires X-Admin-Key header AND admin/owner role.
    """
    # Use service role to bypass RLS
    client = get_supabase_client(use_service_role=True)
    
    try:
        result = client.table("tenants").select("*").range(skip, skip + limit - 1).execute()
        
        return [TenantResponse(**t) for t in result.data]
        
    except Exception as e:
        logger.error(f"Error listing tenants: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.put("/tenants/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: UUID,
    tenant_update: TenantUpdate,
    admin_user: UserRole = Depends(get_admin_user)
):
    """
    Update tenant details.

    SEC-009: Requires X-Admin-Key header AND admin/owner role.
    """
    # Use service role to bypass RLS
    client = get_supabase_client(use_service_role=True)
    
    try:
        # Build update data (only include non-None fields)
        update_data = {k: v for k, v in tenant_update.model_dump().items() if v is not None}
        
        if not update_data:
            raise HTTPException(
                status_code=400,
                detail="No fields to update"
            )
        
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        result = client.table("tenants").update(update_data).eq("id", str(tenant_id)).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=404,
                detail=f"Tenant {tenant_id} not found"
            )
        
        logger.info(f"Updated tenant: {tenant_id}")
        return TenantResponse(**result.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating tenant: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.delete("/tenants/{tenant_id}", status_code=204)
async def delete_tenant(
    tenant_id: UUID,
    admin_user: UserRole = Depends(get_admin_user)
):
    """
    Soft delete a tenant (mark as inactive).

    This does not permanently delete the tenant, just marks it as inactive.

    SEC-009: Requires X-Admin-Key header AND admin/owner role.
    """
    # Use service role to bypass RLS
    client = get_supabase_client(use_service_role=True)
    
    try:
        result = client.table("tenants").update({
            "is_active": False,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }).eq("id", str(tenant_id)).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=404,
                detail=f"Tenant {tenant_id} not found"
            )
        
        logger.info(f"Deactivated tenant: {tenant_id}")
        
    except HTTPException:
        raise
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.post("/tenants/{tenant_id}/avv", response_model=TenantResponse)
async def update_tenant_avv(
    tenant_id: UUID,
    avv_update: AVVUpdate,
    admin_user: UserRole = Depends(get_admin_user)
):
    """
    Record AVV signature for a tenant.

    SEC-009: Requires X-Admin-Key header AND admin/owner role.
    """
    client = get_supabase_client(use_service_role=True)
    
    try:
        data = {
            "avv_version": avv_update.avv_version,
            "avv_signed_at": avv_update.signed_at.isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        result = client.table("tenants").update(data).eq("id", str(tenant_id)).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=404,
                detail=f"Tenant {tenant_id} not found"
            )
            
        logger.info(f"Updated AVV for tenant {tenant_id}: {avv_update.avv_version}")
        return TenantResponse(**result.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating tenant AVV: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

