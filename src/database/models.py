from sqlalchemy import Column, Integer, String, DateTime, Enum, SmallInteger
from src.database.database import Base
import enum

class UserRole(enum.Enum):
    user = "user"
    admin = "admin"

class User(Base):
    __tablename__ = "users"
    role = Column(Enum(UserRole), default=UserRole.user)
    email = Column(String, unique=True, index=True, primary_key=True)
    password = Column(String, nullable=False)
    reset_token = Column(String, nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)
    reset_password_tries = Column(SmallInteger, nullable=False, default=0)
    reset_password_last_try = Column(DateTime, nullable=True)

class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, index=True)
