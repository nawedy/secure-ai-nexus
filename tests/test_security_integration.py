import pytest
from datetime import datetime
from src.security.auth import SecurityManager, DataProtectionPipeline
from src.security.mfa import MultiFactor
from src.security.session import SessionHandler
from src.security.encryption import EncryptionManager
from src.security.exceptions import SecurityException

@pytest.fixture
async def security_setup():
    return {
        'security_manager': SecurityManager(),
        'data_protection': DataProtectionPipeline(),
        'mfa_manager': MultiFactor(),
        'session_handler': SessionHandler(),
        'encryption_manager': EncryptionManager()
    }

@pytest.mark.asyncio
async def test_complete_security_flow(security_setup):
    # 1. Initial authentication
    api_key = "test_key"
    context = {
        'ip_address': '192.168.1.1',
        'timestamp': datetime.utcnow(),
        'user_agent': 'test-client/1.0'
    }
    
    # 2. MFA challenge if needed
    if await security_setup['mfa_manager'].requires_challenge(api_key, context):
        await security_setup['mfa_manager'].challenge(api_key)
    
    # 3. Create session
    identity = {
        'api_key': api_key,
        'context': context
    }
    session_token = await security_setup['session_handler'].create(identity)
    
    # 4. Process sensitive data
    test_data = {
        'text': 'SSN: 123-45-6789',
        'metadata': {
            'email': 'test@example.com'
        }
    }
    
    protected_data = await security_setup['data_protection'].process_request(test_data)
    
    # 5. Verify data protection
    assert '123-45-6789' not in str(protected_data)
    assert 'test@example.com' not in str(protected_data)
    
    # 6. Verify session validation
    validated_identity = await security_setup['session_handler'].validate(session_token)
    assert validated_identity['api_key'] == api_key

@pytest.mark.asyncio
async def test_security_failure_scenarios(security_setup):
    # Test invalid API key
    with pytest.raises(SecurityException):
        await security_setup['security_manager'].verify_api_key("invalid_key")
    
    # Test expired session
    with pytest.raises(SecurityException):
        await security_setup['session_handler'].validate("invalid_token")
    
    # Test failed MFA
    with pytest.raises(SecurityException):
        await security_setup['mfa_manager'].verify_code("test_user", "000000")
    
    # Test invalid encryption
    with pytest.raises(SecurityException):
        await security_setup['encryption_manager'].decrypt({
            'encrypted_data': 'invalid',
            'key_id': 'invalid'
        }) 