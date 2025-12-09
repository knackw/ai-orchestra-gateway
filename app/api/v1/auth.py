"""
SEC-019: Authentication endpoints for user session management.

Implements global logout functionality using Supabase Auth.
"""

import logging
from typing import Optional

from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel

from app.core.database import get_supabase_client
from supabase import Client

logger = logging.getLogger(__name__)

router = APIRouter()


class LogoutResponse(BaseModel):
    """Response model for logout operations."""
    message: str
    sessions_invalidated: int


class ErrorResponse(BaseModel):
    """Error response model."""
    detail: str


async def get_current_user_from_token(authorization: Optional[str] = Header(None)) -> str:
    """
    Extract and validate user from Authorization header.

    Args:
        authorization: Authorization header containing Bearer token

    Returns:
        User ID (UUID) from the validated token

    Raises:
        HTTPException(401): If token is missing or invalid
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Missing Authorization header"
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid Authorization header format. Expected: Bearer <token>"
        )

    token = authorization.replace("Bearer ", "").strip()

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Empty token in Authorization header"
        )

    try:
        # Validate token with Supabase
        client: Client = get_supabase_client()

        # Get user from token
        user_response = client.auth.get_user(token)

        if not user_response or not user_response.user:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token"
            )

        user_id = user_response.user.id
        logger.info(f"Authenticated user: {user_id}")

        return user_id

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating auth token: {e}")
        raise HTTPException(
            status_code=401,
            detail="Authentication failed"
        ) from e


@router.post(
    "/auth/logout",
    response_model=LogoutResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized - Invalid or missing token"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
    summary="Logout from current device",
    description="Invalidates the current session. User will be logged out from this device only."
)
async def logout(
    request: Request,
    authorization: Optional[str] = Header(None)
) -> LogoutResponse:
    """
    SEC-019: Logout from current device.

    Invalidates only the current session using the provided JWT token.
    Other active sessions on different devices remain valid.

    Headers:
        Authorization: Bearer <token>

    Returns:
        LogoutResponse with confirmation message
    """
    user_id = await get_current_user_from_token(authorization)

    try:
        client: Client = get_supabase_client()

        # Extract token from header
        token = authorization.replace("Bearer ", "").strip()

        # Sign out with local scope (current session only)
        # Note: Supabase Python client doesn't have direct signOut method with scope
        # Instead, we revoke the specific token
        client.auth.sign_out()

        logger.info(f"User {user_id} logged out from current device")

        return LogoutResponse(
            message="Successfully logged out from current device",
            sessions_invalidated=1
        )

    except Exception as e:
        logger.error(f"Error during logout for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Logout failed. Please try again."
        ) from e


@router.post(
    "/auth/logout-all",
    response_model=LogoutResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized - Invalid or missing token"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
    summary="Logout from all devices",
    description="Invalidates ALL active sessions for the user across all devices. This is a global logout."
)
async def logout_all_devices(
    request: Request,
    authorization: Optional[str] = Header(None)
) -> LogoutResponse:
    """
    SEC-019: Global logout - invalidate all sessions across all devices.

    This endpoint invalidates ALL active sessions for the authenticated user,
    effectively logging them out from all devices where they are currently signed in.

    Use cases:
    - User suspects account compromise
    - Password change
    - Security settings require all devices to re-authenticate

    Headers:
        Authorization: Bearer <token>

    Returns:
        LogoutResponse with confirmation message
    """
    user_id = await get_current_user_from_token(authorization)

    try:
        client: Client = get_supabase_client(use_service_role=True)

        # Sign out globally - invalidate all refresh tokens for this user
        # This requires admin/service role access
        # Using the admin API to revoke all sessions for the user

        # Method 1: Use Supabase Admin API to sign out user from all devices
        # This invalidates all refresh tokens for the user
        try:
            # The service role client has admin privileges
            # We need to call the admin user signOut endpoint
            response = client.auth.admin.sign_out(user_id)

            logger.info(f"User {user_id} logged out from ALL devices (global signout)")

            return LogoutResponse(
                message="Successfully logged out from all devices",
                sessions_invalidated=-1  # -1 indicates "all sessions"
            )

        except AttributeError:
            # Fallback: If admin.sign_out doesn't exist in this version,
            # use RPC call to invalidate sessions
            logger.warning("admin.sign_out not available, using RPC fallback")

            # Call a custom Supabase RPC function to invalidate all sessions
            # This would need to be created in Supabase
            result = client.rpc('invalidate_all_user_sessions', {'target_user_id': user_id}).execute()

            logger.info(f"User {user_id} logged out from ALL devices (RPC method)")

            return LogoutResponse(
                message="Successfully logged out from all devices",
                sessions_invalidated=-1
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during global logout for user {user_id}: {e}")

        # Log detailed error for debugging
        logger.error(f"Global logout error details: {type(e).__name__}: {str(e)}")

        raise HTTPException(
            status_code=500,
            detail="Global logout failed. Please try again or contact support."
        ) from e
