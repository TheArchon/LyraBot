from pyrogram.types import InlineKeyboardMarkup

from Shizu.config import settings
from Shizu.utils.inline.button import styled_button


def normalize_url(value: str) -> str:
    if not value:
        return "https://t.me/"
    if value.startswith(("https://", "http://")):
        return value
    return "https://t.me/" + value.lstrip("@")


def bot_username() -> str:
    return settings.bot_username.strip().lstrip("@")


def add_group_url() -> str:
    username = bot_username()
    if not username:
        return "https://t.me/"
    return f"https://t.me/{username}?startgroup=true"


def owner_url() -> str:
    username = settings.owner_username.strip().lstrip("@")
    if username:
        return f"https://t.me/{username}"
    return f"tg://user?id={settings.owner_id}"


def start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                styled_button(
                    "Add To Your Group",
                    url=add_group_url(),
                    style="success",
                    icon_custom_emoji_id=settings.emoji_add_group,
                )
            ],
            [
                styled_button(
                    "Help & Commands",
                    callback_data="shizu:commands",
                    style="primary",
                    icon_custom_emoji_id=settings.emoji_help,
                )
            ],
            [
                styled_button(
                    "Owner",
                    url=owner_url(),
                    icon_custom_emoji_id=settings.emoji_owner,
                ),
                styled_button(
                    "Channel",
                    url=normalize_url(settings.support_channel),
                    icon_custom_emoji_id=settings.emoji_channel,
                ),
            ],
            [
                styled_button(
                    "Support",
                    url=normalize_url(settings.support_group),
                    icon_custom_emoji_id=settings.emoji_support,
                )
            ],
        ]
    )


def commands_page() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                styled_button(
                    "Music",
                    callback_data="cmd:music",
                    style="primary",
                    icon_custom_emoji_id=settings.emoji_music,
                ),
                styled_button(
                    "Controls",
                    callback_data="cmd:controls",
                    style="primary",
                    icon_custom_emoji_id=settings.emoji_controls,
                ),
            ],
            [
                styled_button(
                    "General",
                    callback_data="cmd:general",
                    style="primary",
                    icon_custom_emoji_id=settings.emoji_general,
                ),
            ],
            [
                styled_button(
                    "‹ Back",
                    callback_data="shizu:home",
                    icon_custom_emoji_id=settings.emoji_back,
                ),
            ],
        ]
    )


def command_back() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                styled_button(
                    "‹ Back",
                    callback_data="shizu:commands",
                    icon_custom_emoji_id=settings.emoji_back,
                )
            ]
        ]
    )
