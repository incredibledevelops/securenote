import hmac
import hashlib
import httpx
from app.core.config import settings

PAYSTACK_BASE = "https://api.paystack.co"

async def initialize_transaction(email: str, amount_kobo: int, reference: str, callback_url: str):
    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"{PAYSTACK_BASE}/transaction/initialize",
            headers={"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"},
            json={
                "email": email,
                "amount": amount_kobo,
                "reference": reference,
                "callback_url": callback_url,
                "plan": settings.PAYSTACK_PLAN_CODE or None,
                "channels": ["card", "mobile_money", "bank"],
            },
        )
        res.raise_for_status()
        return res.json()["data"]

def verify_webhook_signature(raw_body: bytes, signature: str) -> bool:
    if not signature:
        return False
    expected = hmac.new(
        settings.PAYSTACK_SECRET_KEY.encode(), raw_body, hashlib.sha512
    ).hexdigest()
    return hmac.compare_digest(expected, signature)