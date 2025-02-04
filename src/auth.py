from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from src.database import models
from src.utils.security import get_password_hash, verify_password, create_access_token
from datetime import timedelta, datetime
import os
import logging
from src.utils.email import send_password_reset_email
import uuid

logger = logging.getLogger(__name__)

def commit_or_rollback(db: Session):
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error committing to database: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error committing to database"
        )

def create_user(db: Session, user_data: dict):
    # Check if a user with the given email already exists
    db_user = db.query(models.User).filter(models.User.email == user_data["email"]).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )
    # Hash the password and create a new user
    hashed_password = get_password_hash(user_data["password"])
    db_user = models.User(email=user_data["email"], password=hashed_password)
    db.add(db_user)
    commit_or_rollback(db)
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, user_data: dict):
    db_user = db.query(models.User).filter(models.User.email == user_data["email"]).first()
    if not db_user or not verify_password(user_data["password"], db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password"
        )
    return db_user

def create_token(user):
    expires_delta = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)))
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=expires_delta
    )
    return access_token

def update_user_reset_token(db: Session, user:models.User):
    """Update the user reset token"""
    token = str(uuid.uuid4())
    user.reset_token = token
    user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
    db.add(user)
    commit_or_rollback(db)
    return token

def reset_password(db: Session, user_data: dict):
    """Send an email with a token for the password reset"""
    # Check if a user with the given email exists
    user = db.query(models.User).filter(models.User.email == user_data["email"]).first()
    if user:
        # Update the user's token
        token = update_user_reset_token(db, user)
        # Send the email
        send_password_reset_email(user.email, token)
        logger.info(f"Password reset email sent to {user.email}")
    return user

def confirm_reset_password(db: Session, user_data: dict, token:str):
    """Reset the password of a user"""
    # Check if a user with the given token exists
    user = db.query(models.User).filter(models.User.reset_token == token, models.User.reset_token_expires > datetime.utcnow()).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token"
        )
    # Hash the new password and update the user
    hashed_password = get_password_hash(user_data["password"])
    user.password = hashed_password
    user.reset_token = None
    user.reset_token_expires = None
    db.add(user)
    commit_or_rollback(db)
    return user