from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from app.core.security import get_supabase_client
from app.core.admin_auth import get_admin_user
from app.core.rbac import UserRole

router = APIRouter()

@router.get("/stats/credits")
async def get_credit_stats(
    admin_user: UserRole = Depends(get_admin_user)
):
    """
    Get aggregated credit statistics.
    Returns:
        - total_allocated: Sum of all credits_total
        - total_remaining: Sum of all credits_remaining
        - total_used: Derived (allocated - remaining)
    """
    client = get_supabase_client(use_service_role=True)

    try:
        # Fetch generic aggregation (Sum)
        # Note: PostgREST doesn't support aggregate functions directly on the root endpoint easily without RPC or views.
        # For Phase 2 MVP with low data volume, fetching all licenses is acceptable.
        # For production, we should create a DB view or RPC.
        
        response = client.table("licenses").select("credits_total, credits_remaining").execute()
        licenses = response.data
        
        total_allocated = sum(l["credits_total"] for l in licenses)
        total_remaining = sum(l["credits_remaining"] for l in licenses)
        total_used = total_allocated - total_remaining
        
        return {
            "total_allocated": total_allocated,
            "total_remaining": total_remaining,
            "total_used": total_used
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/top-tenants")
async def get_top_tenants(
    limit: int = 10,
    admin_user: UserRole = Depends(get_admin_user)
):
    """
    Get top tenants by credit usage.
    
    For MVP, we calculate this by aggregating license usage per tenant.
    Ideally, this should be a SQL view:
    SELECT t.name, t.id, SUM(l.credits_total - l.credits_remaining) as used
    FROM tenants t 
    JOIN licenses l ON t.id = l.tenant_id
    GROUP BY t.id
    ORDER BY used DESC
    """
    client = get_supabase_client(use_service_role=True)
    
    try:
        # Fetch licenses with tenant info
        response = client.table("licenses").select("credits_total, credits_remaining, tenants(id, name)").execute()
        data = response.data
        
        tenant_usage = {}
        
        for row in data:
            tenant = row.get("tenants")
            if not tenant:
                continue
                
            tid = tenant["id"]
            tname = tenant["name"]
            used = row["credits_total"] - row["credits_remaining"]
            
            if tid not in tenant_usage:
                tenant_usage[tid] = {"id": tid, "name": tname, "total_usage": 0}
            
            tenant_usage[tid]["total_usage"] += used
            
        # Sort and limit
        sorted_tenants = sorted(
            tenant_usage.values(), 
            key=lambda x: x["total_usage"], 
            reverse=True
        )
        
        return sorted_tenants[:limit]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/usage-over-time")
async def get_usage_over_time(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """
    Get daily usage statistics.
    Uses the 'daily_usage_stats' DB view.
    """
    client = get_supabase_client(use_service_role=True)
    try:
        query = client.table("daily_usage_stats").select("*").order("usage_date", desc=True)
        
        if start_date:
            query = query.gte("usage_date", start_date)
        if end_date:
            query = query.lte("usage_date", end_date)
            
        response = query.execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/provider-split")
async def get_provider_split():
    """
    Get generic split of usage by provider (Anthropic vs Scaleway).
    """
    client = get_supabase_client(use_service_role=True)
    try:
        # We can aggregate from the view for efficiency
        response = client.table("daily_usage_stats").select("provider, request_count").execute()
        data = response.data
        
        split = {}
        for row in data:
            prov = row["provider"]
            count = row["request_count"]
            split[prov] = split.get(prov, 0) + count
            
        return [{"provider": k, "count": v} for k, v in split.items()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/export")
async def export_usage_logs():
    """
    Export usage logs as CSV.
    """
    from fastapi.responses import StreamingResponse
    import io
    import csv

    client = get_supabase_client(use_service_role=True)
    
    async def iter_csv():
        # Write header
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "id", "created_at", "license_id", "app_id", "tenant_id", 
            "provider", "model", "prompt_length", "tokens_used", 
            "credits_deducted", "response_status", "pii_detected"
        ])
        yield output.getvalue()
        output.seek(0)
        output.truncate(0)

        # Fetch data in chunks (simplified for MVP: fetch all, but streaming response structure ready)
        # Ideally, we should use cursor/pagination for large exports.
        try:
            response = client.table("usage_logs").select("*").order("created_at", desc=True).limit(5000).execute()
            
            for row in response.data:
                writer.writerow([
                    row.get("id"),
                    row.get("created_at"),
                    row.get("license_id"),
                    row.get("app_id"),
                    row.get("tenant_id"),
                    row.get("provider"),
                    row.get("model"),
                    row.get("prompt_length"),
                    row.get("tokens_used"),
                    row.get("credits_deducted"),
                    row.get("response_status"),
                    row.get("pii_detected")
                ])
                yield output.getvalue()
                output.seek(0)
                output.truncate(0)
                
        except Exception as e:
            # In a streaming response, we can't easily raise HTTP exception once started.
            # We might log valid error or append error row.
            yield "Error fetching data"

    return StreamingResponse(
        iter_csv(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=usage_logs.csv"}
    )
