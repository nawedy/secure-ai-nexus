from typing import Dict, Optional
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from pydantic import BaseModel
import logging
from ..utils.monitoring import MetricsManager
import time
from ..security.auth import DataProtectionPipeline
from .validator import ModelSecurityValidator

logger = logging.getLogger(__name__)

class ModelMetadata(BaseModel):
    name: str
    version: str
    framework: str
    architecture: str
    description: str
    performance_metrics: Optional[Dict] = None

class ModelRegistry:
    def __init__(self):
        self.models: Dict = {}
        self.tokenizers: Dict = {}
        self.metadata: Dict[str, ModelMetadata] = {}
        self.security_validator = ModelSecurityValidator()
        self.data_protection = DataProtectionPipeline()
        
    async def register_model(self, model_name: str) -> ModelMetadata:
        """Register and load a model with security validation"""
        start_time = time.time()
        try:
            if model_name == "deepseek":
                model_id = "deepseek-ai/deepseek-coder-1.3b-base"
                metadata = ModelMetadata(
                    name="deepseek",
                    version="1.3b",
                    framework="pytorch",
                    architecture="transformer",
                    description="DeepSeek Coder 1.3B base model"
                )
            elif model_name == "qwen":
                model_id = "Qwen/Qwen-1_8B"
                metadata = ModelMetadata(
                    name="qwen",
                    version="1.8b",
                    framework="pytorch",
                    architecture="transformer",
                    description="Qwen 1.8B model"
                )
            else:
                raise ValueError(f"Unknown model: {model_name}")

            logger.info(f"Loading model: {model_id}")
            
            # Load with optimizations as per technical specs
            self.models[model_name] = AutoModelForCausalLM.from_pretrained(
                model_id,
                torch_dtype=torch.float16,
                load_in_4bit=True,
                device_map="auto",
                trust_remote_code=True
            )
            
            self.tokenizers[model_name] = AutoTokenizer.from_pretrained(
                model_id, 
                trust_remote_code=True
            )
            
            # Validate model security
            validation_result = await self.security_validator.validate_model(
                model=self.models[model_name],
                metadata=metadata
            )
            
            if not validation_result.passed:
                raise SecurityException(
                    f"Model security validation failed: {validation_result.details}"
                )
            
            # Add security metadata
            metadata.security_validation = validation_result.summary
            self.metadata[model_name] = metadata
            
            # Record metrics
            load_time = time.time() - start_time
            MetricsManager.record_model_load_time(model_name, load_time)
            
            # Record GPU memory usage
            if torch.cuda.is_available():
                memory_bytes = torch.cuda.max_memory_allocated()
                device = torch.cuda.get_device_name(0)
                MetricsManager.update_gpu_memory(model_name, device, memory_bytes)
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error loading model {model_name}: {str(e)}")
            REQUEST_COUNT.labels(model_name=model_name, status="error").inc()
            raise 

    async def process_input(self, text: str, model_name: str) -> str:
        """Process input with privacy protection"""
        protected_input = await self.data_protection.process_request({
            "text": text,
            "model": model_name
        })
        
        return protected_input["text"] 