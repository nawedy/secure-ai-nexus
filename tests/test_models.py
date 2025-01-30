import pytest
from src.models.registry import ModelRegistry, ModelMetadata
import torch

@pytest.fixture
async def model_registry():
    registry = ModelRegistry()
    yield registry

@pytest.mark.asyncio
async def test_model_registration(model_registry):
    # Test deepseek model registration
    metadata = await model_registry.register_model("deepseek")
    assert isinstance(metadata, ModelMetadata)
    assert metadata.name == "deepseek"
    assert metadata.version == "1.3b"
    assert "deepseek" in model_registry.models
    assert "deepseek" in model_registry.tokenizers

@pytest.mark.asyncio
async def test_invalid_model(model_registry):
    with pytest.raises(ValueError):
        await model_registry.register_model("invalid_model") 