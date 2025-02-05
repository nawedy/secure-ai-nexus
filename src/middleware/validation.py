"""Middleware for input validation."""

from fastapi import Request, HTTPException, status, Depends
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from pydantic import BaseModel, ValidationError
from src.auth import get_current_user


class InputValidationMiddleware(BaseHTTPMiddleware):
    """Middleware for input validation."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        """
        Validates the request body if the method is POST or PUT and the content type is application/json.

        Args:
            request (Request): The incoming request.
            call_next (RequestResponseEndpoint): The next middleware or endpoint.

        Returns:
            Response: The response from the next middleware or endpoint.
        """
        try:
            if request.method in ["POST", "PUT"]:
                content_type = request.headers.get("Content-Type")
                if content_type == "application/json":
                    body = await request.json()
                    if request.url.path == "/api/auth/register":
                        # Validate the body for user register
                        class UserRegisterValidation(BaseModel):
                            email: str
                            password: str
                        UserRegisterValidation.model_validate(body)
                    elif request.url.path == "/api/auth/login":
                        # Validate the body for user login
                        class UserLoginValidation(BaseModel):
                            email: str
                            password: str
                        UserLoginValidation.model_validate(body)
                    elif request.url.path == "/api/auth/password-reset":
                        # Validate the body for password reset request
                        class UserResetValidation(BaseModel):
                            email: str
                        UserResetValidation.model_validate(body)
                    else:
                        pass
                        #TODO: Add more input validation
                else:
                    # Raise an exception if the content type is not json
                    raise HTTPException(
                        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                        detail="Unsupported media type",
                    )
        except ValidationError as e:
            # Raise an exception if the validation fail
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.errors())
        except Exception as e:
            # Raise an exception if another error occur
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        response = await call_next(request)
        return response