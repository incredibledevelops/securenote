from fastapi import APIRouter, Depends
from typing import List
from app.models.user import User
from app.models.subscription import Subscription
from app.api.deps import get_admin_user

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/subscribers", response_model=List[dict])
async def list_subscribers(admin: User = Depends(get_admin_user)):
    subs = await Subscription.find(Subscription.status == "active").to_list()
    out = []
    for s in subs:
        u = await s.user.fetch()
        if u:
            out.append({
                "user_id": str(u.id),
                "email": u.email,
                "full_name": u.full_name,
                "status": s.status,
                "amount_ghs": s.amount_ghs,
                "current_period_end": s.current_period_end.isoformat() if s.current_period_end else None,
            })
    return out

@router.get("/stats")
async def stats(admin: User = Depends(get_admin_user)):
    active = await Subscription.find(Subscription.status == "active").count()
    total = await Subscription.find().count()
    return {"active_subscriptions": active, "total_subscriptions": total,
            "mrr_ghs": active * 20}