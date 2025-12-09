import logging
import stripe
from fastapi import APIRouter, Request, Header, HTTPException, status
from app.core import config
from app.services.billing import BillingService

logger = logging.getLogger(__name__)

router = APIRouter()
settings = config.settings

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

@router.post("/stripe", include_in_schema=False)
async def stripe_webhook(request: Request, stripe_signature: str = Header(None)):
    """
    Handle Stripe webhooks.
    
    Primarily listens for 'checkout.session.completed' to add credits.
    """
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET
    payload = await request.body()
    
    if not webhook_secret:
        logger.error("Stripe webhook secret is not configured.")
        raise HTTPException(status_code=500, detail="Webhook configuration error")

    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, webhook_secret
        )
    except ValueError as e:
        # Invalid payload
        logger.error(f"Invalid payload error: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        logger.error(f"Signature verification error: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        logger.error(f"Unexpected error constructing event: {e}")
        raise HTTPException(status_code=400, detail="Error constructing event")

    # Handle the event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        await handle_checkout_session_completed(session)

    return {"status": "success"}


async def handle_checkout_session_completed(session: dict):
    """
    Process successful checkout session.
    
    Extracts license key from metadata and adds credits.
    """
    # Try to find license key in client_reference_id or metadata
    license_key = session.get("client_reference_id")
    metadata = session.get("metadata", {})
    
    if not license_key and metadata:
        license_key = metadata.get("license_key")
        
    if not license_key:
        logger.error(f"No license_key found in Stripe session {session.get('id')}")
        return

    # Determine amount of credits
    # Ideally, this should come from the product/price metadata.
    # For MVP, we assume metadata contains 'credits' or valid fallback.
    credits_to_add = 0
    if metadata and "credits" in metadata:
        try:
            credits_to_add = int(metadata["credits"])
        except ValueError:
            pass
            
    # Fallback: check custom fields or line items? 
    # For MVP simplicity, let's enforce passing 'credits' in metadata
    if credits_to_add <= 0:
         logger.error(f"No valid credits amount found in Stripe session {session.get('id')}")
         return

    logger.info(f"Adding {credits_to_add} credits to license {license_key} from Stripe session {session.get('id')}")
    
    try:
        await BillingService.add_credits(license_key, credits_to_add)
        logger.info(f"Successfully added credits to {license_key}")
    except HTTPException as e:
        logger.error(f"Failed to add credits to {license_key}: {e.detail}")
    except Exception as e:
        logger.error(f"Unexpected error adding credits to {license_key}: {e}")
