from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from .metrics import MetricsManager
from .logging import SecureLogger
import time
from typing import Callable
import logging

logger = logging.getLogger(__name__)

class MonitoringMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.metrics = MetricsManager()
        self.secure_logger = SecureLogger()

    async def dispatch(self, request: Request, call_next: Callable):
        start_time = time.time()

        try:
            # Get request details
            path = request.url.path
            method = request.method
            user_id = request.state.user.id if hasattr(request.state, 'user') else None

            # Process request
            response = await call_next(request)

            # Calculate duration
            duration = time.time() - start_time

            # Record metrics
            await self.metrics.record_request(
                model_name=request.path_params.get('model_name', 'unknown'),
                status='success',
                duration=duration
            )

            # Log access
            if path.startswith('/model'):
                await self.secure_logger.log_model_access(
                    model_name=request.path_params.get('model_name', 'unknown'),
                    user_id=user_id,
                    action=method,
                    status=response.status_code
                )

            return response

        except Exception as e:
            # Record error metrics
            duration = time.time() - start_time
            await self.metrics.record_request(
                model_name=request.path_params.get('model_name', 'unknown'),
                status='error',
                duration=duration
            )

            # Log error
            await self.secure_logger.log_security_event(
                event_type='request_error',
                severity='error',
                details={'error': str(e)},
                user_id=user_id
            )

            raise
