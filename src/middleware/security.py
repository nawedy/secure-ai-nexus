from fastapi import Request, status
from fastapi.responses import JSONResponse
import logging
import re
from typing import List, Dict
import ipaddress
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

logger = logging.getLogger(__name__)

class SecurityMiddleware:
    """
    Enhanced security middleware with multiple protection layers.
    """

    def __init__(self):
        self.blocked_ips: List[str] = []
        self.suspicious_patterns: List[str] = [
            r"(?i)(union|select|insert|delete|drop|update)\s+",
            r"(?i)script>",
            r"(?i)javascript:",
            r"(?i)eval\(",
        ]
        self.request_logs: Dict[str, List[dict]] = {}

    async def __call__(self, request: Request, call_next):
        client_ip = request.client.host

        # Check IP blocking
        if self.is_ip_blocked(client_ip):
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "Access denied"}
            )

        # Check for suspicious patterns
        if await self.has_suspicious_patterns(request):
            self.block_ip(client_ip)
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "Suspicious request detected"}
            )

        # Add security headers
        response = await call_next(request)
        return self.add_security_headers(response)

    def is_ip_blocked(self, ip: str) -> bool:
        """Check if an IP is blocked."""
        return ip in self.blocked_ips

    def block_ip(self, ip: str):
        """Block an IP address."""
        if ip not in self.blocked_ips:
            self.blocked_ips.append(ip)
            logger.warning(f"Blocked IP: {ip}")

    async def has_suspicious_patterns(self, request: Request) -> bool:
        """Check for suspicious patterns in request."""
        # Check URL
        url = str(request.url)
        for pattern in self.suspicious_patterns:
            if re.search(pattern, url):
                return True

        # Check body for POST/PUT requests
        if request.method in ["POST", "PUT"]:
            try:
                body = await request.json()
                body_str = str(body)
                for pattern in self.suspicious_patterns:
                    if re.search(pattern, body_str):
                        return True
            except:
                pass

        return False

    def add_security_headers(self, response):
        """Add security headers to response."""
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response

def setup_security_middleware(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://secureai.example.com"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"]
    )
