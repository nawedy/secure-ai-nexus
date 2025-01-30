from typing import Any, Dict, List
from pydantic import BaseModel, validator
import re
import logging
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class InputValidation(BaseModel):
    max_length: int = 32768  # Maximum input length
    allowed_patterns: Dict[str, str] = {
        'text': r'^[\w\s\.,\-\?\!]+$',
        'code': r'^[\w\s\.,\-\{\}\[\]\(\)\n\t\"\']+$'
    }
    blocked_patterns: List[str] = [
        r'(?i)(<script|javascript:|data:)',  # XSS patterns
        r'(?i)(exec\s+|system\s+|eval\s+)',  # Code injection
        r'(?i)(drop\s+table|delete\s+from)',  # SQL injection
    ]

class OutputValidation(BaseModel):
    max_length: int = 65536  # Maximum output length
    sensitive_patterns: List[str] = [
        r'\b\d{16}\b',  # Credit card numbers
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
        r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
    ]

class IOSecurityValidator:
    def __init__(self):
        self.input_validation = InputValidation()
        self.output_validation = OutputValidation()

    async def validate_input(self, data: str, input_type: str = 'text') -> str:
        """Validate and sanitize input"""
        try:
            # Check length
            if len(data) > self.input_validation.max_length:
                raise HTTPException(status_code=400, detail="Input exceeds maximum length")

            # Check against allowed patterns
            pattern = self.input_validation.allowed_patterns.get(input_type)
            if pattern and not re.match(pattern, data):
                raise HTTPException(status_code=400, detail="Invalid input format")

            # Check for blocked patterns
            for pattern in self.input_validation.blocked_patterns:
                if re.search(pattern, data):
                    logger.warning(f"Blocked pattern detected in input: {pattern}")
                    raise HTTPException(status_code=400, detail="Invalid input detected")

            return data

        except Exception as e:
            logger.error(f"Input validation failed: {str(e)}")
            raise HTTPException(status_code=400, detail="Input validation failed")

    async def validate_output(self, data: str) -> str:
        """Validate and sanitize output"""
        try:
            # Check length
            if len(data) > self.output_validation.max_length:
                logger.warning("Output exceeded maximum length")
                data = data[:self.output_validation.max_length]

            # Check for sensitive data
            for pattern in self.output_validation.sensitive_patterns:
                if re.search(pattern, data):
                    logger.warning("Sensitive data detected in output")
                    data = re.sub(pattern, '[REDACTED]', data)

            return data

        except Exception as e:
            logger.error(f"Output validation failed: {str(e)}")
            raise HTTPException(status_code=500, detail="Output validation failed")
