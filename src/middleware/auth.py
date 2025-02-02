from google.auth import default
from google.cloud import secretmanager

# Remove Azure imports
# from azure.identity import DefaultAzureCredential

# Add rate limiting
from fastapi import Request, HTTPException
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
import jwt
from typing import Dict, List

class AuthMiddleware:
    def __init__(self):
        self.rate_limits: Dict[str, List[datetime]] = {}
        self.max_requests = 100  # Per minute
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

    async def __call__(self, request: Request, call_next):
        # Rate limiting
        client_ip = request.client.host
        now = datetime.utcnow()

        # Clean old requests
        if client_ip in self.rate_limits:
            self.rate_limits[client_ip] = [
                timestamp for timestamp in self.rate_limits[client_ip]
                if now - timestamp < timedelta(minutes=1)
            ]

        # Check rate limit
        if len(self.rate_limits.get(client_ip, [])) >= self.max_requests:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

        # Add request timestamp
        if client_ip not in self.rate_limits:
            self.rate_limits[client_ip] = []
        self.rate_limits[client_ip].append(now)

        return await call_next(request)
