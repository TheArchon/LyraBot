"""Helpers for Telegram Bot API 9.4 styled inline buttons.

The helper keeps the project compatible with older PyroFork builds, while
using ``style`` and ``icon_custom_emoji_id`` automatically when the installed
PyroFork build exposes those Bot API fields.
"""

from __future__ import annotations

import inspect
from functools import lru_cache
from typing import Any

from pyrogram.types import InlineKeyboardButton


@lru_cache(maxsize=1)
def _supports_button_field(field: str) -> bool:
    """Return whether this PyroFork build accepts a button field."""
    try:
        parameters = inspect.signature(
            InlineKeyboardButton.__init__
        ).parameters
    except (TypeError, ValueError):
        # Prefer trying the modern API if introspection is unavailable.
        return True

    return (
        field in parameters
        or any(
            parameter.kind
            is inspect.Parameter.VAR_KEYWORD
            for parameter in parameters.values()
        )
    )


def styled_button(
    text: str,
    *,
    style: str | None = None,
    icon_custom_emoji_id: str | None = None,
    **button_type: Any,
) -> InlineKeyboardButton:
    """Create an inline button with optional Bot API 9.4 styling.

    ``style`` is one of ``primary``, ``success`` or ``danger``.  The custom
    emoji identifier is sent as ``icon_custom_emoji_id`` when supported by the
    installed PyroFork version.  Old versions fall back to a normal button so
    the bot remains runnable instead of crashing.
    """
    kwargs: dict[str, Any] = dict(button_type)

    if style and _supports_button_field("style"):
        kwargs["style"] = style

    if (
        icon_custom_emoji_id
        and _supports_button_field("icon_custom_emoji_id")
    ):
        kwargs["icon_custom_emoji_id"] = (
            icon_custom_emoji_id
        )

    try:
        return InlineKeyboardButton(
            text,
            **kwargs,
        )
    except TypeError:
        # A safety fallback for an older library which does not yet expose
        # the two new Bot API fields.
        kwargs.pop("style", None)
        kwargs.pop("icon_custom_emoji_id", None)
        return InlineKeyboardButton(
            text,
            **kwargs,
        )
