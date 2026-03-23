"""GitHub Webhook Payload Parsing and Validation."""

import hmac
import hashlib
from typing import Any
from fastapi import Request, HTTPException
from app.config import settings
import structlog

logger = structlog.get_logger()

async def verify_signature(request: Request) -> bytes:
    """Verify the HMAC signature of the incoming GitHub webhook."""
    signature_header = request.headers.get("X-Hub-Signature-256")
    if not signature_header:
        raise HTTPException(status_code=401, detail="Missing signature header")
        
    if not settings.github_webhook_secret:
        logger.warning("Webhook secret is not configured, skipping signature validation")
        return await request.body()
        
    body = await request.body()
    secret = settings.github_webhook_secret.get_secret_value().encode("utf-8")
    expected_signature = "sha256=" + hmac.new(secret, body, hashlib.sha256).hexdigest()
    
    if not hmac.compare_digest(signature_header, expected_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
        
    return body

async def process_pull_request_event(payload: dict[str, Any]) -> None:
    """Process a pull request webhook event."""
    action = payload.get("action")
    if action not in ["opened", "synchronize"]:
        await logger.adebug("Ignoring PR action", action=action)
        return
        
    pr_number = payload["pull_request"]["number"]
    repo_full_name = payload["repository"]["full_name"]
    installation_id = payload["installation"]["id"]
    
    await logger.ainfo(
        "Received PR event", 
        action=action, 
        repo=repo_full_name, 
        pr_number=pr_number
    )
    
    # RAG pipeline and agent review graph will be orchestrated here.
