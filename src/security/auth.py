import os
from datetime import datetime, timedelta
from typing import Optional, Dict

import jwt
from fastapi import Depends, HTTPException, status, Security
from fastapi.security.api_key import APIKeyHeader
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from ..models import schemas
from .encryption import EncryptionManager
from .tokenizer import PrivacyTokenizer
from .scanner import SensitiveDataScanner, SENSITIVE_DATA_PATTERNS

from ..database import models
import logging

logger = logging.getLogger(__name__)
"""
class SecurityManager:
    """
    Manages API key verification, rate limiting, and MFA challenges using Google Cloud Secret Manager.
    """

    def __init__(self):
        """
        Initializes the SecurityManager with the Secret Manager client, request logs, and MFA manager.
        """
        self.api_key_header = APIKeyHeader(name="X-API-Key")
        self.client = secretmanager.SecretManagerServiceClient()
        self.project_id = os.getenv("GCP_PROJECT_ID")  # Replace with your GCP project ID
        self.request_logs = {}
        self.mfa_manager = MultiFactor()

    def get_secret(self, secret_id, version_id="latest"):
        """
        Retrieves a secret from Google Cloud Secret Manager.
        Args:
            secret_id (str): The ID of the secret to retrieve.
            version_id (str, optional): The version of the secret to retrieve. Defaults to "latest".
        Returns:
            str: The secret value.
        Raises:
            Exception: If there is an error retrieving the secret.
        """
        name = f"projects/{self.project_id}/secrets/{secret_id}/versions/{version_id}"
        try:
            response = self.client.access_secret_version(name=name)
            return response.payload.data.decode("UTF-8")
        except Exception as e:
            logger.error(f"Failed to access secret {secret_id}: {str(e)}")
            raise

    async def verify_api_key(self, api_key: str = Security(APIKeyHeader(name="X-API-Key"))) -> bool:
        """
        Verifies the provided API key against the stored key in Google Cloud Secret Manager.
        Raises HTTPException if the API key is invalid.
        """
        try:
            stored_key = self.get_secret("api-key")
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve API key from Secret Manager",
            )
        if api_key != stored_key:
            logger.warning(f"Invalid API key attempt at {datetime.utcnow()}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid API key",
            )
        return True

    async def rate_limit(self, api_key: str) -> bool:
        """
        Implements enhanced rate limiting with additional security checks.
        Allows a maximum of 100 requests per minute per API key.
        Raises HTTPException if the rate limit is exceeded.
        Args: api_key (str): the api key.
        """
        now = datetime.utcnow()
        if api_key not in self.request_logs:
            self.request_logs[api_key] = []

        # Clean old requests
        self.request_logs[api_key] = [
            timestamp for timestamp in self.request_logs[api_key]
            if timestamp > now - timedelta(minutes=1)
        ]

        # Enhanced rate limit checks
        if len(self.request_logs[api_key]) >= 100:
            logger.warning(f"Rate limit exceeded for API key at {now}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
            )

        # Add request timestamp
        self.request_logs[api_key].append(now)

        # Log for audit
        logger.info(f"API request from {api_key} at {now}")

        return True

"""

class SecurityManager:
    Manages API key verification, rate limiting, and security-related tasks.
    """

    def __init__(self):
        """
        Initializes the SecurityManager with API key header and request logs.
        """
        self.api_key_header = APIKeyHeader(name="X-API-Key")
        self.request_logs = {}

    async def verify_api_key(self, api_key: str = Security(APIKeyHeader(name="X-API-Key"))) -> bool:
        """
        Verifies the provided API key.
        Raises HTTPException if the API key is invalid.
        """
        stored_key = os.getenv("API_KEY")
        if not stored_key:
            logger.error("API_KEY environment variable not set")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="API key not configured",
            )
        if api_key != stored_key:
            logger.warning(f"Invalid API key attempt at {datetime.utcnow()}")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid API key"
            )

        return True

    async def rate_limit(self, api_key: str) -> bool:
        """
        Implements enhanced rate limiting with additional security checks.
        Allows a maximum of 100 requests per minute per API key..
        Raises HTTPException if the rate limit is exceeded.

        Args: api_key (str): The api key.
        """
        now = datetime.utcnow()
        if api_key not in self.request_logs:
            self.request_logs[api_key] = []

        # Clean old requests
        self.request_logs[api_key] = [
            timestamp for timestamp in self.request_logs[api_key]
            if timestamp > now - timedelta(minutes=1)
        ]

        # Enhanced rate limit checks
        if len(self.request_logs[api_key]) >= 100:
            logger.warning(f"Rate limit exceeded for API key at {now}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )

        # Add request timestamp
        self.request_logs[api_key].append(now)

        # Log for audit
        logger.info(f"API request from {api_key} at {now}")

        return True

class DataProtectionPipeline:

    """
    Manages the data protection pipeline including encryption, tokenization, and sensitive data scanning.
    """

    def __init__(self):
        """
        Initializes the DataProtectionPipeline with encryption, tokenization, and scanning managers.
        """
        self.encryption = EncryptionManager()
        self.tokenizer = PrivacyTokenizer()
        self.scanner = SensitiveDataScanner()

    async def process_request(self, request_data: dict) -> dict:
        """
        Processes incoming request data with privacy protections.

        Args: request_data (dict): The request data to process.

        Returns: dict: The protected data.
        """

        # Scan for sensitive data
        scan_result = await self.scanner.scan(
            data=request_data,
            patterns=SENSITIVE_DATA_PATTERNS
        )

        # Tokenize sensitive information
        tokenized_data = await self.tokenizer.tokenize(
            data=request_data,
            sensitive_ranges=scan_result.sensitive_ranges
        )

        # Encrypt processed data
        protected_data = await self.encryption.encrypt(
            data=tokenized_data,
            key_rotation_policy='4h'
        )

        return protected_data



def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """
    Retrieves a user from the database by their email.

    Args:
        db (Session): The database session.
        email (str): The email of the user to search for.

    Returns:
        Optional[models.User]: The User object if found, otherwise None.
    """
    # Using the session to query the database
    user = db.query(models.User).filter(models.User.email == email).first()
    return user


security_manager = SecurityManager()
data_protection = DataProtectionPipeline()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
from ..database.database import get_db

# Security configurations
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Environment variables
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.

    Args:
        plain_password (str): The plain text password.
        hashed_password (str): The hashed password.

    Returns: bool: True if the password matches the hash, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Generate password hash.

    Args:
        password (str): The password to hash.

    Returns: str: The hashed password.
    """
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT token with expiration."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> schemas.User:
    """
    Get current user from JWT token.

    Args:
        token (str): The JWT token.

    Returns:


        schemas.User: The current user.

    Raises: HTTPException: If the token is invalid or the user is not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception


    db = next(get_db())
    user = get_user_by_email(db=db, email=token_data.email)
    db.close()
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: schemas.User = Depends(get_current_user)
) -> schemas.User:
    """
    Verify user is active.

    Args:
        current_user (schemas.User): The current user.

    Returns:
        schemas.User: The active user.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
