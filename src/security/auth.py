from fastapi import Security, HTTPException, status, Depends
from fastapi.security.api_key import APIKeyHeader
from fastapi.security import OAuth2AuthorizationCodeBearer
import secrets
from typing import Optional
import logging
from datetime import datetime, timedelta
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from msal import ConfidentialClientApplication
import jwt
import os

logger = logging.getLogger(__name__)

class SecurityManager:
    def __init__(self):
        self.api_key_header = APIKeyHeader(name="X-API-Key")
        # Store API key in Azure Key Vault instead of memory
        self.key_vault_url = "https://secureai-kv.vault.azure.net/"
        self.secret_client = SecretClient(
            vault_url=self.key_vault_url,
            credential=DefaultAzureCredential()
        )
        self.request_logs = {}
        self.mfa_manager = MultiFactor()

    async def verify_api_key(self, api_key: str = Security(APIKeyHeader(name="X-API-Key"))) -> bool:
        stored_key = self.secret_client.get_secret("api-key").value
        if api_key != stored_key:
            logger.warning(f"Invalid API key attempt at {datetime.utcnow()}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid API key"
            )

        # Add MFA challenge if needed
        if self.mfa_manager.requires_challenge(api_key, request.context):
            await self.mfa_manager.challenge(api_key)

        return True

    async def rate_limit(self, api_key: str) -> bool:
        """Enhanced rate limiting with additional security checks"""
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
        await self.audit_log.log_access(
            api_key=api_key,
            timestamp=now,
            action="api_request"
        )

        return True

class DataProtectionPipeline:
    def __init__(self):
        self.encryption = EncryptionManager()
        self.tokenizer = PrivacyTokenizer()
        self.scanner = SensitiveDataScanner()

    async def process_request(self, request_data: dict) -> dict:
        """Process incoming request data with privacy protections"""
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

class AzureADAuth:
    def __init__(self):
        self.tenant_id = os.getenv("AZURE_TENANT_ID")
        self.client_id = os.getenv("AZURE_CLIENT_ID")
        self.client_secret = os.getenv("AZURE_CLIENT_SECRET")
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"

        self.msal_app = ConfidentialClientApplication(
            client_id=self.client_id,
            client_credential=self.client_secret,
            authority=self.authority
        )

    async def verify_token(self, token: str):
        try:
            # Verify JWT token
            decoded = jwt.decode(
                token,
                verify=True,
                algorithms=["RS256"],
                audience=self.client_id
            )
            return decoded
        except Exception as e:
            logger.error(f"Token verification failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
    tokenUrl="https://login.microsoftonline.com/common/oauth2/v2.0/token"
)

auth = AzureADAuth()

async def get_current_user(token: str = Depends(oauth2_scheme)):
    return await auth.verify_token(token)

security_manager = SecurityManager()
data_protection = DataProtectionPipeline()
