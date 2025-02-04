from pydantic import BaseSettings, Field
from functools import lru_cache
from fastapi.security import OAuth2PasswordBearer
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = Field(..., env="PROJECT_NAME")
    API_PREFIX: str = Field("/api", env="API_PREFIX")
    BCRYPT_ROUNDS: int = Field(12, env="BCRYPT_ROUNDS")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    ALLOWED_HOSTS: List[str] = Field(["*"], env="ALLOWED_HOSTS")
    DEBUG: bool = Field(False, env="DEBUG")
    OAUTH2_SCHEME: OAuth2PasswordBearer = Field(OAuth2PasswordBearer(tokenUrl="/api/auth/login"), env="OAUTH2_SCHEME")
    SECRET_KEY: str = Field("secretkey", env="SECRET_KEY")
    ALGORITHM: str = Field("HS256", env="ALGORITHM")
    SMTP_SERVER: str = Field("localhost", env="SMTP_SERVER")
    SMTP_PORT: int = Field(25, env="SMTP_PORT")
    SMTP_USERNAME: str = Field("user", env="SMTP_USERNAME")
    SMTP_PASSWORD: str = Field("pass", env="SMTP_PASSWORD")
    FRONTEND_URL: str = Field("http://localhost:5173", env="FRONTEND_URL")

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
