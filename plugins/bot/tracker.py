import logging

from pyrogram import filters

from Shizu.core.bot import bot
from Shizu.utils.database.stats import (
    save_chat,
    save_user,
)


logger = logging.getLogger(
    __name__
)


# Commands belonging to this bot.
BOT_COMMANDS = {
    "start",
    "help",
    "play",
    "queue",
    "pause",
    "resume",
    "skip",
    "shuffle",
    "stop",
    "settings",
    "stats",
    "broadcast",
    "restart",
}


def is_our_command(
    text: str | None,
    bot_username: str,
) -> bool:
    if not text:
        return False

    first = text.split(
        maxsplit=1
    )[0]

    if not first.startswith("/"):
        return False

    raw = first[1:]

    if "@" in raw:
        command, username = raw.split(
            "@",
            1,
        )

        if (
            username.lower()
            != bot_username.lower()
        ):
            return False

    else:
        command = raw

    command = command.lower()

    return command in BOT_COMMANDS


@bot.on_message(
    filters.all,
    group=-100,
)
async def track_everything(
    client,
    message,
):
    # Store user.
    try:
        await save_user(
            message.from_user
        )

    except Exception as exc:
        logger.debug(
            "User tracking failed: %s",
            exc,
        )

    # Store group.
    try:
        await save_chat(
            message.chat
        )

    except Exception as exc:
        logger.debug(
            "Chat tracking failed: %s",
            exc,
        )

    # Delete bot commands sent inside groups.
    if (
        message.chat
        and message.chat.type.name
        in {
            "GROUP",
            "SUPERGROUP",
        }
    ):
        try:
            me = await client.get_me()

            if is_our_command(
                message.text,
                me.username or "",
            ):
                await message.delete()

        except Exception:
            # Usually means bot doesn't have
            # delete-message permission.
            pass