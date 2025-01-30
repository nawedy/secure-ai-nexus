from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2AuthorizationCodeBearer
from .security.auth import get_current_user
from .security.azure_setup import AzureSecuritySetup
from .models.security import ModelSecurity
import logging
from .monitoring.middleware import MonitoringMiddleware
from .monitoring.alerts import AlertManager
from .monitoring.metrics import MetricsManager
from .monitoring.logging import SecureLogger

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="SecureAI Platform")

# Security setup
azure_setup = AzureSecuritySetup()
model_security = ModelSecurity(azure_setup.key_vault_client)

# Monitoring setup
metrics_manager = MetricsManager()
secure_logger = SecureLogger()
alert_manager = AlertManager()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add middleware
app.add_middleware(MonitoringMiddleware)

@app.on_event("startup")
async def startup_event():
    """Initialize security and monitoring components on startup"""
    try:
        await azure_setup.setup_key_vault()

        # Set up monitoring
        await alert_manager.setup_alerts()

        logger.info("Security and monitoring initialization completed")
    except Exception as e:
        logger.error(f"Initialization failed: {str(e)}")
        raise

@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {"status": "healthy"}

@app.get("/secure")
async def secure_endpoint(current_user = Depends(get_current_user)):
    """Test secured endpoint"""
    return {"message": "Access granted", "user": current_user}
