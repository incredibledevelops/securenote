from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class NoteCreate(BaseModel):
    title: str = "Untitled note"
    body: str = ""
    folder: str = "Unfiled"
    tags: List[str] = []

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None
    folder: Optional[str] = None
    tags: Optional[List[str]] = None
    is_pinned: Optional[bool] = None
    is_favorite: Optional[bool] = None

class NoteResponse(BaseModel):
    id: str
    title: str
    body: str
    folder: str
    tags: List[str]
    is_pinned: bool
    is_favorite: bool
    is_deleted: bool
    share_token: Optional[str]
    version: int
    created_at: datetime
    updated_at: datetime

class ShareRequest(BaseModel):
    expires_in_days: Optional[int] = 7
    password: Optional[str] = None

class ShareResponse(BaseModel):
    share_url: str
    share_token: str
    expires_at: Optional[datetime]

class PublicNoteResponse(BaseModel):
    title: str
    body: str
    folder: str
    tags: List[str]
    updated_at: datetime
    author_name: str