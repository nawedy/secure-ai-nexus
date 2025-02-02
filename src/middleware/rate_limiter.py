from fastapi import Request, HTTPException
from datetime import datetime, timedelta
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self):
        self.requests: Dict[str, List[datetime]] = {}
        self.limits = {
            "default": {"requests": 100, "window": 60},  # 100 requests per minute
            "auth": {"requests": 5, "window": 60},       # 5 login attempts per minute
            "api": {"requests": 1000, "window": 3600}    # 1000 API requests per hour
        }

    async def __call__(self, request: Request, call_next):
        client_ip = request.client.host
        path = request.url.path
        now = datetime.utcnow()

        # Determine rate limit based on path
        limit_key = "auth" if path.startswith("/auth") else "api"
        limit = self.limits.get(limit_key, self.limits["default"])

        # Clean old requests
        if client_ip in self.requests:
            self.requests[client_ip] = [
                ts for ts in self.requests[client_ip]
                if now - ts < timedelta(seconds=limit["window"])
            ]

        # Check rate limit
        if len(self.requests.get(client_ip, [])) >= limit["requests"]:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please try again later."
            )

        # Add request timestamp
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        self.requests[client_ip].append(now)

        return await call_next(request)
