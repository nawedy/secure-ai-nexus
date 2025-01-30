import pytest
from datetime import datetime, timedelta
import jwt
from src.security.session import SessionHandler
from src.security.exceptions import SecurityException

@pytest.fixture
async def session_handler():
    return SessionHandler()

@pytest.mark.asyncio
async def test_session_creation(session_handler):
    identity = {
        'user_id': 'test_user',
        'role': 'admin'
    }
    
    token = await session_handler.create(identity, '15m')
    assert token is not None
    
    # Verify session storage
    session_id = list(session_handler.sessions.keys())[0]
    session = session_handler.sessions[session_id]
    assert session['identity'] == identity
    assert session['expiry'] > datetime.utcnow()

@pytest.mark.asyncio
async def test_session_validation(session_handler):
    # Create session
    identity = {'user_id': 'test_user'}
    token = await session_handler.create(identity, '15m')
    
    # Validate token
    validated_identity = await session_handler.validate(token)
    assert validated_identity == identity

@pytest.mark.asyncio
async def test_session_expiration(session_handler):
    # Create short-lived session
    token = await session_handler.create({'user_id': 'test_user'}, '1m')
    
    # Fast-forward time
    session_id = list(session_handler.sessions.keys())[0]
    session_handler.sessions[session_id]['expiry'] = datetime.utcnow() - timedelta(minutes=1)
    
    # Verify expiration
    with pytest.raises(SecurityException) as exc_info:
        await session_handler.validate(token)
    assert "Session expired" in str(exc_info.value)

@pytest.mark.asyncio
async def test_session_revocation(session_handler):
    # Create session
    token = await session_handler.create({'user_id': 'test_user'})
    
    # Revoke session
    await session_handler.revoke(token)
    
    # Verify revocation
    with pytest.raises(SecurityException):
        await session_handler.validate(token)

@pytest.mark.asyncio
async def test_session_cleanup(session_handler):
    # Create expired sessions
    identity = {'user_id': 'test_user'}
    token1 = await session_handler.create(identity)
    token2 = await session_handler.create(identity)
    
    # Set sessions as expired
    for session in session_handler.sessions.values():
        session['expiry'] = datetime.utcnow() - timedelta(minutes=1)
    
    # Run cleanup
    await session_handler.cleanup()
    
    # Verify cleanup
    assert len(session_handler.sessions) == 0 