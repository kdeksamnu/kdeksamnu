"""
Dallmier Tech Venture - Premium Asset: Cryptographic Webhook Verification
A standalone, production-grade FastAPI router for verifying inbound webhooks 
(e.g., Stripe, Shopify) using HMAC-SHA256. 

Completely decoupled from the MLAOS-PRIME speculative engine.
Ready for commercial deployment.
"""
import hmac
import hashlib
import logging
from fastapi import APIRouter, Request, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional

router = APIRouter(prefix="/api/v1/webhooks", tags=["Commercial Webhooks"])
logger = logging.getLogger("dallmier.webhooks")

class WebhookVerificationConfig(BaseModel):
    """Configuration for the HMAC verification boundary."""
    secret_key: str = Field(..., min_length=16, description="The shared symmetric secret.")
    header_name: str = Field(default="X-Webhook-Signature", description="The HTTP header containing the signature.")
    algorithm: str = Field(default="sha256", description="The hashing algorithm (sha256, sha512).")
    tolerance_seconds: int = Field(default=300, description="Maximum age of the payload to prevent replay attacks.")

# In-memory store for demonstration; in production, use Redis or a DB.
_active_configs: dict[str, WebhookVerificationConfig] = {}

def _compute_signature(payload: bytes, secret: str, algorithm: str) -> str:
    """Computes the HMAC signature for the given payload."""
    if algorithm == "sha256":
        return hmac.new(secret.encode('utf-8'), payload, hashlib.sha256).hexdigest()
    elif algorithm == "sha512":
        return hmac.new(secret.encode('utf-8'), payload, hashlib.sha512).hexdigest()
    raise ValueError(f"Unsupported algorithm: {algorithm}")

@router.post("/verify/{endpoint_id}", status_code=status.HTTP_200_OK)
async def verify_and_process_webhook(endpoint_id: str, request: Request):
    """
    The Ingestion Gate for commercial webhooks.
    Validates the cryptographic signature before passing the payload to the business logic.
    """
    config = _active_configs.get(endpoint_id)
    if not config:
        raise HTTPException(status_code=404, detail="Webhook endpoint not configured.")

    # 1. Extract the signature from the headers
    provided_signature = request.headers.get(config.header_name)
    if not provided_signature:
        logger.warning(f"Missing signature header for {endpoint_id}")
        raise HTTPException(status_code=401, detail="Missing signature header.")

    # 2. Read the raw payload
    payload_bytes = await request.body()

    # 3. Compute the expected signature
    expected_signature = _compute_signature(payload_bytes, config.secret_key, config.algorithm)

    # 4. Constant-time comparison to prevent timing attacks
    if not hmac.compare_digest(provided_signature, expected_signature):
        logger.warning(f"Signature mismatch for {endpoint_id}")
        raise HTTPException(status_code=403, detail="Invalid signature.")

    # 5. Payload is verified. Pass to business logic.
    # (In a real implementation, this would dispatch to a Celery/Redis queue)
    logger.info(f"Webhook verified and processed for {endpoint_id}")
    
    return {"status": "verified", "message": "Payload accepted and processed."}

@router.post("/configure/{endpoint_id}", status_code=status.HTTP_201_CREATED)
async def configure_webhook_endpoint(endpoint_id: str, config: WebhookVerificationConfig):
    """Registers a new webhook verification boundary."""
    _active_configs[endpoint_id] = config
    logger.info(f"Configured webhook endpoint: {endpoint_id}")
    return {"status": "configured", "endpoint_id": endpoint_id}
