"""
Tests for Compliance Validator
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from security.compliance import ComplianceValidator
from docs.compliance.compliance_documentation import ComplianceRequirement

@pytest.fixture
def validator():
    """Create ComplianceValidator instance for testing"""
    return ComplianceValidator()

@pytest.fixture
def mock_evidence_validator():
    """Mock evidence validator"""
    return Mock()

@pytest.fixture
def sample_requirement():
    """Create sample requirement for testing"""
    return ComplianceRequirement(
        id="REQ-002",
        standard="PCI-DSS",
        category="Data Protection",
        description="Protect stored cardholder data",
        controls=[
            {
                "id": "DP-1",
                "name": "Data Encryption",
                "requirements": ["encryption_implementation", "key_management"]
            }
        ],
        validation_criteria=[
            {
                "id": "VAL-1",
                "type": "TECHNICAL",
                "criteria": "Data must be encrypted"
            }
        ],
        evidence_requirements=[
            {
                "type": "TECHNICAL",
                "source": "system_config",
                "format": "json"
            }
        ]
    )

@pytest.mark.asyncio
async def test_validate_requirement(
    validator,
    mock_evidence_validator,
    sample_requirement
):
    """Test requirement validation"""
    evidence = {
        "TECHNICAL": {
            "data": {"encryption": "AES-256"},
            "metadata": {"collected_at": datetime.utcnow()}
        }
    }

    with patch.object(validator, 'evidence_validator', mock_evidence_validator):
        result = await validator.validate_requirement(sample_requirement, evidence)

        assert result["status"] in ["COMPLIANT", "NON_COMPLIANT"]
        assert "validation_details" in result
        assert "timestamp" in result

@pytest.mark.asyncio
async def test_validate_evidence(validator):
    """Test evidence validation"""
    evidence = {
        "type": "TECHNICAL",
        "data": {"encryption": "AES-256"},
        "source": "system_config"
    }

    result = await validator.validate_evidence(evidence)

    assert result["valid"] is True
    assert "validation_details" in result
    assert isinstance(result["timestamp"], datetime)

@pytest.mark.asyncio
async def test_validate_controls(
    validator,
    sample_requirement
):
    """Test control validation"""
    result = await validator.validate_controls(sample_requirement.controls)

    assert isinstance(result, list)
    assert len(result) == len(sample_requirement.controls)
    assert all("status" in r for r in result)

@pytest.mark.asyncio
async def test_validation_with_missing_evidence(
    validator,
    sample_requirement
):
    """Test validation with missing evidence"""
    evidence = {}  # Empty evidence

    result = await validator.validate_requirement(sample_requirement, evidence)

    assert result["status"] == "NON_COMPLIANT"
    assert "missing_evidence" in result["validation_details"]

@pytest.mark.asyncio
async def test_validation_with_invalid_evidence(
    validator,
    sample_requirement
):
    """Test validation with invalid evidence"""
    evidence = {
        "TECHNICAL": {
            "data": {"encryption": "INVALID"},
            "metadata": {"collected_at": datetime.utcnow()}
        }
    }

    result = await validator.validate_requirement(sample_requirement, evidence)

    assert result["status"] == "NON_COMPLIANT"
    assert "invalid_evidence" in result["validation_details"]
