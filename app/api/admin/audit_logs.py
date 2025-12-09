from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, ConfigDict
from app.core.security import get_supabase_client
from app.core.admin_auth import get_admin_user
from app.core.rbac import UserRole

router = APIRouter()

class UsageLogResponse(BaseModel):
    id: str
    created_at: datetime
    provider: str
    model: Optional[str] = None
    prompt_length: int
    tokens_used: int
    credits_deducted: int
    pii_detected: bool
    response_status: str
    error_type: Optional[str] = None
    
    # Joined fields
    tenant_name: Optional[str] = "Unknown"
    license_key: Optional[str] = "Unknown"

    model_config = ConfigDict(from_attributes=True)

class AuditLogsList(BaseModel):
    total: int
    page: int
    limit: int
    items: List[UsageLogResponse]
    model_config = ConfigDict(from_attributes=True)

@router.get("/audit-logs", response_model=AuditLogsList)
async def get_audit_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=1000),
    tenant_id: Optional[str] = None,
    # license_key: Optional[str] = None, # Simple filtering first
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    admin_user: UserRole = Depends(get_admin_user)
):
    """
    Get paginated and filtered audit logs.
    """
    client = get_supabase_client(use_service_role=True)
    
    try:
        # Base query
        # Select with joins for context
        # Supabase syntax: select(*, tenants(name), licenses(license_key))
        query = client.table("usage_logs").select(
            "*, tenants(name), licenses(license_key)", 
            count="exact"
        )
        
        # Apply filters
        if tenant_id:
            query = query.eq("tenant_id", tenant_id)
        
        if status:
            query = query.eq("response_status", status)
            
        if start_date:
            query = query.gte("created_at", start_date.isoformat())
            
        if end_date:
            query = query.lte("created_at", end_date.isoformat())
            
        # Pagination
        start = (page - 1) * limit
        end = start + limit - 1
        query = query.range(start, end).order("created_at", desc=True)
        
        result = query.execute()
        
        # Transform result
        items = []
        for row in result.data:
            # Flatten joined fields
            tenant_data = row.get("tenants") or {}
            license_data = row.get("licenses") or {}
            
            item = {
                **row,
                "tenant_name": tenant_data.get("name", "Unknown"),
                "license_key": license_data.get("license_key", "Unknown")
            }
            items.append(item)
            
        return {
            "total": result.count,
            "page": page,
            "limit": limit,
            "items": items
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
