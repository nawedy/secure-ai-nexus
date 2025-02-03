import pytest
from unittest.mock import Mock, patch
from ...deployment.verify import DeploymentVerifier, SystemRequirements

@pytest.fixture
def verifier():
    return DeploymentVerifier()

@pytest.mark.asyncio
async def test_verify_system_resources(verifier):
    """Test system resource verification"""
    with patch('psutil.cpu_count', return_value=8), \
         patch('psutil.virtual_memory', return_value=Mock(total=16*(1024**3))), \
         patch('shutil.disk_usage', return_value=Mock(total=200*(1024**3))):

        result = await verifier.verify_system_resources()
        assert result is True

@pytest.mark.asyncio
async def test_verify_insufficient_resources(verifier):
    """Test system resource verification with insufficient resources"""
    with patch('psutil.cpu_count', return_value=2), \
         patch('psutil.virtual_memory', return_value=Mock(total=4*(1024**3))), \
         patch('shutil.disk_usage', return_value=Mock(total=50*(1024**3))), \
         patch.object(verifier, '_request_more_cpu', return_value=True), \
         patch.object(verifier, '_request_more_memory', return_value=True), \
         patch.object(verifier, '_expand_storage', return_value=True):

        result = await verifier.verify_system_resources()
        assert result is True
        assert len(verifier.fixes_applied) == 3

@pytest.mark.asyncio
async def test_verify_tools(verifier):
    """Test tool verification and installation"""
    with patch('shutil.which', side_effect=lambda x: x != 'kubectl'), \
         patch.object(verifier, '_install_missing_tools', return_value=True):

        result = await verifier.verify_tools()
        assert result is True
        assert 'Installed kubectl' in verifier.fixes_applied

@pytest.mark.asyncio
async def test_verify_permissions(verifier):
    """Test permission verification"""
    with patch.object(verifier, '_verify_gcp_permissions', return_value=False), \
         patch.object(verifier, '_verify_k8s_permissions', return_value=False), \
         patch.object(verifier, '_fix_gcp_permissions', return_value=True), \
         patch.object(verifier, '_fix_k8s_permissions', return_value=True):

        result = await verifier.verify_permissions()
        assert result is True
        assert len(verifier.fixes_applied) == 2

@pytest.mark.asyncio
async def test_verify_connectivity(verifier):
    """Test connectivity verification"""
    with patch.object(verifier, '_verify_db_connection', return_value=False), \
         patch.object(verifier, '_verify_storage_connection', return_value=False), \
         patch.object(verifier, '_fix_db_connection', return_value=True), \
         patch.object(verifier, '_fix_storage_connection', return_value=True):

        result = await verifier.verify_connectivity()
        assert result is True
        assert len(verifier.fixes_applied) == 2

@pytest.mark.asyncio
async def test_generate_report(verifier):
    """Test report generation"""
    with patch.object(verifier, 'verify_all', return_value=(True, ['Fix 1', 'Fix 2'])):
        report = await verifier.generate_report()
        assert report['success'] is True
        assert len(report['fixes_applied']) == 2
        assert all(key in report for key in ['system_status', 'tools_status', 'timestamp'])
