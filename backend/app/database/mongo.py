from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import settings

_client: AsyncIOMotorClient | None = None


async def connect():
    global _client
    _client = AsyncIOMotorClient(settings.mongodb_url)
    await _client.admin.command("ping")
    print(f"MongoDB connected: {settings.mongodb_url}")


async def disconnect():
    global _client
    if _client:
        _client.close()
        _client = None
        print("MongoDB disconnected")


def get_db() -> AsyncIOMotorDatabase:
    if _client is None:
        raise RuntimeError("MongoDB is not connected")
    return _client[settings.mongodb_db_name]
