"""
Admin API endpoints for app management.

Internal endpoints for creating and managing apps.
"""

import logging
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from app.core.admin_auth import get_admin_user
from app.core.database import get_supabase_client
from app.core.rbac import UserRole

logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response Models
class AppCreate(BaseModel):
    """Request model for creating an app."""
    tenant_id: UUID
    app_name: str = Field(..., min_length=1, max_length=100)
    allowed_origins: List[str] = Field(default_factory=list)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
                "app_name": "AGB Generator Plugin",
                "allowed_origins": ["https://myshop.com"]
            }
        }
    )


class AppResponse(BaseModel):
    """Response model for app."""
    id: UUID
    tenant_id: UUID
    app_name: str
    allowed_origins: Optional[List[str]] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class AppUpdate(BaseModel):
    """Request model for updating an app."""
    app_name: Optional[str] = Field(None, min_length=1, max_length=100)
    allowed_origins: Optional[List[str]] = None
    is_active: Optional[bool] = None


@router.post("/apps", response_model=AppResponse, status_code=201)
async def create_app(
    app: AppCreate,
    admin_user: UserRole = Depends(get_admin_user)
):
    """
    Create a new app for a tenant.

    SEC-009: Requires X-Admin-Key header AND admin/owner role.
    """
    # Use service role to bypass RLS
    client = get_supabase_client(use_service_role=True)
    
    try:
        # Verify tenant exists
        tenant = client.table("tenants").select("id").eq("id", str(app.tenant_id)).execute()
        if not tenant.data:
            raise HTTPException(
                status_code=404,
                detail=f"Tenant {app.tenant_id} not found"
            )
            
        # Create app
        app_data = {
            "tenant_id": str(app.tenant_id),
            "app_name": app.app_name,
            "allowed_origins": app.allowed_origins,
            "is_active": True
        }
        
        result = client.table("apps").insert(app_data).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=500,
                detail="Failed to create app"
            )
            
        created_app = result.data[0]
        logger.info(f"Created app {created_app['id']} for tenant {app.tenant_id}")
        
        return AppResponse(**created_app)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating app: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.get("/apps/{app_id}", response_model=AppResponse)
async def get_app(
    app_id: UUID,
    admin_user: UserRole = Depends(get_admin_user)
):
    """
    Get app by ID.

    SEC-009: Requires X-Admin-Key header AND admin/owner role.
    """
    # Use service role to bypass RLS
    client = get_supabase_client(use_service_role=True)
    
    try:
        result = client.table("apps").select("*").eq("id", str(app_id)).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=404,
                detail=f"App {app_id} not found"
            )
            
        return AppResponse(**result.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching app: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.get("/apps", response_model=List[AppResponse])
async def list_apps(
    tenant_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100,
    admin_user: UserRole = Depends(get_admin_user)
):
    """
    List apps, optionally filtered by tenant.

    SEC-009: Requires X-Admin-Key header AND admin/owner role.
    """
    # Use service role to bypass RLS
    client = get_supabase_client(use_service_role=True)
    
    try:
        query = client.table("apps").select("*")
        
        if tenant_id:
            query = query.eq("tenant_id", str(tenant_id))
            
        result = query.range(skip, skip + limit - 1).execute()
        
        return [AppResponse(**a) for a in result.data]
        
    except Exception as e:
        logger.error(f"Error listing apps: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.put("/apps/{app_id}", response_model=AppResponse)
async def update_app(
    app_id: UUID,
    app_update: AppUpdate,
    admin_user: UserRole = Depends(get_admin_user)
):
    """
    Update app details.

    SEC-009: Requires X-Admin-Key header AND admin/owner role.
    """
    # Use service role to bypass RLS
    client = get_supabase_client(use_service_role=True)
    
    try:
        # Build update data
        update_data = {k: v for k, v in app_update.model_dump().items() if v is not None}
        
        if not update_data:
            # Nothing to update, fetch and return existing
            current = client.table("apps").select("*").eq("id", str(app_id)).execute()
            if not current.data:
                raise HTTPException(status_code=404, detail="App not found")
            return AppResponse(**current.data[0])
            
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        result = client.table("apps").update(update_data).eq("id", str(app_id)).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=404,
                detail=f"App {app_id} not found"
            )
            
        logger.info(f"Updated app: {app_id}")
        return AppResponse(**result.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating app: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.delete("/apps/{app_id}", status_code=204)
async def delete_app(
    app_id: UUID,
    admin_user: UserRole = Depends(get_admin_user)
):
    """
    Soft delete an app (set is_active = false).

    SEC-009: Requires X-Admin-Key header AND admin/owner role.
    """
    # Use service role to bypass RLS
    client = get_supabase_client(use_service_role=True)
    
    try:
        result = client.table("apps").update({
            "is_active": False,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }).eq("id", str(app_id)).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=404,
                detail=f"App {app_id} not found"
            )
            
        logger.info(f"Deactivated app: {app_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deactivating app: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
