from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import datetime
from typing import Optional, List
from app.schemas.note import NoteCreate, NoteUpdate, NoteResponse, ShareRequest, ShareResponse
from app.models.note import Note, NoteVersion
from app.models.user import User
from app.api.deps import get_current_user
from app.core.security import hash_password
import secrets

router = APIRouter(prefix="/notes", tags=["Notes"])

def to_response(n: Note) -> NoteResponse:
    return NoteResponse(
        id=str(n.id), title=n.title, body=n.body, folder=n.folder, tags=n.tags,
        is_pinned=n.is_pinned, is_favorite=n.is_favorite, is_deleted=n.is_deleted,
        share_token=n.share_token, version=n.version,
        created_at=n.created_at, updated_at=n.updated_at,
    )

@router.get("", response_model=List[NoteResponse])
async def list_notes(
    folder: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    include_deleted: bool = Query(False),
    user: User = Depends(get_current_user),
):
    query = Note.find(Note.owner.id == user.id)
    if not include_deleted:
        query = query.find(Note.is_deleted == False)
    notes = await query.sort(-Note.is_pinned, -Note.updated_at).to_list()
    if folder:
        notes = [n for n in notes if n.folder == folder]
    if tag:
        notes = [n for n in notes if tag in n.tags]
    if search:
        s = search.lower()
        notes = [n for n in notes if s in n.title.lower() or s in n.body.lower()]
    return [to_response(n) for n in notes]

@router.post("", response_model=NoteResponse, status_code=201)
async def create_note(data: NoteCreate, user: User = Depends(get_current_user)):
    note = Note(owner=user, **data.model_dump())
    await note.insert()
    await NoteVersion(note=note, version=1, title=note.title, body=note.body).insert()
    return to_response(note)

@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(note_id: str, user: User = Depends(get_current_user)):
    note = await Note.get(note_id)
    if not note or str(note.owner.ref.id) != str(user.id) or note.is_deleted:
        raise HTTPException(status_code=404, detail="Note not found")
    return to_response(note)

@router.patch("/{note_id}", response_model=NoteResponse)
async def update_note(note_id: str, data: NoteUpdate, user: User = Depends(get_current_user)):
    note = await Note.get(note_id)
    if not note or str(note.owner.ref.id) != str(user.id) or note.is_deleted:
        raise HTTPException(status_code=404, detail="Note not found")
    updates = data.model_dump(exclude_unset=True)
    if not updates:
        return to_response(note)
    # Snapshot current version before mutating
    await NoteVersion(note=note, version=note.version, title=note.title, body=note.body).insert()
    note.version += 1
    for k, v in updates.items():
        setattr(note, k, v)
    note.updated_at = datetime.utcnow()
    await note.save()
    return to_response(note)

@router.post("/{note_id}/duplicate", response_model=NoteResponse, status_code=201)
async def duplicate_note(note_id: str, user: User = Depends(get_current_user)):
    src = await Note.get(note_id)
    if not src or str(src.owner.ref.id) != str(user.id) or src.is_deleted:
        raise HTTPException(status_code=404, detail="Note not found")
    dup = Note(
        owner=user, title=f"{src.title} (copy)", body=src.body, folder=src.folder,
        tags=list(src.tags), is_pinned=False, is_favorite=False,
    )
    await dup.insert()
    await NoteVersion(note=dup, version=1, title=dup.title, body=dup.body).insert()
    return to_response(dup)

@router.delete("/{note_id}")
async def delete_note(note_id: str, user: User = Depends(get_current_user)):
    note = await Note.get(note_id)
    if not note or str(note.owner.ref.id) != str(user.id):
        raise HTTPException(status_code=404, detail="Note not found")
    note.is_deleted = True
    note.deleted_at = datetime.utcnow()
    await note.save()
    return {"detail": "Note moved to trash"}

@router.post("/{note_id}/restore", response_model=NoteResponse)
async def restore_note(note_id: str, user: User = Depends(get_current_user)):
    note = await Note.get(note_id)
    if not note or str(note.owner.ref.id) != str(user.id) or not note.is_deleted:
        raise HTTPException(status_code=404, detail="Deleted note not found")
    note.is_deleted = False
    note.deleted_at = None
    await note.save()
    return to_response(note)

@router.delete("/{note_id}/permanent")
async def permanent_delete(note_id: str, user: User = Depends(get_current_user)):
    note = await Note.get(note_id)
    if not note or str(note.owner.ref.id) != str(user.id):
        raise HTTPException(status_code=404, detail="Note not found")
    await NoteVersion.find(NoteVersion.note.id == note.id).delete()
    await note.delete()
    return {"detail": "Note permanently deleted"}

@router.post("/{note_id}/share", response_model=ShareResponse)
async def share_note(note_id: str, data: ShareRequest, user: User = Depends(get_current_user)):
    note = await Note.get(note_id)
    if not note or str(note.owner.ref.id) != str(user.id) or note.is_deleted:
        raise HTTPException(status_code=404, detail="Note not found")
    token = secrets.token_urlsafe(24)
    note.share_token = token
    note.share_expires_at = (
        datetime.utcnow() + __import__("datetime").timedelta(days=data.expires_in_days)
        if data.expires_in_days else None
    )
    if data.password:
        note.share_password_hash = hash_password(data.password)
    await note.save()
    from app.core.config import settings
    return ShareResponse(
        share_url=f"{settings.FRONTEND_URL}/share/{token}",
        share_token=token,
        expires_at=note.share_expires_at,
    )