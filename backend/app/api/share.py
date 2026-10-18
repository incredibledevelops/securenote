from fastapi import APIRouter, HTTPException
from datetime import datetime
from app.models.note import Note
from app.schemas.note import PublicNoteResponse

router = APIRouter(prefix="/public", tags=["Public Share"])

@router.get("/{token}", response_model=PublicNoteResponse)
async def get_shared_note(token: str):
    note = await Note.find_one(Note.share_token == token)
    if not note:
        raise HTTPException(status_code=404, detail="Shared note not found")
    if note.share_expires_at and note.share_expires_at < datetime.utcnow():
        raise HTTPException(status_code=410, detail="Share link expired")
    owner = await note.owner.fetch()
    return PublicNoteResponse(
        title=note.title, body=note.body, folder=note.folder, tags=note.tags,
        updated_at=note.updated_at, author_name=owner.full_name if owner else "Anonymous",
    )