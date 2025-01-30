from typing import Dict, Optional
from datetime import datetime, timedelta
import jwt
import secrets
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
import logging

logger = logging.getLogger(__name__)

class SessionHandler:
    def __init__(self):
        self.credential = DefaultAzureCredential()
        self.secret_client = SecretClient(
            vault_url="https://secureai-kv.vault.azure.net/",
            credential=self.credential
        )
        self.sessions = {}
        
    async def create(
        self,
        identity: Dict,
        expiration: str = '15m',
        context: Optional[Dict] = None
    ) -> str:
        """Create a new secure session"""
        try:
            # Generate session ID
            session_id = secrets.token_urlsafe(32)
            
            # Get signing key from Key Vault
            signing_key = await self.secret_client.get_secret("session-signing-key")
            
            # Calculate expiration
            duration = int(expiration.replace('m', ''))
            expiry = datetime.utcnow() + timedelta(minutes=duration)
            
            # Create session token
            token = jwt.encode(
                {
                    'session_id': session_id,
                    'identity': identity,
                    'context': context or {},
                    'exp': expiry
                },
                signing_key.value,
                algorithm='HS256'
            )
            
            # Store session
            self.sessions[session_id] = {
                'token': token,
                'identity': identity,
                'expiry': expiry,
                'context': context or {}
            }
            
            return token
            
        except Exception as e:
            logger.error(f"Session creation error: {str(e)}")
            raise SecurityException("Failed to create session")
            
    async def validate(self, token: str) -> Dict:
        """Validate session token"""
        try:
            # Get signing key from Key Vault
            signing_key = await self.secret_client.get_secret("session-signing-key")
            
            # Decode and verify token
            payload = jwt.decode(
                token,
                signing_key.value,
                algorithms=['HS256']
            )
            
            session_id = payload['session_id']
            
            # Check if session exists
            if session_id not in self.sessions:
                raise SecurityException("Invalid session")
                
            session = self.sessions[session_id]
            
            # Check expiration
            if datetime.utcnow() > session['expiry']:
                del self.sessions[session_id]
                raise SecurityException("Session expired")
                
            return session['identity']
            
        except jwt.InvalidTokenError as e:
            logger.error(f"Token validation error: {str(e)}")
            raise SecurityException("Invalid session token")
            
    async def revoke(self, token: str) -> None:
        """Revoke session"""
        try:
            # Get signing key from Key Vault
            signing_key = await self.secret_client.get_secret("session-signing-key")
            
            # Decode token without verification
            payload = jwt.decode(
                token,
                signing_key.value,
                algorithms=['HS256']
            )
            
            session_id = payload['session_id']
            
            # Remove session
            if session_id in self.sessions:
                del self.sessions[session_id]
                
        except Exception as e:
            logger.error(f"Session revocation error: {str(e)}")
            raise SecurityException("Failed to revoke session")
            
    async def cleanup(self) -> None:
        """Clean up expired sessions"""
        now = datetime.utcnow()
        expired = [
            sid for sid, session in self.sessions.items()
            if now > session['expiry']
        ]
        
        for sid in expired:
            del self.sessions[sid] 