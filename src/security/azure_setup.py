from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.identity import ClientSecretCredential
import os
import logging

logger = logging.getLogger(__name__)

class AzureSecuritySetup:
    def __init__(self):
        self.tenant_id = os.getenv("AZURE_TENANT_ID")
        self.client_id = os.getenv("AZURE_CLIENT_ID")
        self.client_secret = os.getenv("AZURE_CLIENT_SECRET")
        self.key_vault_url = os.getenv("AZURE_KEY_VAULT_URL")

        # Initialize Azure credentials
        self.credential = ClientSecretCredential(
            tenant_id=self.tenant_id,
            client_id=self.client_id,
            client_secret=self.client_secret
        )

        # Initialize Key Vault client
        self.key_vault_client = SecretClient(
            vault_url=self.key_vault_url,
            credential=self.credential
        )

    async def setup_key_vault(self):
        """Initialize Key Vault with basic secrets"""
        try:
            # Store initial secrets
            await self.key_vault_client.set_secret("encryption-key", os.urandom(32).hex())
            await self.key_vault_client.set_secret("api-key", os.urandom(32).hex())

            logger.info("Key Vault setup completed successfully")
            return True
        except Exception as e:
            logger.error(f"Key Vault setup failed: {str(e)}")
            raise
