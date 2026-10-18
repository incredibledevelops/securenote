from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "Secure Notes API"
    APP_ENV: str = "development"
    SECRET_KEY: str = "dev-secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB: str = "secure_notes"

    PAYSTACK_SECRET_KEY: str = ""
    PAYSTACK_PUBLIC_KEY: str = ""
    PAYSTACK_PLAN_CODE: str = ""
    PAYSTACK_WEBHOOK_URL: str = ""

    FRONTEND_URL: str = "http://localhost:3000"

    # Comma-separated in .env — do NOT use a JSON list here.
    ADMIN_EMAILS: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def admin_email_list(self) -> List[str]:
        return [e.strip().lower() for e in self.ADMIN_EMAILS.split(",") if e.strip()]


settings = Settings()