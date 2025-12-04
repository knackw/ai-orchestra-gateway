"""
Billing service for atomic credit deduction.

Handles credit transactions via Supabase RPC functions to ensure
atomic, race-condition-free billing operations.
"""

import logging
from typing import Optional

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
