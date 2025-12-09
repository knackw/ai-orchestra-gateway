"""
Usage logging service.

Handles recording of API usage details (tokens, credits, prompts) to the
immutable usage_logs table for audit and analytics.
"""

import logging
from typing import Optional

from app.core.database import get_supabase_client

logger = logging.getLogger(__name__)


class UsageService:
    """Service for logging API usage."""

    @staticmethod
    async def log_usage(
        license_id: str,
        app_id: str,
        tenant_id: str,
        tokens_used: int,
        credits_deducted: int,
        provider: str,
        model: str,
        prompt_length: int,
        pii_detected: bool,
        response_status: str = "success",
        error_message: Optional[str] = None
    ) -> None:
        """
        Log API usage to the database.

        This method is designed to be fire-and-forget or awaited, but should
        not block the critical path if possible (though Supabase-py is sync/http based).
        In FastAPI, this can be run as a background task.

        Args:
            license_id: ID of the license used
            app_id: ID of the app used
            tenant_id: ID of the tenant
            tokens_used: Number of tokens consumed
            credits_deducted: Credits deducted
            provider: AI provider name (e.g., 'anthropic')
            model: Model name used
            prompt_length: Length of the prompt (chars)
            pii_detected: Whether PII was detected
            response_status: 'success' or 'error'
            error_message: Optional error details
        """
        try:
            client = get_supabase_client(use_service_role=True)
            
            log_entry = {
                "license_id": license_id,
                "app_id": app_id,
                "tenant_id": tenant_id,
                "tokens_used": tokens_used,
                "credits_deducted": credits_deducted,
                "provider": provider,
                "model": model,
                "prompt_length": prompt_length,
                "pii_detected": pii_detected,
                "response_status": response_status,
                "error_message": error_message
            }
            
            # Execute insert
            client.table("usage_logs").insert(log_entry).execute()
            
            logger.info(
                f"Usage logged for tenant {tenant_id}: {tokens_used} tokens"
            )

        except Exception as e:
            # We log the error but don't raise it to prevent crashing the API
            # response if logging fails (fail-open for logging)
            logger.error(f"Failed to log usage: {e}")
