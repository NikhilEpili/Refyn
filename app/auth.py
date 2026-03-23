"""GitHub App authentication utilities."""

import time
import jwt
from typing import Any
import httpx
from app.config import settings
import structlog

logger = structlog.get_logger()

def generate_jwt() -> str:
    """Generate a JWT for authenticating as the GitHub App."""
    if not settings.github_app_id or not settings.github_private_key_path:
        raise ValueError("GitHub App configuration missing")
        
    with open(settings.github_private_key_path, "r") as f:
        private_key = f.read()
        
    now = int(time.time())
    payload = {
        "iat": now - 60,  # Issued 60 seconds ago to handle clock drift
        "exp": now + (10 * 60),  # Valid for 10 minutes (maximum allowed)
        "iss": settings.github_app_id
    }
    
    encoded_jwt = jwt.encode(payload, private_key, algorithm="RS256")
    return encoded_jwt

async def get_installation_token(installation_id: int) -> str:
    """Fetch an installation access token for a specific repository installation."""
    jwt_token = generate_jwt()
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data["token"]
