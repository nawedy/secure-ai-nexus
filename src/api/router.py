from fastapi import APIRouter
from .endpoints import auth, models, monitoring

# Initialize main API router
api_router = APIRouter()

# Include routes from different endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(models.router, prefix="/models", tags=["models"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"])
