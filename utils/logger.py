import logging

from datetime import (
    datetime,
    timezone,
)

from Shizu.config import settings
from Shizu.core.bot import bot
from Shizu.core.mongo import db

from Shizu.utils.formatters import (
    esc,
    user_link,
)


logger = logging.getLogger(
    __name__
)


async def get_bot_name() -> str:
    try:
        me = await bot.get_me()

        return esc(
            me.first_name
            or me.username
            or "Music Bot"
        )

    except Exception:
        return "Music Bot"


async def send_log(
    text: str,
) -> None:
    if not settings.log_group_id:
        return

    try:
        await bot.send_message(
            settings.log_group_id,
            text,
        )

    except Exception as exc:
        logger.warning(
            "Unable to send bot log: %s",
            exc,
        )


async def log_startup(
    me,
) -> None:
    bot_name = esc(
        me.first_name
        or me.username
        or "Music Bot"
    )

    await send_log(
        f"🚀 <b>{bot_name} started</b>\n\n"
        f"🤖 <b>Bot:</b> "
        f"@{esc(me.username)}\n"
        f"🆔 <b>ID:</b> "
        f"<code>{me.id}</code>\n"
        "🎧 <b>Music engine:</b> ready"
    )


async def log_user_start(
    message,
) -> None:
    user = message.from_user

    if not user:
        return

    now = datetime.now(
        timezone.utc
    )

    # First check the existing user.
    existing = await db.users.find_one(
        {
            "user_id": user.id,
        }
    )

    # User already started the bot before.
    if (
        existing
        and existing.get(
            "start_logged"
        )
    ):
        return

    # Existing user from old database:
    # mark first-start logging as completed.
    if existing:
        await db.users.update_one(
            {
                "user_id": user.id,
            },
            {
                "$set": {
                    "first_name": (
                        user.first_name
                    ),
                    "last_name": (
                        user.last_name
                    ),
                    "username": (
                        user.username
                    ),
                    "start_logged": True,
                    "start_logged_at": now,
                    "updated_at": now,
                }
            },
        )

    # Completely new user.
    else:
        await db.users.insert_one(
            {
                "user_id": user.id,
                "first_name": (
                    user.first_name
                ),
                "last_name": (
                    user.last_name
                ),
                "username": (
                    user.username
                ),
                "start_logged": True,
                "start_logged_at": now,
                "created_at": now,
                "updated_at": now,
            }
        )

    bot_name = (
        await get_bot_name()
    )

    await send_log(
        f"👤 <b>New {bot_name} User</b>\n\n"
        f"🧑 <b>User:</b> "
        f"{user_link(user)}\n"
        f"🆔 <b>ID:</b> "
        f"<code>{user.id}</code>\n"
        f"🌐 <b>Username:</b> "
        f"@{esc(user.username) if user.username else 'None'}"
    )

async def log_group_add(
    message,
) -> None:
    user = message.from_user

    bot_name = (
        await get_bot_name()
    )

    await send_log(
        f"💬 <b>{bot_name} joined a new group</b>\n\n"
        f"🏠 <b>Group:</b> "
        f"{esc(message.chat.title)}\n"
        f"🆔 <b>Chat ID:</b> "
        f"<code>{message.chat.id}</code>\n"
        f"👤 <b>Added by:</b> "
        f"{user_link(user)}"
    )


async def log_play(
    message,
    track,
    state: str,
    position: int = 0,
) -> None:
    is_playing = (
        state == "playing"
    )

    status = (
        "Now Playing"
        if is_playing
        else "Added to Queue"
    )

    icon = (
        "🎧"
        if is_playing
        else "📥"
    )

    title = esc(
        track.title
        or "Unknown Song"
    )

    if len(title) > 55:
        title = (
            title[:52].rstrip()
            + "..."
        )

    text = (
        f"{icon} <b>{status}</b>\n"

        "<blockquote>"
        f"<b>{title}</b>"
        "</blockquote>\n\n"

        f"👤 {user_link(message.from_user)}\n"

        f"💬 "
        f"{esc(message.chat.title or 'Unknown Group')}"
    )

    if (
        not is_playing
        and position > 0
    ):
        text += (
            "\n\n"
            f"📌 Queue position "
            f"<b>#{position}</b>"
        )

    await send_log(
        text
    )