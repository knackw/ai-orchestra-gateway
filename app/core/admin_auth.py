"""
Admin authentication for internal API endpoints.

Provides simple bearer token authentication for admin operations.
"""

import logging
from fastapi import Header, HTTPException

from app.core.config import settings

logger = logging.getLogger(__name__)


async def get_admin_key(x_admin_key: str = Header(...)) -> str:
    """
    Validate admin API key from X-Admin-Key header.
    
    Args:
        x_admin_key: Admin API key from header
        
    Returns:
        Validated admin key
        
    Raises:
        HTTPException 401: Missing or invalid admin key
    """
    if not x_admin_key:
        logger.warning("Admin API access attempted without key")
        raise HTTPException(
            status_code=401,
            detail="Admin API key required"
        )
    
    if x_admin_key != settings.ADMIN_API_KEY:
        logger.warning(f"Invalid admin API key attempted: {x_admin_key[:10]}...")
        raise HTTPException(
            status_code=401,
            detail="Invalid admin API key"
        )
    
    return x_admin_key
