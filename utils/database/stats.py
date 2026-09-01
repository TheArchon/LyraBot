from datetime import datetime, timezone

from Shizu.core.mongo import db


async def save_user(user) -> None:
    if not user or user.is_bot:
        return

    await db.users.update_one(
        {
            "user_id": user.id,
        },
        {
            "$set": {
                "user_id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username,
                "updated_at": datetime.now(
                    timezone.utc
                ),
            },
            "$setOnInsert": {
                "created_at": datetime.now(
                    timezone.utc
                ),
            },
        },
        upsert=True,
    )


async def save_chat(chat) -> None:
    if not chat:
        return

    chat_type = getattr(
        chat.type,
        "value",
        str(chat.type),
    )

    # We only count groups as groups.
    if chat_type not in {
        "group",
        "supergroup",
    }:
        return

    await db.chats.update_one(
        {
            "chat_id": chat.id,
        },
        {
            "$set": {
                "chat_id": chat.id,
                "title": chat.title,
                "username": chat.username,
                "type": chat_type,
                "active": True,
                "updated_at": datetime.now(
                    timezone.utc
                ),
            },
            "$setOnInsert": {
                "created_at": datetime.now(
                    timezone.utc
                ),
            },
        },
        upsert=True,
    )


async def mark_chat_inactive(
    chat_id: int,
) -> None:
    await db.chats.update_one(
        {
            "chat_id": chat_id,
        },
        {
            "$set": {
                "active": False,
                "updated_at": datetime.now(
                    timezone.utc
                ),
            }
        },
    )


async def get_stats() -> dict:
    users = await db.users.count_documents(
        {}
    )

    groups = await db.chats.count_documents(
        {}
    )

    active_groups = (
        await db.chats.count_documents(
            {
                "active": True,
            }
        )
    )

    return {
        "users": users,
        "groups": groups,
        "active_groups": active_groups,
    }


async def get_broadcast_users():
    cursor = db.users.find(
        {},
        {
            "_id": 0,
            "user_id": 1,
        },
    )

    return await cursor.to_list(
        length=None
    )


async def get_broadcast_groups():
    cursor = db.chats.find(
        {
            "active": True,
        },
        {
            "_id": 0,
            "chat_id": 1,
        },
    )

    return await cursor.to_list(
        length=None
    )