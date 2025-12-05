"""
Admin API endpoints for tenant management.

Internal endpoints for creating and managing tenants.
"""

import logging
from typing import List, Optional
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.core.admin_auth import get_admin_key
from app.core.database import get_supabase_client

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
    created_at: datetime
    updated_at: datetime


class TenantUpdate(BaseModel):
    """Request model for updating a tenant."""
    name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


@router.post("/tenants", response_model=TenantResponse, status_code=201)
async def create_tenant(
    tenant: TenantCreate,
    _admin: str = Depends(get_admin_key)
):
    """
    Create a new tenant.
    
    Requires X-Admin-Key header for authentication.
    """
    client = get_supabase_client()
    
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
    _admin: str = Depends(get_admin_key)
):
    """Get tenant by ID."""
    client = get_supabase_client()
    
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


@router.get("/tenants", response_model=List[TenantResponse])
async def list_tenants(
    skip: int = 0,
    limit: int = 100,
    _admin: str = Depends(get_admin_key)
):
    """List all tenants with pagination."""
    client = get_supabase_client()
    
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
    _admin: str = Depends(get_admin_key)
):
    """Update tenant details."""
    client = get_supabase_client()
    
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
    _admin: str = Depends(get_admin_key)
):
    """
    Soft delete a tenant (mark as inactive).
    
    This does not permanently delete the tenant, just marks it as inactive.
    """
    client = get_supabase_client()
    
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
    except Exception as e:
        logger.error(f"Error deactivating tenant: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
