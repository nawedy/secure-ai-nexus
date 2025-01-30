from fastapi import Security, HTTPException
from fastapi.security.api_key import APIKeyHeader
import secrets

API_KEY = secrets.token_urlsafe(32)  # Generate on startup for MVP
api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Invalid API key"
        )
    return api_key 