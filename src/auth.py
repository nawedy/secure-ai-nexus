from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from src.database import models
from src.utils.security import get_password_hash, verify_password, create_access_token, verify_token, JWTError
from datetime import timedelta, datetime
import os
import logging
from src.database.database import get_db
from src.utils.email import send_password_reset_email
import uuid

logger = logging.getLogger(__name__)


def commit_or_rollback(db: Session, operation_name: str):
    """Utility function to handle database commits and rollbacks."""
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error during {operation_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during {operation_name}",
        )

def revoke_token(db: Session, token: str):
    """Revokes a token by adding it to the RevokedToken table."""
    try:
        db_revoked_token = models.RevokedToken(token=token, expires=datetime.utcnow() + timedelta(hours=1))
        db.add(db_revoked_token)
        db.commit()
        db.refresh(db_revoked_token)
    except Exception as e:
        db.rollback()
        logger.error(f"Error revoking token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error revoking token",
        )



def create_user(db: Session, user_data: dict):
    """Creates a new user in the database."""
    db_user = db.query(models.User).filter(models.User.email == user_data["email"]).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )
    hashed_password = get_password_hash(user_data["password"])
    db_user = models.User(email=user_data["email"], password=hashed_password)
    db.add(db_user)
    commit_or_rollback(db, "user creation")
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, user_data: dict):
    """Authenticates a user based on email and password."""
    db_user = db.query(models.User).filter(models.User.email == user_data["email"]).first()
    if not db_user or not verify_password(user_data["password"], db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password"
        )
    return db_user


def create_token(user):
    """Creates an access token for a user."""
    expires_delta = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)))
    access_token = create_access_token(data={"sub": user.email}, expires_delta=expires_delta)
    return access_token


def _generate_reset_token_and_update_user(db: Session, user: models.User) -> str:
    """Generates a reset token and updates the user in the database."""
    token = str(uuid.uuid4())
    user.reset_token = token
    user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
    commit_or_rollback(db, "password reset token generation")
    return token


def reset_password(db: Session, user_data: dict):
    """Initiates the password reset process for a user."""
    user = db.query(models.User).filter(models.User.email == user_data["email"]).first()
    if user:
        token = _generate_reset_token_and_update_user(db, user)
        send_password_reset_email(user.email, token)
        logger.info(f"Password reset email sent to {user.email}")
    return user


def confirm_reset_password(db: Session, user_data: dict, token: str):
    """Confirms the password reset process for a user."""
    user = db.query(models.User).filter(
        models.User.reset_token == token, models.User.reset_token_expires > datetime.utcnow()
    ).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token"
        )
    hashed_password = get_password_hash(user_data["password"])
    user.password = hashed_password
    user.reset_token = None
    user.reset_token_expires = None
    commit_or_rollback(db, "password reset confirmation")
        
    # Limit the number of tries
    now = datetime.utcnow()
    one_hour_ago = now - timedelta(hours=1)
    if user.reset_password_last_try is None or user.reset_password_last_try < one_hour_ago:
        user.reset_password_tries = 1
        user.reset_password_last_try = now
    else:
        user.reset_password_tries += 1
    
        if user.reset_password_tries > 3:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many password reset attempts. Please try again later.",
            )
        user.reset_password_last_try = now

    db.commit()

    commit_or_rollback(db, "password reset confirmation")
    return user

def get_current_user(token: str, db: Session = Depends(get_db)):
    """
    Retrieves the current user from the database based on the provided token.
    
    Args:
        token: the user token
        db: the database session
    Raises:
        credentials_exception: if the token is invalid
    Returns:
        the user
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
        db_revoked_token = db.query(models.RevokedToken).filter(models.RevokedToken.token == token).first()
    )
    try:
        payload = verify_token(token)
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError as e:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

def authorize_user(user: models.User = Depends(get_current_user), roles: list[models.UserRole] = []):
    """
    Check if the user has the right role.
    Args:
        user: the user
        roles: the required roles
    Raises:
        HTTPException: if the user does not have the right role.
    Returns: the user
    """
    if roles and user.role not in roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    return user
