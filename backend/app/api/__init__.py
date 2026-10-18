from fastapi import APIRouter
from app.api import auth, notes, folders, share, billing, admin

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(notes.router)
api_router.include_router(folders.router)
api_router.include_router(share.router)
api_router.include_router(billing.router)
api_router.include_router(admin.router)