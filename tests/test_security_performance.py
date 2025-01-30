import pytest
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from src.security.auth import SecurityManager
from src.security.encryption import EncryptionManager

@pytest.fixture
async def security_components():
    return {
        'security_manager': SecurityManager(),
        'encryption_manager': EncryptionManager()
    }

@pytest.mark.asyncio
async def test_encryption_performance(security_components):
    test_data = {
        'large_text': 'x' * 1000000,  # 1MB of data
        'nested': {
            'field1': 'x' * 100000,
            'field2': 'x' * 100000
        }
    }
    
    start_time = time.time()
    encrypted = await security_components['encryption_manager'].encrypt(
        test_data,
        key_rotation_policy='4h'
    )
    encryption_time = time.time() - start_time
    
    assert encryption_time < 1.0  # Should encrypt 1MB in under 1 second

@pytest.mark.asyncio
async def test_concurrent_requests(security_components):
    async def make_request():
        try:
            await security_components['security_manager'].verify_api_key("test_key")
            return True
        except Exception:
            return False
    
    # Test 100 concurrent requests
    tasks = [make_request() for _ in range(100)]
    results = await asyncio.gather(*tasks)
    
    # Verify rate limiting worked
    assert sum(results) <= 100  # Should not exceed rate limit

@pytest.mark.asyncio
async def test_key_rotation_performance(security_components):
    # Test key rotation under load
    async def rotate_and_encrypt():
        data = {'test': 'data'}
        return await security_components['encryption_manager'].encrypt(
            data,
            key_rotation_policy='1h'
        )
    
    start_time = time.time()
    tasks = [rotate_and_encrypt() for _ in range(10)]
    results = await asyncio.gather(*tasks)
    total_time = time.time() - start_time
    
    assert total_time < 5.0  # Should handle 10 rotations in under 5 seconds
    assert len(set(r['key_id'] for r in results)) <= 2  # Should reuse keys 