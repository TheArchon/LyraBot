"""Telegram Premium/custom emoji helpers for message text.

If an ID is configured, Telegram receives a real custom-emoji entity through
HTML ``<tg-emoji>`` markup. If it is not configured, the normal Unicode emoji
is kept as a safe fallback.
"""

from __future__ import annotations

import html


def premium_emoji(emoji_id: str | None, fallback: str) -> str:
    emoji_id = (emoji_id or "").strip()
    fallback = fallback or ""
    if not emoji_id:
        return fallback
    return (
        f'<tg-emoji emoji-id="{html.escape(emoji_id, quote=True)}">'
        f'{html.escape(fallback)}</tg-emoji>'
    )
