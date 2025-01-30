import pytest
from src.security.auth import SecurityManager
from fastapi import HTTPException
from datetime import datetime, timedelta

@pytest.fixture
def security_manager():
    return SecurityManager()

@pytest.mark.asyncio
async def test_valid_api_key(security_manager):
    valid_key = security_manager.api_key
    assert await security_manager.verify_api_key(valid_key) is True

@pytest.mark.asyncio
async def test_invalid_api_key(security_manager):
    with pytest.raises(HTTPException) as exc_info:
        await security_manager.verify_api_key("invalid_key")
    assert exc_info.value.status_code == 403

@pytest.mark.asyncio
async def test_rate_limiting(security_manager):
    api_key = security_manager.api_key
    
    # Test normal usage
    for _ in range(50):
        assert await security_manager.rate_limit(api_key) is True
        
    # Test rate limit exceeded
    security_manager.request_logs[api_key] = [
        datetime.utcnow() for _ in range(100)
    ]
    
    with pytest.raises(HTTPException) as exc_info:
        await security_manager.rate_limit(api_key)
    assert exc_info.value.status_code == 429 