"""
This module defines the core model service of the SecureAI Platform, 
including model generation, health checks, and model listing functionalities. 
It integrates with security features, monitoring, and data protection mechanisms.
"""

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Literal
import logging
from datetime import datetime
from ..models.registry import ModelRegistry
from ..security.auth import security_manager, data_protection
from ..utils.monitoring import MetricsManager, ComplianceMonitor
import time

# Configure logging as per technical specs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="SecureAI Platform")
model_registry = ModelRegistry()
"""Model registry for managing registered models."""

compliance_monitor = ComplianceMonitor()
"""Compliance monitor for tracking operations."""

class GenerationRequest(BaseModel):
    text: str
    model_name: Literal["deepseek", "qwen"]
    max_length: Optional[int] = 1024
    temperature: Optional[float] = 0.7


@app.post("/generate")
async def generate(
    request: GenerationRequest,
    api_key: str = Depends(security_manager.verify_api_key)
):
    """
    Generates text based on the given request parameters and the selected model.

    Args:
        request (GenerationRequest): The generation request containing text, model name, max length, and temperature.
        api_key (str): The API key for authentication and rate limiting.

    Returns:
        dict: The generated text, the model used, and the duration of the operation.

    Raises:
        HTTPException: If there is an error during the generation process, including rate limiting or model issues.
    """


    start_time = time.time()
    try:
        # Rate limiting
        await security_manager.rate_limit(api_key)
        
        # Process input with privacy protection
        protected_input = await model_registry.process_input(
            request.text, 
            request.model_name
        )
        
        # Ensure model is registered
        if request.model_name not in model_registry.models:
            await model_registry.register_model(request.model_name)
        
        model = model_registry.models[request.model_name]
        tokenizer = model_registry.tokenizers[request.model_name]
        
        # Generate response with compliance monitoring
        with compliance_monitor.track_operation(
            api_key=api_key,
            model_name=request.model_name
        ):
            inputs = tokenizer(protected_input, return_tensors="pt").to(model.device)
            outputs = model.generate(
                **inputs,
                max_length=request.max_length,
                temperature=request.temperature,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Process output through privacy pipeline
        protected_output = await data_protection.process_request({
            "result": response
        })
        
        duration = time.time() - start_time
        MetricsManager.record_request(request.model_name, "success", duration)
        
        return {
            "result": protected_output["result"], 
            "model": request.model_name, 
            "duration": duration
        }
        
    except Exception as e:
        MetricsManager.record_request(request.model_name, "error", time.time() - start_time)
        logger.error(f"Error in generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """
    Performs a health check on the service.

    Returns:
        dict: A dictionary indicating the service's health status, current timestamp, and loaded models.
    """



    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "models_loaded": list(model_registry.models.keys())
    }

@app.get("/models")
async def list_models():
    """
    Lists the available models for text generation.

    Returns:
        dict: A dictionary listing the available models and their metadata.
    """

    return {
        "available_models": [
            model_registry.metadata[name] for name in ["deepseek", "qwen"]
        ]
    } 