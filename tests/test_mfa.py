import pytest
from datetime import datetime, timedelta
from src.security.mfa import MultiFactor
from src.security.exceptions import SecurityException

@pytest.fixture
async def mfa_manager():
    return MultiFactor()

@pytest.mark.asyncio
async def test_mfa_setup(mfa_manager):
    # Test MFA setup
    setup_result = await mfa_manager.setup_mfa("test_user")
    
    assert 'qr_code' in setup_result
    assert 'secret' in setup_result
    assert 'provisioning_uri' in setup_result
    assert 'SecureAI Platform' in setup_result['provisioning_uri']

@pytest.mark.asyncio
async def test_verify_code(mfa_manager):
    # Setup MFA
    setup = await mfa_manager.setup_mfa("test_user")
    
    # Generate valid code
    totp = pyotp.TOTP(setup['secret'])
    valid_code = totp.now()
    
    # Test valid code
    assert await mfa_manager.verify_code("test_user", valid_code)
    
    # Test invalid code
    assert not await mfa_manager.verify_code("test_user", "000000")

@pytest.mark.asyncio
async def test_risk_assessment(mfa_manager):
    context = {
        'ip_address': '192.168.1.1',
        'timestamp': datetime.utcnow(),
        'request_history': [
            datetime.utcnow() - timedelta(seconds=1),
            datetime.utcnow()
        ]
    }
    
    risk_level = await mfa_manager._assess_risk(context)
    assert isinstance(risk_level, float)
    assert 0 <= risk_level <= 1

@pytest.mark.asyncio
async def test_requires_challenge(mfa_manager):
    # Test new session
    context = {'timestamp': datetime.utcnow()}
    assert await mfa_manager.requires_challenge("test_key", context)
    
    # Test existing session
    mfa_manager.session_cache["test_key"] = {
        'expiry': datetime.utcnow() + timedelta(hours=1),
        'user_id': 'test_user'
    }
    assert not await mfa_manager.requires_challenge("test_key", context)

@pytest.mark.asyncio
async def test_challenge_failure(mfa_manager):
    with pytest.raises(SecurityException):
        await mfa_manager.challenge("invalid_key") 