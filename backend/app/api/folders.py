from fastapi import APIRouter, Depends
from typing import List
from app.models.note import Note
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter(prefix="/folders", tags=["Folders"])

@router.get("", response_model=List[dict])
async def list_folders(user: User = Depends(get_current_user)):
    notes = await Note.find(
        Note.owner.id == user.id, Note.is_deleted == False
    ).to_list()
    counts = {}
    for n in notes:
        counts[n.folder] = counts.get(n.folder, 0) + 1
    return [{"name": k, "count": v} for k, v in sorted(counts.items())]