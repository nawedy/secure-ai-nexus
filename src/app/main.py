from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
from ..api.endpoints import health, models, auth
from ..middleware.metrics import metrics_middleware
from ..middleware.logging import logging_middleware
from ..utils.logging_config import log_config, security_logger
import logging

logger = logging.getLogger(__name__)

app = FastAPI(title="SecureAI Platform")

# Add middlewares
app.middleware("http")(logging_middleware)  # Add logging middleware first
app.middleware("http")(metrics_middleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(models.router, prefix="/api/models", tags=["models"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])

@app.on_event("startup")
async def startup_event():
    logger.info("Application starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutting down...")
