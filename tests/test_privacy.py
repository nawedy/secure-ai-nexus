import pytest
from src.security.auth import DataProtectionPipeline, SecurityManager
from src.models.registry import ModelRegistry

@pytest.fixture
def data_protection():
    return DataProtectionPipeline()

@pytest.fixture
def security_manager():
    return SecurityManager()

@pytest.mark.asyncio
async def test_data_protection(data_protection):
    test_data = {
        "text": "My SSN is 123-45-6789 and email is test@example.com",
        "model": "test_model"
    }
    
    protected_data = await data_protection.process_request(test_data)
    
    # Verify PII is protected
    assert "123-45-6789" not in protected_data["text"]
    assert "test@example.com" not in protected_data["text"]
    
@pytest.mark.asyncio
async def test_model_security_validation(model_registry):
    with pytest.raises(SecurityException):
        await model_registry.register_model("malicious_model")
        
@pytest.mark.asyncio
async def test_mfa_challenge(security_manager):
    with pytest.raises(HTTPException) as exc_info:
        await security_manager.verify_api_key("test_key")
    assert exc_info.value.status_code == 403 