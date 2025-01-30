from cryptography.fernet import Fernet
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
import logging

logger = logging.getLogger(__name__)

class ModelSecurity:
    def __init__(self, key_vault_client: SecretClient):
        self.key_vault_client = key_vault_client
        self.encryption_key = self._get_encryption_key()
        self.fernet = Fernet(self.encryption_key)

    def _get_encryption_key(self) -> bytes:
        """Get encryption key from Azure Key Vault"""
        try:
            secret = self.key_vault_client.get_secret("encryption-key")
            return secret.value.encode()
        except Exception as e:
            logger.error(f"Failed to get encryption key: {str(e)}")
            raise

    async def encrypt_model(self, model_data: bytes) -> bytes:
        """Encrypt model data"""
        try:
            return self.fernet.encrypt(model_data)
        except Exception as e:
            logger.error(f"Model encryption failed: {str(e)}")
            raise

    async def decrypt_model(self, encrypted_data: bytes) -> bytes:
        """Decrypt model data"""
        try:
            return self.fernet.decrypt(encrypted_data)
        except Exception as e:
            logger.error(f"Model decryption failed: {str(e)}")
            raise
