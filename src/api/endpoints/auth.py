from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from src.database.database import get_db
from src.auth import auth_logic
from src.database import models
from pydantic import BaseModel, EmailStr, constr, validator

router = APIRouter(prefix="/auth")

class UserRegister(BaseModel):
    email: EmailStr
    password: constr(min_length=8)

    @validator("password")
    def password_validator(cls, value):
        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isalpha() for char in value):
            raise ValueError("Password must contain at least one letter")
        return value

class UserLogin(BaseModel):
    email: EmailStr
    password: constr(min_length=8)

class UserPasswordReset(BaseModel):
    password: constr(min_length=8)


class UserReset(BaseModel):
    email: EmailStr


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    user = auth_logic.create_user(db, user_data.model_dump())
    return {"message": "User created successfully", "user_id": user.id}

@router.post("/login")
async def login_user(user_data: UserLogin, db: Session = Depends(get_db)):
    user = auth_logic.authenticate_user(db, user_data.model_dump())
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    token = auth_logic.create_token(user)
    return {"access_token": token, "token_type": "bearer"}

@router.post("/password-reset")
async def reset_password(user_data: UserReset, db: Session = Depends(get_db)):
    user = auth_logic.reset_password(db, user_data.model_dump())
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return {"message": "Password reset email sent"}


@router.post("/reset-password")
async def confirm_password_reset(user_data: UserPasswordReset, token:str = Query(...), db: Session = Depends(get_db)):
    user = auth_logic.confirm_reset_password(db, user_data.model_dump(), token)
    return {"message": "Password reset"}