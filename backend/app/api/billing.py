from fastapi import APIRouter, Request, HTTPException, Depends
from datetime import datetime, timedelta
from bson import ObjectId
from app.schemas.subscription import (
    InitializePaymentRequest, InitializePaymentResponse, SubscriptionResponse
)
from app.models.subscription import Subscription, WebhookEvent
from app.models.user import User
from app.api.deps import get_current_user
from app.services import paystack
from app.core.config import settings
import secrets

router = APIRouter(prefix="/billing", tags=["Billing"])

@router.get("/subscription", response_model=SubscriptionResponse)
async def my_subscription(user: User = Depends(get_current_user)):
    sub = await Subscription.find_one(Subscription.user.id == user.id)
    if not sub:
        return SubscriptionResponse(status="trial", plan_code="free", amount_ghs=0, current_period_end=None)
    return SubscriptionResponse(
        status=sub.status, plan_code=sub.plan_code, amount_ghs=sub.amount_ghs,
        current_period_end=sub.current_period_end,
    )

@router.post("/initialize", response_model=InitializePaymentResponse)
async def initialize_payment(data: InitializePaymentRequest, user: User = Depends(get_current_user)):
    reference = f"SN-{secrets.token_hex(8).upper()}"
    result = await paystack.initialize_transaction(
        email=data.email,
        amount_kobo=2000 * 100,  # 20 GHS in kobo (pesewas)
        reference=reference,
        callback_url=f"{settings.FRONTEND_URL}/billing/callback",
    )
    # Persist a pending subscription record keyed by reference
    await WebhookEvent(
        event="payment.initialized",
        reference=reference,
        payload={"user_id": str(user.id), "authorization_url": result["authorization_url"]},
    ).insert()
    return InitializePaymentResponse(
        authorization_url=result["authorization_url"],
        access_code=result["access_code"],
        reference=reference,
    )

@router.post("/webhook")
async def paystack_webhook(request: Request):
    raw = await request.body()
    signature = request.headers.get("x-paystack-signature", "")
    if not paystack.verify_webhook_signature(raw, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    import json
    payload = json.loads(raw)
    event = payload.get("event")
    data = payload.get("data", {})
    reference = data.get("reference")

    # Idempotency: skip if we've already processed this exact event
    existing = await WebhookEvent.find_one(
        WebhookEvent.event == event, WebhookEvent.reference == reference,
        WebhookEvent.processed == True,
    )
    if existing:
        return {"status": "already_processed"}

    log = WebhookEvent(event=event, reference=reference, payload=payload, processed=True)

    if event == "charge.success":
        customer_email = data.get("customer", {}).get("email")
        user = await User.find_one(User.email == customer_email)
        if user:
            sub = await Subscription.find_one(Subscription.user.id == user.id)
            now = datetime.utcnow()
            if sub:
                sub.status = "active"
                sub.current_period_end = now + timedelta(days=30)
                sub.updated_at = now
            else:
                sub = Subscription(
                    user=user, status="active", plan_code="pro_monthly",
                    amount_ghs=20,
                    paystack_customer_code=data.get("customer", {}).get("customer_code"),
                    current_period_start=now,
                    current_period_end=now + timedelta(days=30),
                )
            await sub.save()

    elif event in ("subscription.disable", "invoice.payment_failed"):
        sub = await Subscription.find_one(Subscription.user.id == (await User.find_one(User.email == data.get("customer", {}).get("email"))).id) if data.get("customer", {}).get("email") else None
        if sub:
            sub.status = "cancelled" if event == "subscription.disable" else "past_due"
            await sub.save()

    await log.insert()
    return {"status": "ok"}