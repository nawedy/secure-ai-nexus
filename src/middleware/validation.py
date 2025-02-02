from fastapi import Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError, BaseModel, EmailStr
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class InputValidator:
    """
    Middleware for validating incoming request data against predefined schemas.

    Features:
    - Validates request body against endpoint-specific schemas
    - Handles validation errors with appropriate HTTP responses
    - Logs validation failures for monitoring
    - Supports custom schema definitions per endpoint

    Usage:
    ```python
    app = FastAPI()
    app.middleware("http")(InputValidator())
    ```
    """

    async def __call__(self, request: Request, call_next):
        """
        Process incoming requests and validate their data.

        Args:
            request (Request): The incoming FastAPI request
            call_next (Callable): The next middleware in the chain

        Returns:
            Response: The HTTP response, either from validation error or next middleware
        """
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.json()
                await self.validate_request_body(request.url.path, body)
            except ValidationError as e:
                logger.warning(f"Validation error for {request.url.path}: {str(e)}")
                return JSONResponse(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    content={"detail": str(e)}
                )
            except Exception as e:
                logger.error(f"Validation error: {str(e)}", exc_info=True)
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"detail": "Invalid request data"}
                )

        return await call_next(request)

    async def validate_request_body(self, path: str, body: dict):
        """
        Validate request body against predefined schemas.

        Args:
            path (str): The endpoint path
            body (dict): The request body to validate

        Raises:
            ValidationError: If the body fails schema validation
        """
        endpoint_schemas = {
            "/api/auth/login": LoginSchema,
            "/api/auth/signup": SignupSchema,
            "/api/models/create": ModelCreateSchema,
            "/api/models/update": ModelUpdateSchema
        }

        if path in endpoint_schemas:
            schema = endpoint_schemas[path]
            schema(**body)

class LoginSchema(BaseModel):
    email: EmailStr
    password: str

class SignupSchema(BaseModel):
    email: EmailStr
    password: str
    name: str
    company: Optional[str]

class ModelCreateSchema(BaseModel):
    name: str
    description: str
    framework: str
    version: str

class ModelUpdateSchema(BaseModel):
    name: Optional[str]
    description: Optional[str]
    version: Optional[str]
