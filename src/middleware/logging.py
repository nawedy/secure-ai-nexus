from fastapi import Request, Response
import logging
import time
from typing import Callable, Any
import uuid

logger = logging.getLogger(__name__)


async def logging_middleware(request: Request, call_next: Callable) -> Any:
    """Middleware to log all incoming requests and their corresponding responses.

    Args:
        request (Request): The incoming FastAPI Request object.
        call_next (Callable): The next callable in the middleware stack.

    Returns:
        Any: The response from the next middleware or the endpoint.

    Raises:
        Exception: If any error occurs during the request processing, it is raised after logging the error.

    Example:
        
    """
    request_id = str(uuid.uuid4())
    start_time = time.time()

    # Log request
    logger.info(
        "Incoming request",
        extra={
            'extra': {
                'request_id': request_id,
                'method': request.method,
                'url': str(request.url),
                'client_ip': request.client.host,
                'headers': dict(request.headers),
            }
        }
    )

    try:
        response = await call_next(request)
        duration = time.time() - start_time

        # Log response
        logger.info(
            "Request completed",
            extra={
                'extra': {
                    'request_id': request_id,
                    'status_code': response.status_code,
                    'duration': duration,
                }
            }
        )
        return response

    except Exception as e:
        logger.error(
            "Request failed",
            extra={
                'extra': {
                    'request_id': request_id,
                    'error': str(e),
                    'duration': time.time() - start_time,
                }
            },
            exc_info=True
        )
        raise
