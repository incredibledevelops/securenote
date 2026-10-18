from beanie import Document, Indexed
from pydantic import EmailStr, Field
from datetime import datetime
from typing import Optional

class User(Document):
    email: Indexed(EmailStr, unique=True)
    phone: Optional[str] = None
    full_name: str
    hashed_password: str
    is_active: bool = True
    is_admin: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

    class Settings:
        name = "users"
        indexes = ["email"]