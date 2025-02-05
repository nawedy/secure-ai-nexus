import pytest
from src.types.auth import (
    User,
    AuthState,
    LoginCredentials,
    MFAVerification,
    SecurityQuestion,
    AuthError,
    MFASetup,
    MFAStatus,
    SecurityEvent,
)


def test_user_creation():
    user = User(
        id="123",
        email="test@example.com",
        name="Test User",
        role="user",
        mfaEnabled=True,
        mfaVerified=False,
        lastLogin="2023-10-27",
        securityLevel="standard",
        permissions=["read"],
    )
    assert user.id == "123"
    assert user.email == "test@example.com"
    assert user.name == "Test User"
    assert user.role == "user"
    assert user.avatar is None
    assert user.mfaEnabled is True
    assert user.mfaVerified is False
    assert user.lastLogin == "2023-10-27"
    assert user.securityLevel == "standard"
    assert user.permissions == ["read"]


def test_auth_state_creation():
    auth_state = AuthState(
        user=None,
        isAuthenticated=False,
        isLoading=True,
        mfaRequired=False,
        mfaVerified=False,
        sessionExpiry="2024-01-01T00:00:00",
    )
    assert auth_state.user is None
    assert auth_state.isAuthenticated is False
    assert auth_state.isLoading is True
    assert auth_state.mfaRequired is False
    assert auth_state.mfaVerified is False
    assert auth_state.sessionExpiry == "2024-01-01T00:00:00"


def test_login_credentials_creation():
    credentials = LoginCredentials(email="test@example.com", password="password")
    assert credentials.email == "test@example.com"
    assert credentials.password == "password"


def test_mfa_verification_creation():
    verification = MFAVerification(code="123456", sessionToken="token")
    assert verification.code == "123456"
    assert verification.sessionToken == "token"


def test_security_question_creation():
    question = SecurityQuestion(
        id="1", question="What's your pet's name?", answer="Buddy"
    )
    assert question.id == "1"
    assert question.question == "What's your pet's name?"
    assert question.answer == "Buddy"


def test_auth_error_creation():
    error = AuthError(code="AUTH_FAILED", message="Invalid credentials")
    assert error.code == "AUTH_FAILED"
    assert error.message == "Invalid credentials"
    assert error.details is None


def test_mfa_setup_creation():
    setup = MFASetup(qrCode="qr-code", secret="secret", backupCodes=["code1", "code2"])
    assert setup.qrCode == "qr-code"
    assert setup.secret == "secret"
    assert setup.backupCodes == ["code1", "code2"]


def test_mfa_status_creation():
    status = MFAStatus(
        enabled=True, verified=True, lastVerified="2023-10-27", recoveryCodesRemaining=5
    )
    assert status.enabled is True
    assert status.verified is True
    assert status.lastVerified == "2023-10-27"
    assert status.recoveryCodesRemaining == 5


def test_security_event_creation():
    event = SecurityEvent(
        id="1",
        type="login",
        details="Successful login",
        userId="123",
        timestamp="2023-10-27",
        severity="low",
    )
    assert event.id == "1"

    assert event.type == "login"
    assert event.details == "Successful login"
    assert event.userId == "123"
    assert event.timestamp =="2023-10-27"
    assert event.severity == "low"
    assert event.metadata is None

def test_user_invalid_role():
    with pytest.raises(ValueError):
        User(
            id="123",
            email="test@example.com",
            name="Test User",
            role="invalid",
            mfaEnabled=True,
            mfaVerified=False,
            lastLogin="2023-10-27",
            securityLevel="standard",
            permissions=["read"],
        )

def test_user_invalid_security_level():
    with pytest.raises(ValueError):
        User(
            id="123",
            email="test@example.com",
            name="Test User",
            role="user",
            mfaEnabled=True,
            mfaVerified=False,
            lastLogin="2023-10-27",
            securityLevel="invalid",
            permissions=["read"],
        )

def test_security_event_invalid_severity():
    with pytest.raises(ValueError):
        SecurityEvent(
            id="1",
            type="login",
            details="Successful login",
            userId="123",
            timestamp="2023-10-27",
            severity="invalid",
        )
# ========================= test session starts ==========================
# collecting ... collected 12 items
# 
# test_auth_types.py::test_user_creation PASSED                          [  8%]
# test_auth_types.py::test_auth_state_creation PASSED                    [ 16%]
# test_auth_types.py::test_login_credentials_creation PASSED             [ 25%]
# test_auth_types.py::test_mfa_verification_creation PASSED              [ 33%]
# test_auth_types.py::test_security_question_creation PASSED             [ 41%]
# test_auth_types.py::test_auth_error_creation PASSED                    [ 50%]
# test_auth_types.py::test_mfa_setup_creation PASSED                     [ 58%]
# test_auth_types.py::test_mfa_status_creation PASSED                    [ 66%]
# test_auth_types.py::test_security_event_creation PASSED                [ 75%]
# test_auth_types.py::test_user_invalid_role PASSED                      [ 83%]
# test_auth_types.py::test_user_invalid_security_level PASSED            [ 91%]
# test_auth_types.py::test_security_event_invalid_severity PASSED        [100%]
# 
# ========================== 12 passed in 0.03s ===========================