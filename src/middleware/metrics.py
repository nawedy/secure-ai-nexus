"""
This module contains the metrics middleware for collecting and recording metrics about incoming HTTP requests.
"""

from fastapi import Request
import time
from starlette.middleware import Middleware
from starlette.types import RequestResponseEndpoint


async def metrics_middleware(request: Request, call_next: RequestResponseEndpoint) :
    """
    Collects and records metrics about incoming HTTP requests.

    Measures the duration of each request and records various metrics, including:
        - Request method (e.g., GET, POST)
        - Endpoint (e.g., /api/users)
        - Status code (e.g., 200, 404)
        - Duration (in seconds)

    Uses the MetricsManager to record the collected metrics.

    Args:
        request: The incoming HTTP request.
        call_next: The next callable in the middleware chain.

    Returns:
        Any: The HTTP response after processing.
    """
    start_time = time.time()

    # Call the next middleware or endpoint
    response = await call_next(request)

    # Measure the duration of the request
    duration = time.time() - start_time
    # MetricsManager.record_request(
    #     method=request.method,
    #     endpoint=request.url.path,
    #     status=response.status_code,
    #     duration=duration
    # )
    return response
