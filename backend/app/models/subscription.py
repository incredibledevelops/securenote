from beanie import Document, Link
from pydantic import Field
from datetime import datetime
from typing import Optional
from app.models.user import User

class Subscription(Document):
    user: Link[User]
    plan_code: str = "pro_monthly"
    amount_ghs: int = 20
    status: str = "active"  # active | cancelled | past_due | trial
    paystack_customer_code: Optional[str] = None
    paystack_subscription_code: Optional[str] = None
    paystack_email_token: Optional[str] = None
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "subscriptions"
        indexes = ["user", "status", "paystack_subscription_code"]

class WebhookEvent(Document):
    event: str
    reference: Optional[str] = None
    payload: dict
    processed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "webhook_events"
        indexes = ["event", "reference", "created_at"]