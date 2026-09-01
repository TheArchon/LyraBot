from motor.motor_asyncio import AsyncIOMotorClient
from Shizu.config import settings

mongo_client = AsyncIOMotorClient(settings.mongo_uri)
db = mongo_client[settings.mongo_db_name]


async def ensure_indexes() -> None:
    await db.history.create_index(
        [
            ("chat_id", 1),
            ("played_at", -1),
        ]
    )

    await db.users.create_index(
        "user_id",
        unique=True,
    )

    await db.chats.create_index(
        "chat_id",
        unique=True,
    )

    await db.chats.create_index(
        "active"
    )