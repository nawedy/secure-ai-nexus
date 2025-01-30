from typing import Dict, List, Optional
from pydantic import BaseModel
import logging
from azure.storage.blob import BlobServiceClient
import hashlib
import json
from .advanced_scanning import AdvancedModelScanner

logger = logging.getLogger(__name__)

class ValidationResult(BaseModel):
    passed: bool
    issues: List[str] = []
    risk_score: float
    metadata: Dict = {}

class ModelValidator:
    def __init__(self, blob_service_client: BlobServiceClient):
        self.blob_service_client = blob_service_client
        self.max_model_size = 10 * 1024 * 1024 * 1024  # 10GB
        self.allowed_formats = ['pt', 'safetensors', 'bin']
        self.advanced_scanner = AdvancedModelScanner(self.model_security)

    async def validate_model(self, model_data: bytes, metadata: Dict) -> ValidationResult:
        """Validate model before deployment"""
        issues = []

        # Add advanced scanning
        scan_results = await self.advanced_scanner.scan_model(model_data, metadata)

        if scan_results["security_score"] < 80.0:
            issues.append("Model failed security scan")
            issues.extend([t["details"] for t in scan_results["threats_found"]])

        # Size check
        if len(model_data) > self.max_model_size:
            issues.append("Model exceeds maximum size limit")

        # Format validation
        model_format = metadata.get('format', '')
        if model_format not in self.allowed_formats:
            issues.append(f"Unsupported model format: {model_format}")

        # Integrity check
        if not self._verify_integrity(model_data, metadata.get('hash')):
            issues.append("Model integrity check failed")

        # Security scan
        security_issues = await self._security_scan(model_data)
        issues.extend(security_issues)

        # Calculate risk score
        risk_score = len(issues) / 10  # Simple scoring for MVP

        return ValidationResult(
            passed=len(issues) == 0,
            issues=issues,
            risk_score=risk_score,
            metadata=metadata
        )

    def _verify_integrity(self, model_data: bytes, expected_hash: Optional[str]) -> bool:
        """Verify model integrity using SHA-256"""
        if not expected_hash:
            return False

        actual_hash = hashlib.sha256(model_data).hexdigest()
        return actual_hash == expected_hash

    async def _security_scan(self, model_data: bytes) -> List[str]:
        """Basic security scan of model"""
        issues = []

        # Size anomaly check
        if len(model_data) < 1000:
            issues.append("Model size suspiciously small")

        # Basic content checks
        try:
            # Check for suspicious patterns
            data_str = str(model_data)
            suspicious_patterns = ['exec(', 'eval(', 'import os', 'system(']
            for pattern in suspicious_patterns:
                if pattern in data_str:
                    issues.append(f"Suspicious pattern detected: {pattern}")
        except Exception as e:
            logger.error(f"Security scan failed: {str(e)}")
            issues.append("Security scan failed")

        return issues
