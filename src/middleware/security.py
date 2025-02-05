from fastapi import Request, Response, HTTPException, status
from typing import Dict, Set
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to set security headers in HTTP responses.
    """

    blacklisted_ips: Set[str] = set()
    failed_attempts: Dict[str, int] = {}

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        """
        Sets security headers in the response and blocks blacklisted IP addresses.
        """
        client_ip = request.client.host

        # Check if the IP is blacklisted
        if client_ip in self.blacklisted_ips:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your IP address has been blocked due to suspicious activity.",
            )

        # Check the number of attempts from this ip
        if client_ip in self.failed_attempts:
            if self.failed_attempts[client_ip] > 5:
                self.blacklisted_ips.add(client_ip)
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Your IP address has been blocked due to suspicious activity.",
                )

        response: Response = await call_next(request)
        
        # Add security headers to response
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Content-Security-Policy"] = "default-src 'self'; object-src 'none'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        
        return response
