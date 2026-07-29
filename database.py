from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from config import settings

_client: AsyncIOMotorClient | None = None


async def init_db() -> None:
    """Connect to MongoDB and initialize Beanie ODM (call on app startup)."""
    global _client
    from models import Expense, User

    _client = AsyncIOMotorClient(settings.database_url)
    await init_beanie(
        database=_client[settings.database_name],
        document_models=[User, Expense],
    )


async def close_db() -> None:
    """Close the MongoDB connection (call on app shutdown)."""
    if _client is not None:
        _client.close()
