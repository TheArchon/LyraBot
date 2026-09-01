from datetime import datetime, timezone

from Shizu.core.mongo import db


async def add_favourite(user_id: int, track) -> bool:
    await db.favourites.update_one(
        {
            "user_id": user_id,
            "track.id": track.id,
        },
        {
            "$set": {
                "user_id": user_id,
                "track": track.to_dict(),
                "created_at": datetime.now(timezone.utc),
            }
        },
        upsert=True,
    )

    return True


async def list_favourites(user_id: int, limit: int = 30) -> list[dict]:
    cursor = db.favourites.find({"user_id": user_id}).sort("created_at", -1)
    return await cursor.to_list(length=min(limit, 50))


async def remove_favourite(user_id: int, index: int):
    docs = await list_favourites(user_id, 50)

    if index < 1 or index > len(docs):
        return False

    result = await db.favourites.delete_one({"_id": docs[index - 1]["_id"]})
    return result.deleted_count == 1
