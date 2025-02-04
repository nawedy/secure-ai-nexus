from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 100, time_window: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.time_window = time_window
        self.request_counts = {}

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        client_ip = request.client.host
        current_time = int(request.scope["asgi.receive"]()
        if client_ip not in self.request_counts:
            self.request_counts[client_ip] = []

        # Remove old requests outside the time window
        self.request_counts[client_ip] = [
            time for time in self.request_counts[client_ip] if current_time - time < self.time_window
        ]

        # Check if request limit is exceeded
        if len(self.request_counts[client_ip]) >= self.max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests",
            )

        # Add current request time
        self.request_counts[client_ip].append(current_time)
        response = await call_next(request)
        return response
