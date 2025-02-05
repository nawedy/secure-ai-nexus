from dataclasses import dataclass
from typing import List, Optional, Literal


@dataclass
class BackupCode:
    code: str
    used: bool
    usedAt: Optional[str] = None
    hashedValue: str


@dataclass
class BackupCodesState:
    codes: List[BackupCode]
    generatedAt: str
    lastUsed: Optional[str] = None
    remainingCodes: int


@dataclass
class BackupCodesValidation:
    valid: bool
    used: bool
    error: Optional[str] = None


@dataclass
class BackupCodesGenerationOptions:
    numberOfCodes: Optional[int] = None
    codeLength: Optional[int] = None
    format: Optional[Literal['groups', 'single']] = None
    groupSize: Optional[int] = None