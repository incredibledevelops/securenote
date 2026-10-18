from beanie import Document, Indexed, Link
from pydantic import Field
from datetime import datetime
from typing import Optional, List
from app.models.user import User

class Note(Document):
    owner: Link[User]
    title: str = "Untitled note"
    body: str = ""
    folder: str = "Unfiled"
    tags: List[str] = []
    is_pinned: bool = False
    is_favorite: bool = False
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    share_token: Optional[str] = None
    share_expires_at: Optional[datetime] = None
    share_password_hash: Optional[str] = None
    version: int = 1
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "notes"
        indexes = [
            "owner",
            "folder",
            "tags",
            "updated_at",
            [("owner", 1), ("is_deleted", 1), ("updated_at", -1)],
        ]

class NoteVersion(Document):
    note: Link[Note]
    version: int
    title: str
    body: str
    saved_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "note_versions"
        indexes = [[("note", 1), ("version", -1)]]