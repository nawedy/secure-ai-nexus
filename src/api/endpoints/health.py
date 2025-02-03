from fastapi import APIRouter, Response
from ..monitoring.metrics import MetricsManager
import psutil
import logging

router = APIRouter()
logger = logging.getLogger(__name__)
metrics = MetricsManager()

@router.get("/health")
async def health_check():
    """
    Health check endpoint for Kubernetes probes
    """
    try:
        # Check system resources
        memory = psutil.virtual_memory()
        metrics.update_memory_usage(memory.used)

        return {
            "status": "healthy",
            "memory_usage": f"{memory.percent}%",
            "cpu_usage": f"{psutil.cpu_percent()}%"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return Response(status_code=500)

@router.get("/readiness")
async def readiness_check():
    """
    Readiness check endpoint for Kubernetes probes
    """
    try:
        # Check database connection
        await check_database()

        # Check model service
        await check_model_service()

        return {"status": "ready"}
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        return Response(status_code=503)

async def check_database():
    """Check database connectivity"""
    from ...models.database import engine
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
    except Exception as e:
        logger.error(f"Database check failed: {str(e)}")
        raise

async def check_model_service():
    """Check model service availability"""
    from ...models.registry import model_registry
    try:
        models = await model_registry.list_models()
        if not models:
            raise Exception("No models available")
    except Exception as e:
        logger.error(f"Model service check failed: {str(e)}")
        raise
