from fastapi import Depends, HTTPException, status
from src.utils.security import verify_token
from sqlalchemy.orm import Session
from src.database.database import get_db
from src.database import models

def authenticate_user(token: str, db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = verify_token(token)
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

def authorize_user(user = Depends(authenticate_user), roles: list[str] = []):
    if roles:
        #TODO: Add authorization logic
        print("TODO: add authorization logic")
    return user