from dataclasses import dataclass
from typing import Literal, Optional, Any, Dict


@dataclass
class User:
    id: str
    email: str
    name: str
    avatar: Optional[str] = None
    role: Literal['user', 'admin']
    mfaEnabled: bool
    mfaVerified: bool
    lastLogin: str
    securityLevel: Literal['standard', 'enhanced']
    permissions: list[str]


@dataclass
class AuthState:
    user: Optional[User] = None
    isAuthenticated: bool
    isLoading: bool
    mfaRequired: bool
    mfaVerified: bool
    sessionExpiry: Optional[str] = None


@dataclass
class LoginCredentials:
    email: str
    password: str