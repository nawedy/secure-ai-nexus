"""Main application entry point."""

from fastapi import FastAPI, Request, Form, HTTPException, Response
from fastapi.responses import JSONResponse
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import EmailStr
from src.config.settings import settings
from src.api.router import api_router
from src.middleware.logging import LoggingMiddleware
from src.middleware.error_handler import ErrorHandlerMiddleware
from src.middleware.metrics import MetricsMiddleware
from src.middleware.rate_limiter import RateLimiterMiddleware
from src.middleware.validation import InputValidationMiddleware
from src.middleware.security import SecurityHeadersMiddleware
from src.database.database import Base, engine
import logging
from src.utils.email import send_contact_email
from src.utils.validation import validate_contact

logger = logging.getLogger(__name__)


def get_application() -> FastAPI:
    """
    Creates and configures the FastAPI application.

    Returns: A configured FastAPI application instance.
    """
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.ALLOWED_HOSTS],
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            allow_headers=["*"],
        ),
        Middleware(ErrorHandlerMiddleware),
        Middleware(MetricsMiddleware),
        Middleware(LoggingMiddleware),
        Middleware(RateLimiterMiddleware, max_requests=100, time_window=60),
        Middleware(InputValidationMiddleware),
        Middleware(SecurityHeadersMiddleware),
    ]

    application = FastAPI(
        title=settings.PROJECT_NAME,
        debug=settings.DEBUG,
        middleware=middleware,
    )

    application.include_router(api_router, prefix=settings.API_PREFIX)
    return application


app = get_application()

app.mount("/static", StaticFiles(directory="static"), name="static")

Base.metadata.create_all(bind=engine)


@app.get("/health", tags=["Health Check"])
async def health_check():
    """Endpoint for health check.
    Returns: A JSON response indicating the application's status.
    """
    return JSONResponse(content={"status": "OK"}, status_code=200)


@app.get("/", tags=["Home"])
async def home():
    """Endpoint for the home page.
    Returns: A JSON response indicating the home page status.
    """
    return JSONResponse(content={"status": "OK"}, status_code=200)


@app.post("/api/contact", tags=["Contact"])
async def contact(
    name: str = Form(...),
    email: EmailStr = Form(...),
    message: str = Form(...),
):
    """
    Endpoint to handle contact form submissions.

    Args:
        name (str): Name of the sender.
        email (EmailStr): Email of the sender.
        message (str): Message from the sender.
    Returns: A JSON response indicating success or failure.
    """
    try:
        # check the validity of the input
        validate_contact(name, message)
        # send the email
        await send_contact_email(name, email, message)
        return JSONResponse(content={"status": "success"})
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error sending contact email: {e}")
        raise HTTPException(status_code=500, detail=str(e))
