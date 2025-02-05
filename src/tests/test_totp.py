import pytest
import time
import hashlib
import pyotp
from src.utils.totp import (
    TOTPSecret,
    generate_totp,
    verify_totp,
    hash_secret,
    generate_backup_code,
    validate_totp_setup,
    generate_emergency_access_token,
)


@pytest.mark.asyncio
async def test_generate_totp():
    totp_secret = await generate_totp("user1")
    assert isinstance(totp_secret, TOTPSecret)
    assert totp_secret.secret
    assert totp_secret.uri
    assert totp_secret.qrCode


def test_totp_secret_creation():
    totp_secret = TOTPSecret(secret="secret", uri="uri", qrCode="qrCode")
    assert totp_secret.secret == "secret"
    assert totp_secret.uri == "uri"
    assert totp_secret.qrCode == "qrCode"


def test_verify_totp():
    secret = "JBSWY3DPEHPK3PXP"
    totp_obj = pyotp.TOTP(secret)
    token = totp_obj.now()

    assert verify_totp(token, secret) is True
    assert verify_totp("123456", secret) is False
    assert verify_totp(token, secret, {"window": 2}) is True
    assert verify_totp(token, secret, {"window": 0}) is True
    assert verify_totp("123456", secret, {"window": 2}) is False


def test_hash_secret():
    secret = "mysecret"
    hashed_secret = hash_secret(secret)
    assert len(hashed_secret) == 64
    assert hashlib.sha256(secret.encode()).hexdigest() == hashed_secret


def test_generate_backup_code():
    code = generate_backup_code()
    assert len(code) == 23
    assert code.count("-") == 4
    for c in code:
      if c != '-':
        assert c.isalnum()

def test_validate_totp_setup():
    secret = "JBSWY3DPEHPK3PXP"
    totp_obj = pyotp.TOTP(secret)
    token = totp_obj.now()

    result = validate_totp_setup(secret, token)
    assert result["valid"] is True
    assert "error" not in result

    result = validate_totp_setup(secret, "123456")
    assert result["valid"] is False
    assert result["error"] == "Invalid verification code"

    result = validate_totp_setup("", token)
    assert result["valid"] is False
    assert result["error"] == "Missing required parameters"

    result = validate_totp_setup(secret, "invalid")
    assert result["valid"] is False
    assert result["error"] == "Invalid token format"


def test_generate_emergency_access_token():
    token = generate_emergency_access_token("user1")
    parts = token.split(".")
    assert len(parts) == 2
    assert len(parts[0]) == 64
    assert parts[1].isdigit()