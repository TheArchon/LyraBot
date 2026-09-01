import random
import re
from datetime import datetime, timezone

from Shizu.config import settings
from Shizu.core.mongo import db
from Shizu.models import Track


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug[:48] or "playlist"


async def create_playlist(user_id: int, name: str):
    name = name.strip()[:64]

    if not name:
        return False, "invalid"

    count = await db.playlists.count_documents({"user_id": user_id})

    if count >= settings.max_playlists_per_user:
        return False, "limit"

    slug = slugify(name)

    if await db.playlists.find_one({"user_id": user_id, "slug": slug}):
        return False, "exists"

    now = datetime.now(timezone.utc)

    await db.playlists.insert_one(
        {
            "user_id": user_id,
            "name": name,
            "slug": slug,
            "tracks": [],
            "created_at": now,
            "updated_at": now,
        }
    )

    return True, slug


async def list_playlists(user_id: int) -> list[dict]:
    cursor = db.playlists.find({"user_id": user_id}).sort("updated_at", -1)
    return await cursor.to_list(length=settings.max_playlists_per_user)


async def get_playlist(user_id: int, slug: str) -> dict | None:
    return await db.playlists.find_one(
        {
            "user_id": user_id,
            "slug": slug,
        }
    )


async def add_track(user_id: int, slug: str, track: Track):
    playlist = await get_playlist(user_id, slug)

    if not playlist:
        return False, "not_found"

    tracks = playlist.get("tracks", [])

    if len(tracks) >= settings.max_tracks_per_playlist:
        return False, "full"

    if any(item.get("id") == track.id for item in tracks):
        return False, "duplicate"

    result = await db.playlists.update_one(
        {"user_id": user_id, "slug": slug},
        {
            "$push": {"tracks": track.to_dict()},
            "$set": {"updated_at": datetime.now(timezone.utc)},
        },
    )

    return result.modified_count == 1, "ok"


async def remove_track(user_id: int, slug: str, index: int):
    playlist = await get_playlist(user_id, slug)

    if not playlist:
        return False, "not_found"

    tracks = playlist.get("tracks", [])

    if index < 1 or index > len(tracks):
        return False, "index"

    tracks.pop(index - 1)

    await db.playlists.update_one(
        {"user_id": user_id, "slug": slug},
        {
            "$set": {
                "tracks": tracks,
                "updated_at": datetime.now(timezone.utc),
            }
        },
    )

    return True, "ok"


async def delete_playlist(user_id: int, slug: str) -> bool:
    result = await db.playlists.delete_one(
        {"user_id": user_id, "slug": slug}
    )
    return result.deleted_count == 1


async def playlist_tracks(user_id: int, slug: str, shuffle: bool = False):
    playlist = await get_playlist(user_id, slug)

    if not playlist:
        return None, []

    tracks = list(playlist.get("tracks", []))

    if shuffle:
        random.shuffle(tracks)

    return playlist, [Track.from_dict(item) for item in tracks]
