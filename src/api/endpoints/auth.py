from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.orm import Session
from typing import Dict, Any


from src.database.database import get_db, engine
from src.auth import auth_service, authorize_user, get_current_user
from src.database import models
from pydantic import BaseModel, EmailStr, constr, validator
from src.middleware.rate_limiter import rate_limiter_middleware
import re
from src.utils.validation import password_validator, is_valid_uuid
from src.utils.constants import INCORRECT_EMAIL_OR_PASSWORD, USER_NOT_FOUND, PASSWORD_RESET_EMAIL_SENT, PASSWORD_RESET

router = APIRouter(prefix="/auth")



class UserRegister(BaseModel):
    email: EmailStr
    password: constr(min_length=8)

    _password_validator = validator("password", allow_reuse=True)(password_validator)


class UserLogin(BaseModel):
    email: EmailStr
    password: constr(min_length=8)


class UserPasswordReset(BaseModel):
    password: constr(min_length=8)


class UserReset(BaseModel):
    email: EmailStr

class PasswordResetRequest(BaseModel):
    email: EmailStr

def validate_user_registration_data(user_data: Dict[str, Any]):
    """Validates the user registration data.

    Args:
        user_data (Dict[str, Any]): The user registration data to validate.

    Raises:
        HTTPException: If the email or password is empty, or if the password is less than 8 characters.
    """
    if not user_data["email"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email cannot be empty")
    if not user_data["password"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password cannot be empty")
    if len(user_data["password"]) < 8:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must be at least 8 characters long")
    if not re.match(r"[^@]+@[^@]+\.[^@]+", user_data["email"]):
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email format")

def validate_user_login_data(user_data: Dict[str, Any]):
    """Validates the user login data.

    Args:
        user_data (Dict[str, Any]): The user login data to validate.

    Raises:
        HTTPException: If the email or password is empty
    """
    if not user_data["email"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email cannot be empty")
    if not user_data["password"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password cannot be empty")

def validate_password_reset_request_data(user_data: Dict[str, Any]):
    """Validates the password reset request data.

    Args:
        user_data (Dict[str, Any]): The password reset request data to validate.

    Raises:
        HTTPException: If the email is empty or has invalid format.
    """
    if not user_data["email"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email cannot be empty")
    if not re.match(r"[^@]+@[^@]+\.[^@]+", user_data["email"]):
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email format")
@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    try:
        validate_user_registration_data(user_data.model_dump())
        user = auth_service.create_user(db, user_data.model_dump())
        if not user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creating user",
            )
        return {"message": "User created successfully", "user_id": user.id}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal server error occurred during user registration.")
        


@router.post("/login", status_code=status.HTTP_200_OK)
async def login_user(user_data: UserLogin, db: Session = Depends(get_db)):
    validate_user_login_data(user_data.model_dump())
    try:
        user = auth_service.authenticate_user(db, user_data.model_dump())
        token = auth_service.create_token(user)
        return {"message": "Login successful", "access_token": token, "token_type": "bearer"}
    except HTTPException as e:
        raise e
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=INCORRECT_EMAIL_OR_PASSWORD
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal server error occurred during login.")

@router.post("/password-reset-request", status_code=status.HTTP_200_OK, dependencies=[Depends(rate_limiter_middleware)])

async def request_password_reset(
    password_reset_request: PasswordResetRequest, db: Session = Depends(get_db)
):
    validate_password_reset_request_data(password_reset_request.model_dump())
    try:
        email = password_reset_request.email
        user = db.query(models.User).filter(models.User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=USER_NOT_FOUND,
            )
        auth_service.send_password_reset_email(db, user.email)
        return {"message": PASSWORD_RESET_EMAIL_SENT}

    except HTTPException as http_exc:
        raise http_exc
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send password reset email",
        )



@router.post("/password-reset", status_code=status.HTTP_200_OK, dependencies=[Depends(rate_limiter_middleware)])
async def reset_password(user_data: UserReset, db: Session = Depends(get_db)):
     auth_service.reset_password(db, user_data.model_dump())
     return {"message": PASSWORD_RESET_EMAIL_SENT}


@router.post("/reset-password", status_code=status.HTTP_200_OK, dependencies=[Depends(rate_limiter_middleware)])
async def confirm_password_reset( 
    user_data: UserPasswordReset, token: str = Query(...), db: Session = Depends(get_db)
):
   auth_service.confirm_reset_password(db, user_data.model_dump(), token)
   return {"message": PASSWORD_RESET}


router = APIRouter(prefix="/auth", dependencies=[Depends(get_current_user)])
@router.post("/logout", status_code=status.HTTP_200_OK, dependencies=[Depends(rate_limiter_middleware)])
@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    user=Depends(authorize_user),
    token: str = Query(...),
    db: Session = Depends(get_db),
):
    return {"message": auth_service.revoke_token(db, token)}

if __name__ == "__main__":
    pass
