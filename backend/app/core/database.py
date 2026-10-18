from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.core.config import settings
from app.models.user import User
from app.models.note import Note, NoteVersion
from app.models.subscription import Subscription, WebhookEvent

client: AsyncIOMotorClient = None

async def init_db():
    global client
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    await init_beanie(
        database=client[settings.MONGODB_DB],
        document_models=[User, Note, NoteVersion, Subscription, WebhookEvent],
    )

async def close_db():
    global client
    if client:
        client.close()
        client = None