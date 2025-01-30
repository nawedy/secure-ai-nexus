import pytest
from src.security.encryption import EncryptionManager, KeyRotationManager
from src.security.privacy import DataProtectionPipeline

@pytest.fixture
async def encryption_manager():
    return EncryptionManager()

@pytest.fixture
async def key_manager():
    return KeyRotationManager()

@pytest.mark.asyncio
async def test_encryption_decryption(encryption_manager):
    test_data = {
        "sensitive": "test123",
        "nested": {
            "secret": "password123"
        }
    }
    
    # Test encryption
    encrypted = await encryption_manager.encrypt(test_data, "4h")
    assert "encrypted_data" in encrypted
    assert "key_id" in encrypted
    
    # Test decryption
    decrypted = await encryption_manager.decrypt(encrypted)
    assert decrypted == test_data

@pytest.mark.asyncio
async def test_key_rotation(key_manager):
    # Get initial key
    key1 = await key_manager.get_current_key("1h")
    key_id1 = key_manager.current_key_id
    
    # Force rotation
    await key_manager._rotate_key()
    
    # Get new key
    key2 = await key_manager.get_current_key("1h")
    key_id2 = key_manager.current_key_id
    
    assert key_id1 != key_id2
    assert key1 != key2

@pytest.mark.asyncio
async def test_end_to_end_protection():
    data_protection = DataProtectionPipeline()
    
    test_data = {
        "text": "SSN: 123-45-6789, CC: 4111-1111-1111-1111",
        "metadata": {
            "email": "test@example.com"
        }
    }
    
    # Process data through pipeline
    protected = await data_protection.process_request(test_data)
    
    # Verify sensitive data is protected
    assert "123-45-6789" not in str(protected)
    assert "4111-1111-1111-1111" not in str(protected)
    assert "test@example.com" not in str(protected)
    
    # Verify structure is preserved
    assert "text" in protected
    assert "metadata" in protected 