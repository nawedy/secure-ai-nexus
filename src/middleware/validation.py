from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from pydantic import BaseModel, ValidationError

class InputValidationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        try:
            if request.method in ["POST", "PUT"]:
                content_type = request.headers.get("Content-Type")
                if content_type == "application/json":
                    body = await request.json()
                    if request.url.path == "/api/auth/register":
                        class UserRegisterValidation(BaseModel):
                            email: str
                            password: str
                        UserRegisterValidation.model_validate(body)
                    elif request.url.path == "/api/auth/login":
                        class UserLoginValidation(BaseModel):
                            email: str
                            password: str
                        UserLoginValidation.model_validate(body)
                    elif request.url.path == "/api/auth/password-reset":
                        class UserResetValidation(BaseModel):
                            email: str
                        UserResetValidation.model_validate(body)
                    else:
                        print("TODO: Add more input validation")
                else:
                    raise HTTPException(
                        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                        detail="Unsupported media type",
                    )
        except ValidationError as e:
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=e.errors(),
            )
        except Exception:
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid request body",
            )
        response = await call_next(request)
        return response