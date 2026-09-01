import asyncio
import html
import logging
import os
import sys

from pyrogram import filters
from pyrogram.errors import (
    FloodWait,
    UserIsBlocked,
    InputUserDeactivated,
)
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from Shizu.config import settings
from Shizu.utils.inline.button import styled_button
from Shizu.core.bot import bot
from Shizu.utils.premium import premium_emoji

from Shizu.utils.database.stats import (
    get_broadcast_groups,
    get_broadcast_users,
    get_stats,
    mark_chat_inactive,
)


logger = logging.getLogger(
    __name__
)


def owner_only(
    user_id: int | None,
) -> bool:
    return (
        user_id
        == settings.owner_id
    )


# ─────────────────────────────
# STATS
# ─────────────────────────────

@bot.on_message(
    filters.command("stats")
)
async def stats_command(
    _,
    message,
):
    if not owner_only(
        message.from_user.id
        if message.from_user
        else None
    ):
        return

    stats = await get_stats()

    me = await bot.get_me()

    bot_name = html.escape(
        me.first_name
        or "Music Bot"
    )

    await message.reply_text(
        f"{premium_emoji(settings.emoji_text_statistics, '📊')} <b>{bot_name} Statistics</b>\n\n"

        "<blockquote>"
        "A quick look at the people "
        "and groups using the bot."
        "</blockquote>\n\n"

        f"{premium_emoji(settings.emoji_text_users, '👤')} <b>Total Users:</b> "
        f"<code>{stats['users']:,}</code>\n"

        f"{premium_emoji(settings.emoji_text_groups, '💬')} <b>Total Groups:</b> "
        f"<code>{stats['groups']:,}</code>\n"

        f"{premium_emoji(settings.emoji_text_active, '🟢')} <b>Active Groups:</b> "
        f"<code>{stats['active_groups']:,}</code>"
    )


# ─────────────────────────────
# BROADCAST
# ─────────────────────────────

@bot.on_message(
    filters.command("broadcast")
)
async def broadcast_command(
    _,
    message,
):
    if not owner_only(
        message.from_user.id
        if message.from_user
        else None
    ):
        return

    if not message.reply_to_message:
        return await message.reply_text(
            "📨 <b>Broadcast</b>\n\n"
            "<blockquote>"
            "Reply to the exact message "
            "you want me to broadcast."
            "</blockquote>"
        )

    users = await get_broadcast_users()
    groups = await get_broadcast_groups()

    status = await message.reply_text(
        "📨 <b>Broadcast Started</b>\n\n"
        "<blockquote>"
        "Sending your message exactly "
        "as it appears."
        "</blockquote>"
    )

    source = (
        message.reply_to_message
    )

    success_users = 0
    failed_users = 0

    success_groups = 0
    failed_groups = 0

    # ───── USERS ─────

    for item in users:
        chat_id = item.get(
            "user_id"
        )

        if not chat_id:
            continue

        try:
            await source.copy(
                chat_id=chat_id,
                reply_markup=(
                    source.reply_markup
                ),
            )

            success_users += 1

        except FloodWait as exc:
            await asyncio.sleep(
                exc.value
            )

            try:
                await source.copy(
                    chat_id=chat_id,
                    reply_markup=(
                        source.reply_markup
                    ),
                )

                success_users += 1

            except Exception:
                failed_users += 1

        except (
            UserIsBlocked,
            InputUserDeactivated,
        ):
            failed_users += 1

        except Exception:
            failed_users += 1

    # ───── GROUPS ─────

    for item in groups:
        chat_id = item.get(
            "chat_id"
        )

        if not chat_id:
            continue

        try:
            await source.copy(
                chat_id=chat_id,
                reply_markup=(
                    source.reply_markup
                ),
            )

            success_groups += 1

        except FloodWait as exc:
            await asyncio.sleep(
                exc.value
            )

            try:
                await source.copy(
                    chat_id=chat_id,
                    reply_markup=(
                        source.reply_markup
                    ),
                )

                success_groups += 1

            except Exception:
                failed_groups += 1

        except Exception:
            failed_groups += 1

            try:
                await mark_chat_inactive(
                    chat_id
                )
            except Exception:
                pass

    await status.edit_text(
        "✅ <b>Broadcast Complete</b>\n\n"

        f"👤 <b>Users</b>\n"
        f"Sent: <code>{success_users}</code>\n"
        f"Failed: <code>{failed_users}</code>\n\n"

        f"💬 <b>Groups</b>\n"
        f"Sent: <code>{success_groups}</code>\n"
        f"Failed: <code>{failed_groups}</code>"
    )


# ─────────────────────────────
# RESTART
# ─────────────────────────────

def restart_keyboard():
    return InlineKeyboardMarkup(
        [
            [
                styled_button(
                    "Restart",
                    callback_data="owner:restart:yes",
                    style="success",
                    icon_custom_emoji_id=settings.emoji_restart,
                ),
                styled_button(
                    "Cancel",
                    callback_data="owner:restart:no",
                    style="danger",
                    icon_custom_emoji_id=settings.emoji_cancel,
                ),
            ]
        ]
    )


@bot.on_message(
    filters.command("restart")
)
async def restart_command(
    _,
    message,
):
    if not owner_only(
        message.from_user.id
        if message.from_user
        else None
    ):
        return

    await message.reply_text(
        "🔄 <b>Restart Bot?</b>\n\n"
        "<blockquote>"
        "This restarts the running "
        "Python process."
        "</blockquote>",
        reply_markup=(
            restart_keyboard()
        ),
    )


@bot.on_callback_query(
    filters.regex(
        r"^owner:restart:"
    )
)
async def restart_callback(
    _,
    query,
):
    if not owner_only(
        query.from_user.id
    ):
        return await query.answer(
            "Owner only.",
            show_alert=True,
        )

    action = query.data.split(
        ":"
    )[2]

    if action == "no":
        try:
            await query.message.delete()
        except Exception:
            pass

        return await query.answer(
            "Cancelled"
        )

    await query.answer(
        "Restarting..."
    )

    try:
        await query.message.edit_text(
            "🔄 <b>Restarting...</b>\n\n"
            "<blockquote>"
            "I'll be back in a moment."
            "</blockquote>",
            reply_markup=None,
        )

    except Exception:
        pass

    await asyncio.sleep(
        1
    )

    # Replace the current process with
    # a fresh Python process.
    os.execv(
        sys.executable,
        [
            sys.executable,
            "-m",
            "Shizu",
        ],
    )