"""
Integration Tests for Security Validation Components
Implements comprehensive testing of security validation functionality
"""

import pytest
import numpy as np
from pathlib import Path
import yaml
import asyncio
from datetime import datetime
from typing import Dict, Any, Generator
import tensorflow as tf
import json

from security.validation import SecurityValidator, SecurityValidationResult
from security.analyzer import SecurityAnalyzer
from ml.anomaly_detection import AnomalyDetector
from monitoring.metrics import MetricsCollector

class TestSecurityValidation:
    """Integration tests for security validation components"""

    @pytest.fixture(autouse=True)
    async def setup(self) -> Generator:
        """Setup test environment"""
        # Load test configuration
        config_path = Path("src/tests/ml/training/config.yaml")
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        # Initialize components
        self.security_validator = SecurityValidator()
        self.security_analyzer = SecurityAnalyzer()
        self.anomaly_detector = AnomalyDetector()
        self.metrics_collector = MetricsCollector()

        # Create test directories
        test_dirs = ["logs", "models", "data"]
        for dir_name in test_dirs:
            Path(dir_name).mkdir(exist_ok=True)

        # Generate test data and models
        await self._setup_test_environment()

        yield

        # Cleanup
        await self._cleanup_test_environment()

    async def test_authentication_validation(self) -> None:
        """Test authentication validation"""
        # Create test auth data
        auth_data = {
            "token": "test_token",
            "user": {
                "id": 1,
                "role": "admin",
                "permissions": ["read", "write"]
            },
            "session": {
                "id": "session_1",
                "created_at": datetime.now().isoformat()
            }
        }

        # Perform authentication validation
        auth_result = await self.security_validator._validate_authentication(
            auth_data,
            self._get_security_config()
        )

        # Validate results
        assert isinstance(auth_result, dict)
        assert "token_valid" in auth_result
        assert "user_valid" in auth_result
        assert "session_valid" in auth_result
        assert "permissions_valid" in auth_result
        assert isinstance(auth_result["token_valid"], bool)

    async def test_input_validation(self) -> None:
        """Test input validation"""
        # Create test input data
        input_data = {
            "api_requests": [
                {
                    "method": "POST",
                    "endpoint": "/api/data",
                    "body": {"key": "value"},
                    "headers": {"Content-Type": "application/json"}
                }
            ],
            "form_data": {
                "username": "test_user",
                "email": "test@example.com"
            }
        }

        # Perform input validation
        validation_result = await self.security_validator._validate_input(
            input_data,
            self._get_security_config()
        )

        # Validate results
        assert isinstance(validation_result, dict)
        assert "sanitization_results" in validation_result
        assert "validation_errors" in validation_result
        assert "risk_assessment" in validation_result

    async def test_access_control_validation(self) -> None:
        """Test access control validation"""
        # Create test access control data
        access_data = {
            "user": {
                "id": 1,
                "role": "user",
                "permissions": ["read"]
            },
            "resource": {
                "id": "resource_1",
                "type": "document",
                "required_permissions": ["read"]
            },
            "action": "view"
        }

        # Perform access control validation
        access_result = await self.security_validator._validate_access_control(
            access_data,
            self._get_security_config()
        )

        # Validate results
        assert isinstance(access_result, dict)
        assert "access_granted" in access_result
        assert "permission_check" in access_result
        assert "role_check" in access_result

    async def test_encryption_validation(self) -> None:
        """Test encryption validation"""
        # Create test encryption data
        encryption_data = {
            "data": "sensitive_data",
            "encryption_method": "AES-256",
            "key_management": {
                "rotation_period": 30,
                "key_strength": 256
            }
        }

        # Perform encryption validation
        encryption_result = await self.security_validator._validate_encryption(
            encryption_data,
            self._get_security_config()
        )

        # Validate results
        assert isinstance(encryption_result, dict)
        assert "encryption_valid" in encryption_result
        assert "key_management_valid" in encryption_result
        assert "recommendations" in encryption_result

    async def test_security_scanning(self) -> None:
        """Test security scanning functionality"""
        # Create test scan data
        scan_data = {
            "code_snippets": ["test code"],
            "dependencies": ["package1", "package2"],
            "configurations": {
                "api": {"rate_limit": 100},
                "auth": {"session_timeout": 3600}
            }
        }

        # Perform security scan
        scan_result = await self.security_validator._perform_security_scan(
            scan_data,
            self._get_security_config()
        )

        # Validate results
        assert isinstance(scan_result, dict)
        assert "vulnerabilities" in scan_result
        assert "risk_assessment" in scan_result
        assert "recommendations" in scan_result

    async def test_ml_security_insights(self) -> None:
        """Test ML-driven security insights"""
        # Create test security data
        security_data = {
            "metrics": np.random.random((100, 10)),
            "events": [
                {"type": "auth_failure", "timestamp": datetime.now()}
                for _ in range(10)
            ]
        }

        # Generate security insights
        insights = await self.security_validator._generate_security_insights(
            security_data,
            self._get_ml_config()
        )

        # Validate insights
        assert isinstance(insights, dict)
        assert "patterns" in insights
        assert "anomalies" in insights
        assert "risk_factors" in insights
        assert "recommendations" in insights

    async def test_comprehensive_security_validation(self) -> None:
        """Test comprehensive security validation"""
        # Create test security data
        security_data = {
            "auth": {
                "token": "test_token",
                "user": {"id": 1, "role": "user"}
            },
            "input": {
                "api_requests": [{"method": "GET", "endpoint": "/test"}]
            },
            "access": {
                "user": {"id": 1, "permissions": ["read"]},
                "resource": {"id": "res_1", "type": "document"}
            },
            "encryption": {
                "method": "AES-256",
                "key_management": {"rotation_period": 30}
            }
        }

        # Perform comprehensive validation
        result = await self.security_validator.validate_security(
            security_data,
            self._get_security_config()
        )

        # Validate comprehensive results
        assert isinstance(result, SecurityValidationResult)
        assert isinstance(result.success, bool)
        assert isinstance(result.auth_results, dict)
        assert isinstance(result.input_validation_results, dict)
        assert isinstance(result.access_control_results, dict)
        assert isinstance(result.encryption_results, dict)
        assert isinstance(result.vulnerabilities, list)
        assert isinstance(result.ml_insights, dict)
        assert isinstance(result.recommendations, list)

    async def _setup_test_environment(self) -> None:
        """Setup test environment with necessary data and models"""
        # Create dummy ML models for testing
        input_shape = (self.config["input_dim"],)

        # Create and save security analyzer model
        security_model = tf.keras.Sequential([
            tf.keras.layers.Dense(64, activation='relu', input_shape=input_shape),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dense(16, activation='relu'),
            tf.keras.layers.Dense(1, activation='sigmoid')
        ])
        security_model.save("models/security_analyzer.h5")

        # Create test data
        test_data = {
            "auth_logs": [
                {
                    "timestamp": datetime.now().isoformat(),
                    "event_type": "login",
                    "success": True
                }
                for _ in range(100)
            ],
            "security_events": [
                {
                    "timestamp": datetime.now().isoformat(),
                    "type": "security_scan",
                    "findings": []
                }
                for _ in range(50)
            ]
        }

        # Save test data
        with open("data/test_security_data.json", "w") as f:
            json.dump(test_data, f)

    async def _cleanup_test_environment(self) -> None:
        """Clean up test environment"""
        import shutil

        # Remove test directories
        test_dirs = ["logs", "models", "data"]
        for dir_name in test_dirs:
            shutil.rmtree(dir_name, ignore_errors=True)

    def _get_security_config(self) -> Dict[str, Any]:
        """Get security configuration"""
        return {
            "auth_rules": {
                "token_expiry": 3600,
                "password_policy": {
                    "min_length": 8,
                    "require_special": True,
                    "require_numbers": True
                },
                "session_timeout": 1800
            },
            "input_validation_rules": {
                "sanitize_input": True,
                "max_request_size": 1024 * 1024,
                "allowed_content_types": [
                    "application/json",
                    "application/x-www-form-urlencoded"
                ]
            },
            "access_control_rules": {
                "default_policy": "deny",
                "role_hierarchy": {
                    "admin": ["user", "guest"],
                    "user": ["guest"]
                }
            },
            "encryption_rules": {
                "minimum_key_length": 256,
                "key_rotation_period": 30,
                "allowed_algorithms": ["AES-256", "RSA-2048"]
            },
            "scanning_rules": {
                "scan_frequency": 24,
                "vulnerability_threshold": "medium",
                "auto_remediation": False
            }
        }

    def _get_ml_config(self) -> Dict[str, Any]:
        """Get ML configuration"""
        return {
            "model_paths": {
                "security": "models/security_analyzer.h5"
            },
            "inference_batch_size": 32,
            "confidence_threshold": 0.8,
            "analysis_window": 3600
        }
