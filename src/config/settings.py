"""
This module defines the settings for the application.
"""
from pydantic import BaseSettings, Field
from functools import lru_cache
from fastapi.security import OAuth2PasswordBearer
from typing import List

class Settings(BaseSettings):
    """Settings for the application."""
    PROJECT_NAME: str = Field(..., env="PROJECT_NAME")
    API_PREFIX: str = Field("/api", env="API_PREFIX")
    BCRYPT_ROUNDS: int = Field(12, env="BCRYPT_ROUNDS")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    ALLOWED_HOSTS: List[str] = Field(["localhost"], env="ALLOWED_HOSTS")
    DEBUG: bool = Field(False, env="DEBUG")
    OAUTH2_SCHEME: OAuth2PasswordBearer = Field(OAuth2PasswordBearer(tokenUrl="/api/auth/login"), env="OAUTH2_SCHEME") # scheme for the oauth2
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    JWT_SECRET_KEY: str = Field(..., env="JWT_SECRET_KEY")
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    ALGORITHM: str = Field("HS256", env="ALGORITHM")
    SMTP_SERVER: str = Field(..., env="SMTP_SERVER")
    SMTP_PORT: int = Field(..., env="SMTP_PORT")
    SMTP_USERNAME: str = Field(..., env="SMTP_USERNAME")
    SMTP_PASSWORD: str = Field(..., env="SMTP_PASSWORD")
    FRONTEND_URL: str = Field(..., env="FRONTEND_URL") # url for the frontend
    
    class Config:
        env_prefix = "PROD_"
        env_file = ".env"
    """
    Configuration for the application.
    Load the variable in the .env file.
    """
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()

# Example of how to use the settings:
# from src.config.settings import settings
#
# print(settings.PROJECT_NAME)
# print(settings.API_PREFIX)
# print(settings.BCRYPT_ROUNDS)
# print(settings.ACCESS_TOKEN_EXPIRE_MINUTES)
# print(settings.ALLOWED_HOSTS)
# print(settings.DEBUG)
# print(settings.OAUTH2_SCHEME)
#

# from google.cloud import secretmanager
# class Settings:
#     PROJECT_ID: str
#     REGION: str
#     # ... other GCP-specific settings
