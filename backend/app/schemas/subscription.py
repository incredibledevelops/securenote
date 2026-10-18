from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class InitializePaymentRequest(BaseModel):
    email: EmailStr

class InitializePaymentResponse(BaseModel):
    authorization_url: str
    access_code: str
    reference: str

class SubscriptionResponse(BaseModel):
    status: str
    plan_code: str
    amount_ghs: int
    current_period_end: Optional[datetime]