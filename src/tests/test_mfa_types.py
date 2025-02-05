import pytest
from src.types.mfa import (
    TOTPConfig,
    MFAStatus,
    MFAVerificationResult,
    MFASettings,
    MFAChallenge,
)


def test_totp_config_creation():
    config = TOTPConfig(
        secret="secret",
        uri="uri",
        qrCode="qr",
        backupCodes=["123", "456"],
        algorithm="sha256",
        digits=6,
        step=30,
    )
    assert config.secret == "secret"
    assert config.uri == "uri"
    assert config.qrCode == "qr"
    assert config.backupCodes == ["123", "456"]
    assert config.algorithm == "sha256"
    assert config.digits == 6
    assert config.step == 30


def test_mfa_status_creation():
    status = MFAStatus(
        enabled=True,
        verified=False,
        recoveryCodesRemaining=5,
        failedAttempts=0,
    )
    assert status.enabled is True
    assert status.verified is False
    assert status.lastVerified is None
    assert status.method is None
    assert status.recoveryCodesRemaining == 5
    assert status.lastFailedAttempt is None
    assert status.failedAttempts == 0
    assert status.blockedUntil is None


def test_mfa_verification_result_creation():
    result = MFAVerificationResult(success=True)
    assert result.success is True
    assert result.method is None
    assert result.timestamp is None
    assert result.error is None
    assert result.remainingAttempts is None
    assert result.blockDuration is None


def test_mfa_settings_creation():
    settings = MFASettings(
        userId="user1",
        secret="secret",
        backupCodes=["123", "456"],
        lastRotated="2023-10-27",
        algorithm="sha256",
        digits=6,
        step=30,
    )
    assert settings.userId == "user1"
    assert settings.secret == "secret"
    assert settings.backupCodes == ["123", "456"]
    assert settings.lastRotated == "2023-10-27"
    assert settings.algorithm == "sha256"
    assert settings.digits == 6
    assert settings.step == 30


def test_mfa_challenge_creation():
    challenge = MFAChallenge(
        challengeId="1",
        method="totp",
        timestamp="2023-10-27",
        expiresAt="2023-10-27",
        attempts=1,
        maxAttempts=3,
    )
    assert challenge.challengeId == "1"
    assert challenge.method == "totp"
    assert challenge.timestamp == "2023-10-27"
    assert challenge.expiresAt == "2023-10-27"
    assert challenge.attempts == 1
    assert challenge.maxAttempts == 3


def test_mfa_status_invalid_method():
    with pytest.raises(ValueError):
        MFAStatus(
            enabled=True,
            verified=False,
            recoveryCodesRemaining=5,
            failedAttempts=0,
            method="invalid"
        )


def test_mfa_verification_result_invalid_method():
    with pytest.raises(ValueError):
        MFAVerificationResult(success=True, method="invalid")

def test_mfa_challenge_invalid_method():
    with pytest.raises(ValueError):
        MFAChallenge(
            challengeId="1",
            method="invalid",
            timestamp="2023-10-27",
            expiresAt="2023-10-27",
            attempts=1,
            maxAttempts=3,
        )