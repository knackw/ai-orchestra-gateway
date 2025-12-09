"""
Billing service for atomic credit deduction.

Handles credit transactions via Supabase RPC functions to ensure
atomic, race-condition-free billing operations.
"""

import logging

from fastapi import HTTPException

from app.core.database import get_supabase_client
from supabase import Client

logger = logging.getLogger(__name__)


class BillingService:
    """Service for managing credit billing operations."""

    @staticmethod
    async def deduct_credits(license_key: str, amount: int) -> int:
        """
        Atomically deduct credits from a license.

        Args:
            license_key: License key to deduct credits from
            amount: Number of credits to deduct

        Returns:
            New credit balance after deduction

        Raises:
            HTTPException(402): Insufficient credits
            HTTPException(403): Invalid, inactive, or expired license
            HTTPException(500): Database or unexpected error
        """
        try:
            client: Client = get_supabase_client()

            # Call Supabase RPC function for atomic deduction
            response = client.rpc(
                "deduct_credits",
                {"p_license_key": license_key, "p_amount": amount}
            ).execute()

            new_balance = response.data
            logger.info(
                f"Credits deducted successfully: {amount} credits, "
                f"new balance: {new_balance}"
            )
            return new_balance

        except Exception as e:
            error_message = str(e)

            # Map database errors to HTTP exceptions
            if "INSUFFICIENT_CREDITS" in error_message:
                logger.warning(f"Insufficient credits for license key: {license_key[:10]}...")
                raise HTTPException(
                    status_code=402,
                    detail="Insufficient credits to complete this request"
                )

            if "INVALID_LICENSE" in error_message:
                logger.warning(f"Invalid license key in billing: {license_key[:10]}...")
                raise HTTPException(
                    status_code=403,
                    detail="Invalid license key"
                )

            if "INACTIVE_LICENSE" in error_message:
                logger.warning(f"Inactive license in billing: {license_key[:10]}...")
                raise HTTPException(
                    status_code=403,
                    detail="License is not active"
                )

            if "EXPIRED_LICENSE" in error_message:
                logger.warning(f"Expired license in billing: {license_key[:10]}...")
                raise HTTPException(
                    status_code=403,
                    detail="License has expired"
                )

            # Unexpected database error
            logger.error(f"Database error during credit deduction: {error_message}")
            raise HTTPException(
                status_code=500,
                detail="Billing system error. Please try again later."
            )

    @staticmethod
    async def add_credits(license_key: str, credits_to_add: int) -> None:
        """
        Add credits to a license.
        
        Args:
            license_key: The license key to credit.
            credits_to_add: Amount of credits to add.
            
        Raises:
            HTTPException: If license not found or DB error.
        """
        client = get_supabase_client(use_service_role=True)  # Must be admin to add credits
        
        try:
            # Call PostgreSQL function 'add_credits'
            response = client.rpc(
                "add_credits",
                {"license_key_param": license_key, "credits_to_add": credits_to_add}
            ).execute()
            
            # Successful RPC returns None (void) but raises error if failed inside PG
            
        except Exception as e:
            error_message = str(e)
            logger.error(f"Failed to add credits: {error_message}")
            
            if "INVALID_LICENSE" in error_message:
                raise HTTPException(status_code=404, detail="License not found.")
            
            raise HTTPException(
                status_code=500,
                detail="Billing system error during credit addition."
            )
