from typing import Dict, List, Optional
import logging
import hashlib
import json
import aiohttp
import tensorflow as tf
from azure.storage.blob import BlobServiceClient
from .security import ModelSecurity

logger = logging.getLogger(__name__)

class AdvancedModelScanner:
    def __init__(self, model_security: ModelSecurity):
        self.model_security = model_security
        self.threat_db_url = "https://api.secureai.example.com/threats"
        self.scan_results_container = "model-scan-results"

    async def scan_model(self, model_data: bytes, metadata: Dict) -> Dict:
        """Perform comprehensive model security scan"""
        try:
            scan_results = {
                "security_score": 0.0,
                "threats_found": [],
                "recommendations": [],
                "metadata_analysis": {}
            }

            # Perform multiple scanning phases
            await self._scan_binary_content(model_data, scan_results)
            await self._analyze_metadata(metadata, scan_results)
            await self._check_known_vulnerabilities(model_data, scan_results)
            await self._validate_model_structure(model_data, scan_results)

            # Calculate final security score
            scan_results["security_score"] = self._calculate_security_score(scan_results)

            # Store scan results
            await self._store_scan_results(scan_results)

            return scan_results

        except Exception as e:
            logger.error(f"Model scanning failed: {str(e)}")
            raise

    async def _scan_binary_content(self, model_data: bytes, results: Dict):
        """Scan binary content for known malicious patterns"""
        try:
            # Calculate model hash
            model_hash = hashlib.sha256(model_data).hexdigest()

            # Check for known malicious patterns
            patterns = [
                b"exec(",
                b"eval(",
                b"import os",
                b"system(",
                b"subprocess"
            ]

            for pattern in patterns:
                if pattern in model_data:
                    results["threats_found"].append({
                        "type": "malicious_code",
                        "pattern": pattern.decode(),
                        "severity": "critical"
                    })

        except Exception as e:
            logger.error(f"Binary content scan failed: {str(e)}")
            results["threats_found"].append({
                "type": "scan_error",
                "details": str(e),
                "severity": "high"
            })

    async def _analyze_metadata(self, metadata: Dict, results: Dict):
        """Analyze model metadata for security issues"""
        required_fields = ["version", "creator", "creation_date", "intended_use"]

        # Check for missing required fields
        missing_fields = [field for field in required_fields if field not in metadata]
        if missing_fields:
            results["metadata_analysis"]["missing_fields"] = missing_fields
            results["recommendations"].append({
                "type": "metadata",
                "details": f"Add missing metadata fields: {', '.join(missing_fields)}"
            })

        # Check for suspicious metadata values
        suspicious_patterns = [
            "test",
            "temp",
            "unknown",
            "none",
            "n/a"
        ]

        for key, value in metadata.items():
            if str(value).lower() in suspicious_patterns:
                results["metadata_analysis"]["suspicious_values"] = {
                    key: value
                }

    async def _check_known_vulnerabilities(self, model_data: bytes, results: Dict):
        """Check model against known vulnerability database"""
        try:
            model_hash = hashlib.sha256(model_data).hexdigest()

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.threat_db_url}/check/{model_hash}"
                ) as response:
                    if response.status == 200:
                        threat_data = await response.json()
                        if threat_data["threats"]:
                            results["threats_found"].extend(threat_data["threats"])

        except Exception as e:
            logger.error(f"Vulnerability check failed: {str(e)}")
            results["recommendations"].append({
                "type": "vulnerability_check",
                "details": "Unable to complete vulnerability check"
            })

    async def _validate_model_structure(self, model_data: bytes, results: Dict):
        """Validate model structure and architecture"""
        try:
            # Load model for structural analysis
            model = tf.keras.models.load_model(model_data)

            # Check model architecture
            suspicious_layers = []
            for layer in model.layers:
                if "Lambda" in str(type(layer)):
                    suspicious_layers.append(layer.name)

            if suspicious_layers:
                results["threats_found"].append({
                    "type": "suspicious_architecture",
                    "details": f"Suspicious layers found: {suspicious_layers}",
                    "severity": "medium"
                })

        except Exception as e:
            logger.error(f"Model structure validation failed: {str(e)}")
            results["recommendations"].append({
                "type": "structure_validation",
                "details": "Unable to validate model structure"
            })

    def _calculate_security_score(self, results: Dict) -> float:
        """Calculate overall security score"""
        score = 100.0

        # Deduct points for threats based on severity
        severity_weights = {
            "critical": 25.0,
            "high": 15.0,
            "medium": 10.0,
            "low": 5.0
        }

        for threat in results["threats_found"]:
            score -= severity_weights.get(threat["severity"], 5.0)

        # Deduct points for metadata issues
        if "metadata_analysis" in results:
            score -= len(results["metadata_analysis"].get("missing_fields", [])) * 2.0
            score -= len(results["metadata_analysis"].get("suspicious_values", {})) * 3.0

        return max(0.0, score)

    async def _store_scan_results(self, results: Dict):
        """Store scan results in Azure Blob Storage"""
        try:
            blob_service_client = BlobServiceClient.from_connection_string(
                self.model_security.storage_connection_string
            )
            container_client = blob_service_client.get_container_client(
                self.scan_results_container
            )

            # Generate unique blob name
            blob_name = f"scan_{results['scan_id']}.json"

            # Upload results
            blob_client = container_client.get_blob_client(blob_name)
            await blob_client.upload_blob(
                json.dumps(results),
                overwrite=True
            )

        except Exception as e:
            logger.error(f"Failed to store scan results: {str(e)}")
            raise
