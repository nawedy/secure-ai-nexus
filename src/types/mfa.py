from dataclasses import dataclass
from typing import Literal, Optional, List


@dataclass
class TOTPConfig:
    secret: str
    uri: str
    qrCode: str
    backupCodes: List[str]
    algorithm: str
    digits: int
    step: int


@dataclass
class MFAStatus:
    enabled: bool
    verified: bool
    lastVerified: Optional[str] = None
    method: Optional[Literal['totp', 'backup']] = None
    recoveryCodesRemaining: int
    lastFailedAttempt: Optional[str] = None
    failedAttempts: int
    blockedUntil: Optional[str] = None


@dataclass
class MFAVerificationResult:
    success: bool
    method: Optional[Literal['totp', 'backup']] = None
    timestamp: Optional[str] = None
    error: Optional[str] = None
    remainingAttempts: Optional[int] = None
    blockDuration: Optional[int] = None


@dataclass
class MFASettings:
    userId: str
    secret: str
    backupCodes: List[str]
    lastRotated: str
    algorithm: str
    digits: int
    step: int


@dataclass
class MFAChallenge:
    challengeId: str
    method: Literal['totp', 'backup']
    timestamp: str
    expiresAt: str
    attempts: int
    maxAttempts: int