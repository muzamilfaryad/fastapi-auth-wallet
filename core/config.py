from functools import lru_cache
import os

from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseModel):
    app_name: str = "Complete Auth FastAPI"
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./auth.db")
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-this")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    refresh_token_expire_days: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))
    reset_token_expire_minutes: int = int(os.getenv("RESET_TOKEN_EXPIRE_MINUTES", 30))
    password_reset_base_url: str = os.getenv("PASSWORD_RESET_BASE_URL", "http://localhost:3000/reset-password")
    smtp_server: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", 587))
    smtp_user: str = os.getenv("SMTP_USER", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")


@lru_cache
def get_settings() -> Settings:
    return Settings()
