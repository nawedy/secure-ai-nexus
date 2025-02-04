"""
This module contains the metrics middleware for collecting and recording metrics about incoming HTTP requests.
"""

from fastapi import Request
import time
from ..monitoring.metrics import MetricsManager
from typing import Callable, Any


async def metrics_middleware(request: Request, call_next: Callable[[Request], Any]) -> Any:
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
    response = await call_next(request)
    duration = time.time() - start_time
    MetricsManager.record_request(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code,
        duration=duration
    )
    return response
