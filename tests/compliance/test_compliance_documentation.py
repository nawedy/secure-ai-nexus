"""
Tests for Compliance Documentation System
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from docs.compliance.compliance_documentation import (
    ComplianceDocumentation,
    ComplianceRequirement,
    ComplianceValidation
)

@pytest.fixture
def compliance_doc():
    """Create ComplianceDocumentation instance for testing"""
    return ComplianceDocumentation()

@pytest.fixture
def mock_validator():
    """Mock compliance validator"""
    return Mock()

@pytest.fixture
def mock_generator():
    """Mock documentation generator"""
    return Mock()

@pytest.fixture
def sample_requirement():
    """Create sample compliance requirement for testing"""
    return ComplianceRequirement(
        id="REQ-001",
        standard="ISO27001",
        category="Access Control",
        description="Implement strong access controls",
        controls=[
            {
                "id": "AC-1",
                "name": "Access Control Policy",
                "requirements": ["policy_document", "implementation_evidence"]
            }
        ],
        validation_criteria=[
            {
                "id": "VAL-1",
                "type": "DOCUMENTATION",
                "criteria": "Policy must be documented"
            },
            {
                "id": "VAL-2",
                "type": "IMPLEMENTATION",
                "criteria": "Controls must be implemented"
            }
        ],
        evidence_requirements=[
            {
                "type": "DOCUMENT",
                "source": "policy_repository",
                "format": "pdf"
            }
        ]
    )

@pytest.mark.asyncio
async def test_validate_compliance(
    compliance_doc,
    mock_validator,
    sample_requirement
):
    """Test compliance validation"""
    with patch.object(compliance_doc, 'validator', mock_validator):
        validation = await compliance_doc.validate_compliance(sample_requirement)

        assert isinstance(validation, ComplianceValidation)
        assert validation.requirement == sample_requirement
        assert isinstance(validation.timestamp, datetime)
        assert "evidence" in validation.evidence
        assert len(validation.findings) >= 0

@pytest.mark.asyncio
async def test_collect_compliance_evidence(
    compliance_doc,
    sample_requirement
):
    """Test evidence collection"""
    evidence = await compliance_doc.collect_compliance_evidence(sample_requirement)

    for req in sample_requirement.evidence_requirements:
        assert req['type'] in evidence
        assert 'data' in evidence[req['type']]
        assert 'metadata' in evidence[req['type']]
        assert isinstance(evidence[req['type']]['metadata']['collected_at'], datetime)

@pytest.mark.asyncio
async def test_generate_compliance_documentation(
    compliance_doc,
    mock_generator,
    sample_requirement
):
    """Test documentation generation"""
    validation = ComplianceValidation(
        requirement=sample_requirement,
        timestamp=datetime.utcnow(),
        status="COMPLIANT",
        evidence={"DOCUMENT": {"data": "test", "metadata": {}}},
        findings=[],
        recommendations=[],
        next_review=datetime.utcnow() + timedelta(days=90)
    )

    with patch.object(compliance_doc, 'generator', mock_generator):
        documentation = await compliance_doc.generate_compliance_documentation(validation)

        assert "documentation" in documentation
        assert "attachments" in documentation
        assert "summary" in documentation
        assert "metadata" in documentation
        assert isinstance(documentation["metadata"]["generated_at"], datetime)

@pytest.mark.asyncio
async def test_monitor_compliance_status(
    compliance_doc,
    mock_validator,
    sample_requirement
):
    """Test compliance status monitoring"""
    with patch.object(compliance_doc, 'get_compliance_requirements',
                     return_value=[sample_requirement]):
        status = await compliance_doc.monitor_compliance_status()

        assert "overall_status" in status
        assert "requirements" in status
        assert sample_requirement.id in status["requirements"]
        assert isinstance(status["timestamp"], datetime)

@pytest.mark.asyncio
async def test_evidence_collection_failure(
    compliance_doc,
    sample_requirement
):
    """Test evidence collection failure handling"""
    error = Exception("Failed to collect evidence")

    with pytest.raises(Exception):
        with patch.object(compliance_doc, 'collect_specific_evidence',
                         side_effect=error):
            await compliance_doc.collect_compliance_evidence(sample_requirement)

    # Verify error handling
    assert compliance_doc.logger.error.called

@pytest.mark.asyncio
async def test_validation_failure_handling(
    compliance_doc,
    sample_requirement
):
    """Test validation failure handling"""
    error = Exception("Validation failed")

    with pytest.raises(Exception):
        with patch.object(compliance_doc, 'validator',
                         side_effect=error):
            await compliance_doc.validate_compliance(sample_requirement)

    # Verify error handling and notification
    assert compliance_doc.logger.error.called
