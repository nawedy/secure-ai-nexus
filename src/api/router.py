"""
This module defines the main API router for the application.
It aggregates routes from different endpoints.
"""
from fastapi import APIRouter
from .endpoints import auth, monitoring
from src.config.settings import settings



# Initialize main API router with a prefix
api_router = APIRouter()

# Include routes from different endpoints into the main router
api_router.include_router(auth.router)
api_router.include_router(monitoring.router)

