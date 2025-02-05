from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
import time
from typing import Dict, List


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    Middleware for rate limiting incoming requests based on IP and endpoint.
    """

    def __init__(self, app, max_requests: int = 100, time_window: int = 60, login_max_requests: int = 5, login_time_window: int = 60):
        """
        Initializes the RateLimiterMiddleware.

        Args:
            app: The FastAPI application.
            max_requests: The maximum number of requests allowed within the time window.
            time_window: The time window (in seconds) for general API rate limiting.
            login_max_requests: The maximum number of login attempts allowed within the login time window.
            login_time_window: The time window (in seconds) for login attempts rate limiting.
        """
        super().__init__(app)
        self.max_requests = max_requests
        self.time_window = time_window
        self.login_max_requests = login_max_requests
        self.login_time_window = login_time_window
        self.request_counts: Dict[str, Dict[str, List[int]]] = {}

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        """
        Dispatches the incoming request and enforces rate limiting based on the endpoint.

        Args:
            request: The incoming request.
            call_next: The next middleware or endpoint in the pipeline.
        """
        client_ip = request.client.host
        endpoint = request.url.path

        if client_ip not in self.request_counts:
            self.request_counts[client_ip] = {}

        # Separate rate limiting for login attempts
        if endpoint == "/api/auth/login":
            response = await self.handle_login_rate_limiting(request, call_next, client_ip, endpoint)
        else:
            response = await self.handle_api_rate_limiting(request, call_next, client_ip, endpoint)

        return response

    async def handle_login_rate_limiting(self, request: Request, call_next: RequestResponseEndpoint, client_ip: str, endpoint: str):
        """Handles rate limiting specifically for login attempts."""
        return await self.handle_rate_limiting(request, call_next, client_ip, endpoint, self.login_max_requests, self.login_time_window)
    
    async def handle_api_rate_limiting(self, request: Request, call_next: RequestResponseEndpoint, client_ip: str, endpoint: str):
        """Handles rate limiting for general API requests."""
        return await self.handle_rate_limiting(request, call_next, client_ip, endpoint, self.max_requests, self.time_window)


    async def handle_rate_limiting(self, request: Request, call_next: RequestResponseEndpoint, client_ip: str, endpoint: str, max_requests:int, time_window: int):
        """
        Handles rate limiting logic for different types of requests.
        """
        if endpoint not in self.request_counts[client_ip]:
            self.request_counts[client_ip][endpoint] = []
        current_time = int(time.time())
        # Remove old requests outside the time window
        self.request_counts[client_ip][endpoint] = [
            request_time for request_time in self.request_counts[client_ip][endpoint] if current_time - request_time < time_window
        ]

        if len(self.request_counts[client_ip][endpoint]) >= max_requests:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many requests")
        self.request_counts[client_ip][endpoint].append(current_time)
        response = await call_next(request)
        return response
