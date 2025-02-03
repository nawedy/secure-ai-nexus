import logging
import logging.handlers
import json
from pathlib import Path
from datetime import datetime
import os
from typing import Dict, Any

class LogConfig:
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    LOG_DIR = Path('logs')
    MAX_BYTES = 10 * 1024 * 1024  # 10MB
    BACKUP_COUNT = 5

    def __init__(self):
        self.LOG_DIR.mkdir(exist_ok=True)
        self.setup_logging()

    def setup_logging(self):
        """Configure logging with file and console handlers"""
        # Create formatters
        console_formatter = logging.Formatter(self.LOG_FORMAT, self.DATE_FORMAT)
        json_formatter = JsonFormatter()

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging.INFO)

        # File handlers
        app_handler = logging.handlers.RotatingFileHandler(
            self.LOG_DIR / 'app.log',
            maxBytes=self.MAX_BYTES,
            backupCount=self.BACKUP_COUNT
        )
        app_handler.setFormatter(json_formatter)
        app_handler.setLevel(logging.INFO)

        error_handler = logging.handlers.RotatingFileHandler(
            self.LOG_DIR / 'error.log',
            maxBytes=self.MAX_BYTES,
            backupCount=self.BACKUP_COUNT
        )
        error_handler.setFormatter(json_formatter)
        error_handler.setLevel(logging.ERROR)

        # Security audit handler
        audit_handler = logging.handlers.RotatingFileHandler(
            self.LOG_DIR / 'audit.log',
            maxBytes=self.MAX_BYTES,
            backupCount=self.BACKUP_COUNT
        )
        audit_handler.setFormatter(json_formatter)
        audit_handler.setLevel(logging.INFO)

        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(console_handler)
        root_logger.addHandler(app_handler)
        root_logger.addHandler(error_handler)

        # Configure security audit logger
        audit_logger = logging.getLogger('security')
        audit_logger.addHandler(audit_handler)
        audit_logger.propagate = False

class JsonFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'process': record.process,
            'thread': record.thread,
        }

        if hasattr(record, 'extra'):
            log_data.update(record.extra)

        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_data)

class SecurityAuditLogger:
    """Security audit logging with structured data"""
    def __init__(self):
        self.logger = logging.getLogger('security')

    def log_security_event(self, event_type: str, details: Dict[str, Any], severity: str = 'INFO'):
        """Log a security event with structured data"""
        extra = {
            'event_type': event_type,
            'details': details,
            'severity': severity,
            'environment': os.getenv('ENVIRONMENT', 'production'),
        }

        self.logger.info(
            f"Security event: {event_type}",
            extra={'extra': extra}
        )

# Initialize logging configuration
log_config = LogConfig()
security_logger = SecurityAuditLogger()
