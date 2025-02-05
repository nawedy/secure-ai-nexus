"""
This module defines health check endpoints for the application.
It provides endpoints for Kubernetes probes to check the health and readiness of the application.
"""

from fastapi import APIRouter, Response, Depends
from src.config.settings import settings
import psutil
import logging

router = APIRouter(prefix=settings.API_PREFIX)
"""APIRouter instance for health check endpoints."""
logger = logging.getLogger(__name__)
"""Logger instance for health check module."""



@router.get("/healthz", tags=["Health Check"])
async def health_check():
    """
    Health check endpoint for Kubernetes probes
    """
    try:
        # Check system resources
        memory = psutil.virtual_memory()

        return {
            "status": "healthy",
            "memory_usage": f"{memory.percent}%",
            "cpu_usage": f"{psutil.cpu_percent()}%"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return Response(status_code=500)


@router.get("/health", tags=["Health Check"])
async def health_check():
    """
    Health check endpoint to see if the app is running.
    """
    try:
        return {"status": "healthy"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return Response(status_code=500)

@router.get("/ready", tags=["Health Check"])
async def readiness_check():
    """
    Checks the readiness of the application.
    """
    """
    Readiness check endpoint for Kubernetes probes
    """
    try:
        # Check database connection
        await check_database()

        # Check model service
        await check_model_service()

        return {"status": "healthy"}
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        return Response(status_code=503)

async def check_database():
    """
    Checks the database connectivity.
    Raises:
        Exception: If database connection fails."""
    """Check database connectivity"""
    from ...models.database import engine
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
    except Exception as e:
        logger.error(f"Database check failed: {str(e)}")
        raise

async def check_model_service():
    """
    Checks the model service availability.
    Raises:
        Exception: If model service is unavailable."""
    """Check model service availability"""
    from ...models.registry import model_registry
    try:
        models = await model_registry.list_models()
        if not models:
            raise Exception("No models available")
    except Exception as e:
        logger.error(f"Model service check failed: {str(e)}")
        raise
