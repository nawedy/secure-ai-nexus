"""
This module defines the core LLM service, including model management and text generation.
"""

import logging
import os
from abc import ABC, abstractmethod
from typing import List, Literal, Optional

from fastapi import Depends, FastAPI, HTTPException, Request
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from src.middleware.auth import verify_api_key

app = FastAPI(title="LLM Service")

logger = logging.getLogger(__name__)


class GenerationRequest(BaseModel):
    """
    Represents a request to generate text using an LLM.
    """
    text: str
    model_name: Literal["openai", "mock"]
    max_length: Optional[int] = 1024
    temperature: Optional[float] = 0.7


class LLM(ABC):
    """
    Abstract base class for LLMs.
    """

    @abstractmethod
    async def generate_text(
        self, request: Request, prompt: str, max_length: int, temperature: float
    ) -> str:
        """
        Abstract method to generate text based on the given prompt.

        Args:
            request (Request): The HTTP request object.
            prompt (str): The prompt for generating text.
            max_length (int): The maximum length of the generated text.
            temperature (float): The temperature parameter for text generation.

        Returns:
            str: The generated text.
        """
        pass


class OpenAILLM(LLM):
    """
    OpenAI LLM implementation.
    """

    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        """
        Initializes the OpenAI LLM with the specified model.
        """
        try:
            self.llm = ChatOpenAI(model_name=model_name, temperature=0.7)
        except Exception as e:
            logger.error(f"Error initializing OpenAI LLM: {e}")
            raise

    async def generate_text(
        self, request: Request, prompt: str, max_length: int, temperature: float
    ) -> str:
        """
        Generates text using the OpenAI model.
        """
        try:
            message = await self.llm.ainvoke([{"role": "user", "content": prompt}])
            return message.content
        except Exception as e:
            logger.error(f"Error generating text with OpenAI LLM: {e}")
            raise


class MockLLM(LLM):
    """
    Mock LLM implementation for testing purposes.
    """

    async def generate_text(
        self, request: Request, prompt: str, max_length: int, temperature: float
    ) -> str:
        """
        Generates a mock response.
        Generates a mock response.
        """
        return f"Mock response to: {prompt}"


class ModelManager:
    """
    Manages available LLMs and handles model loading and selection.
    """

    def __init__(self):
        self.llms: List[LLM] = []
        self.available_models = {"openai": OpenAILLM, "mock": MockLLM}
        self.load_models()

    def load_models(self):
        """Loads all available LLMs."""
        for model_name, llm_class in self.available_models.items():
            try:
                self.llms.append(llm_class())
            except Exception as e:
                logger.error(f"Error loading model {model_name}: {e}")
                raise

    async def generate(self, request: GenerationRequest) -> str:
        """
        Generates text using the selected LLM.

        Args:
            request (GenerationRequest): The request containing the prompt,
                model name, max length, and temperature.

        Returns:
            str: The generated text.

        Raises:
            HTTPException: If the specified model is not available or loaded.
        """
        llm = self.get_llm(request.model_name)
        response = await llm.generate_text(
            request=None, prompt=request.text, max_length=request.max_length, temperature=request.temperature
        )
        return response

    def get_llm(self, model_name: str) -> LLM:
        """
        Retrieves a specific LLM instance by its name.

        Args:
            model_name (str): The name of the model to retrieve.

        Returns:
            LLM: An instance of the requested LLM.

        Raises:
            HTTPException: If the specified model is not available or loaded.
        """


        model_class = self.available_models.get(model_name)
        if not model_class:
            raise HTTPException(
                status_code=400, detail=f"Model {model_name} not available",
            )

        for llm in self.llms:
            if isinstance(llm, model_class):
                return llm

        raise HTTPException(
            status_code=400, detail=f"Model {model_name} not loaded"
        )


model_manager = ModelManager()


@app.post("/generate")
async def generate(
    request: GenerationRequest, api_key: str = Depends(verify_api_key)
):
    """
    Endpoint to generate text based on a given prompt and model.

    Args:
        request (GenerationRequest): The request body containing the prompt,
            model name, max length, and temperature.
        api_key (str, optional): The API key for authentication. Defaults to Depends(verify_api_key).

    Returns:
        dict: A dictionary containing the generated text.

    Raises:
        HTTPException: If there is an error during text generation.
    """
    try:
        result = await model_manager.generate(request)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check() -> dict:
    """
    Endpoint to check the health status of the service.

    Returns:
        dict: A dictionary indicating the health status.
    """
    return {"status": "healthy"}


@app.get("/models")
async def list_models() -> dict:
    """
    Endpoint to list the available models.
    Returns:
        dict: List of available models
    """
    return {
        "available_models": [
            {
                "name": "openai",
                "description": "OpenAI model",
            },
            {"name": "mock", "description": "Mock LLM"},
        ],
    }