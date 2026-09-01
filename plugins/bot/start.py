import html
import logging
import time

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup

from Shizu.config import settings
from Shizu.utils.premium import premium_emoji
from Shizu.core.bot import bot
from Shizu.utils.inline.start import (
    start_keyboard,
)
from Shizu.utils.inline.button import styled_button
from Shizu.utils.logger import (
    log_user_start,
)


logger = logging.getLogger(__name__)

# Plugin load hone ke time se uptime count hoga
START_TIME = time.time()


def format_uptime() -> str:
    total = int(
        time.time() - START_TIME
    )

    days, total = divmod(
        total,
        86400,
    )

    hours, total = divmod(
        total,
        3600,
    )

    minutes, seconds = divmod(
        total,
        60,
    )

    if days:
        return (
            f"{days}ᴅᴀʏs, "
            f"{hours}ʜ:{minutes:02}ᴍ:"
            f"{seconds:02}s"
        )

    return (
        f"{hours}ʜ:"
        f"{minutes:02}ᴍ:"
        f"{seconds:02}s"
    )


async def get_bot_name() -> str:
    me = await bot.get_me()

    return html.escape(
        me.first_name
        or "Music"
    )


async def home_caption(
    user,
) -> str:
    name = (
        user.first_name
        if user
        else "there"
    )

    name = html.escape(
        name
    )

    bot_name = await get_bot_name()

    return (
        f"{premium_emoji(settings.emoji_text_hey, "🥂")} <b>Hey {name}</b>  ˚₊‧\n\n"

        "<blockquote>"
        "Music feels better when "
        "you don't have to think "
        "about the player."
        "</blockquote>\n\n"

        f"<b>{bot_name}</b> keeps your "
        "group's music simple — "
        "search, play, queue and "
        "save what you love."
    )


async def group_start_caption() -> str:
    bot_name = await get_bot_name()

    return (
        f"「 <b>{bot_name}</b> 」 "
        "is online.\n\n"

        "<blockquote>"
        "Ready to fill this chat "
        "with some music."
        "</blockquote>\n\n"

        f"<b>Uptime :</b> "
        f"<code>{format_uptime()}</code>"
    )


def group_start_keyboard():
    username = (
        settings.bot_username
        .strip()
        .lstrip("@")
    )

    if username:
        add_url = (
            f"https://t.me/{username}"
            "?startgroup=true"
        )
    else:
        add_url = "https://t.me/"

    return InlineKeyboardMarkup(
        [
            [
                styled_button(
                    "Add To Your Group",
                    url=add_url,
                    style="success",
                    icon_custom_emoji_id=settings.emoji_add_group,
                )
            ]
        ]
    )


@bot.on_message(
    filters.command("start")
    & filters.private
)
async def private_start(
    _,
    message,
):
    await log_user_start(
        message
    )

    caption = await home_caption(
        message.from_user
    )

    if settings.start_img_url:
        try:
            return await message.reply_photo(
                photo=settings.start_img_url,
                caption=caption,
                reply_markup=(
                    start_keyboard()
                ),
            )

        except Exception as exc:
            logger.warning(
                "START_IMG_URL failed: %s",
                exc,
            )

    await message.reply_text(
        caption,
        reply_markup=(
            start_keyboard()
        ),
        disable_web_page_preview=True,
    )


@bot.on_message(
    filters.command("start")
    & filters.group
)
async def group_start(
    _,
    message,
):
    caption = (
        await group_start_caption()
    )

    if settings.start_img_url:
        try:
            return await message.reply_photo(
                photo=settings.start_img_url,
                caption=caption,
                reply_markup=(
                    group_start_keyboard()
                ),
            )

        except Exception as exc:
            logger.warning(
                "Group START_IMG_URL "
                "failed: %s",
                exc,
            )

    await message.reply_text(
        caption,
        reply_markup=(
            group_start_keyboard()
        ),
        disable_web_page_preview=True,
    )