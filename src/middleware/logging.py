from fastapi import Request
import logging
import time
import json
from typing import Callable
import uuid

logger = logging.getLogger(__name__)

async def logging_middleware(request: Request, call_next: Callable):
    """Middleware to log all requests and responses"""
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
