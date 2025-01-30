from fastapi import FastAPI, HTTPException, Depends
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import os
from auth import verify_api_key
from typing import Literal, Optional
from pydantic import BaseModel

app = FastAPI(title="SecureAI MVP")

class GenerationRequest(BaseModel):
    text: str
    model_name: Literal["deepseek", "qwen"]
    max_length: Optional[int] = 1024
    temperature: Optional[float] = 0.7

class ModelService:
    def __init__(self):
        self.models = {}
        self.tokenizers = {}
        
    async def load_model(self, model_name: str):
        if model_name not in self.models:
            if model_name == "deepseek":
                model_id = "deepseek-ai/deepseek-coder-1.3b-base"
            elif model_name == "qwen":
                model_id = "Qwen/Qwen-1_8B"
            else:
                raise ValueError(f"Unknown model: {model_name}")
            
            # Load model with 4-bit quantization for memory efficiency
            self.models[model_name] = AutoModelForCausalLM.from_pretrained(
                model_id,
                torch_dtype=torch.float16,
                load_in_4bit=True,
                device_map="auto"
            )
            self.tokenizers[model_name] = AutoTokenizer.from_pretrained(model_id)
            
    async def generate(self, request: GenerationRequest):
        model_name = request.model_name
        if model_name not in self.models:
            await self.load_model(model_name)
            
        model = self.models[model_name]
        tokenizer = self.tokenizers[model_name]
        
        inputs = tokenizer(request.text, return_tensors="pt").to(model.device)
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_length=request.max_length,
                temperature=request.temperature,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
            
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response

model_service = ModelService()

@app.post("/generate")
async def generate(request: GenerationRequest, api_key: str = Depends(verify_api_key)):
    try:
        result = await model_service.generate(request)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/models")
async def list_models():
    return {
        "available_models": [
            {
                "name": "deepseek",
                "description": "DeepSeek Coder 1.3B base model"
            },
            {
                "name": "qwen",
                "description": "Qwen 1.8B model"
            }
        ]
    } 