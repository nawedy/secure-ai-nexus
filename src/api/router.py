"""
This module defines the main API router for the application.
It aggregates routes from different endpoints.
"""
from fastapi import APIRouter
from src.middleware.error_handler import error_handler_middleware
from .endpoints import auth, monitoring



# Initialize main API router
api_router = APIRouter()

# Include routes from different endpoints into the main router
api_router.include_router(auth.router, tags=["Authentication"])
api_router.include_router(monitoring.router, tags=["Monitoring"])

api_router.middleware("http")(error_handler_middleware)
