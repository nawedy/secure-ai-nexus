import logging
from logging.handlers import RotatingFileHandler
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace
from typing import Optional, Dict
import json
import os
from datetime import datetime

class SecureLogger:
    def __init__(self):
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)

        # Configure Azure Monitor
        configure_azure_monitor(
            connection_string=os.getenv("AZURE_MONITOR_CONNECTION_STRING")
        )

        # Configure basic logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Set up file handler
        file_handler = RotatingFileHandler(
            'logs/secureai.log',
            maxBytes=10485760,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))

        # Get root logger
        self.logger = logging.getLogger('secureai')
        self.logger.addHandler(file_handler)

        # Initialize tracer
        self.tracer = trace.get_tracer(__name__)

    def log_security_event(self,
                          event_type: str,
                          severity: str,
                          details: Dict,
                          user_id: Optional[str] = None):
        """Log security events with proper formatting"""
        try:
            event = {
                'event_type': event_type,
                'severity': severity,
                'details': details,
                'user_id': user_id,
                'timestamp': datetime.utcnow().isoformat()
            }

            # Log to file
            self.logger.warning(json.dumps(event)) if severity == 'warning' \
                else self.logger.error(json.dumps(event))

            # Create span for tracing
            with self.tracer.start_as_current_span("security_event") as span:
                span.set_attribute("event_type", event_type)
                span.set_attribute("severity", severity)
                span.set_attribute("user_id", user_id)

        except Exception as e:
            self.logger.error(f"Failed to log security event: {str(e)}")

    def log_model_access(self,
                        model_name: str,
                        user_id: str,
                        action: str,
                        status: str):
        """Log model access events"""
        try:
            event = {
                'model_name': model_name,
                'user_id': user_id,
                'action': action,
                'status': status,
                'timestamp': datetime.utcnow().isoformat()
            }

            self.logger.info(json.dumps(event))

            # Create span for tracing
            with self.tracer.start_as_current_span("model_access") as span:
                span.set_attribute("model_name", model_name)
                span.set_attribute("user_id", user_id)
                span.set_attribute("action", action)
                span.set_attribute("status", status)

        except Exception as e:
            self.logger.error(f"Failed to log model access: {str(e)}")
