from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer
from src.utils.security import verify_token, create_access_token
from sqlalchemy.orm import Session
from src.database.database import get_db
from src.database import models
from datetime import timedelta


security = HTTPBearer()


def get_current_user(token: str = Security(security), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = verify_token(token)
        email: str = payload.get("email")
        if email is None:
            raise credentials_exception
    except:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user
    

def authorize_user(user = Depends(get_current_user), roles: list[str] = []):
    if roles and user.role not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return user



def create_jwt_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    access_token = create_access_token(to_encode, expires_delta)
    return access_token

def get_user_roles(user: models.User):
    if user.is_admin:
        return ["admin"]
    else:
        return []
