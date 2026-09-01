from pyrogram.types import InlineKeyboardMarkup

from Shizu.config import settings
from Shizu.utils.inline.button import styled_button
from Shizu.utils.premium import premium_emoji


def format_duration(seconds: int) -> str:
    seconds = max(0, int(seconds or 0))
    minutes, sec = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}:{minutes:02}:{sec:02}"
    return f"{minutes}:{sec:02}"


def short_title(title: str) -> str:
    if not title:
        return "Unknown Song"
    separators = [" | ", " - ", " (", " [", " • "]
    cleaned = title.strip()
    for separator in separators:
        if separator in cleaned:
            cleaned = cleaned.split(separator, 1)[0].strip()
    words = cleaned.split()
    if len(words) > 3:
        cleaned = " ".join(words[:3])
    return cleaned[:40]


def progress_text(elapsed: int, duration: int) -> str:
    if not duration:
        return f"{format_duration(elapsed)} ━━●━━━━━ LIVE"
    elapsed = max(0, min(int(elapsed), int(duration)))
    slots = 8
    ratio = elapsed / duration if duration > 0 else 0
    position = int(ratio * (slots - 1))
    bar = ""
    for index in range(slots):
        if index == position:
            bar += "●"
        elif index < position:
            bar += "━"
        else:
            bar += "─"
    return f"{format_duration(elapsed)} {bar} {format_duration(duration)}"


def player_keyboard(track_id: str, duration: int = 0, elapsed: int = 0, paused: bool = False) -> InlineKeyboardMarkup:
    pause_icon = "▷" if paused else "Ⅱ"
    pause_action = "resume" if paused else "pause"
    return InlineKeyboardMarkup(
        [
            [
                styled_button(
                    pause_icon,
                    callback_data=f"player:{pause_action}",
                    style="primary",
                    icon_custom_emoji_id=(settings.emoji_resume if paused else settings.emoji_pause),
                ),
                styled_button(
                    "↻",
                    callback_data="player:replay",
                    style="primary",
                    icon_custom_emoji_id=settings.emoji_replay,
                ),
                styled_button(
                    "▸▸|",
                    callback_data="player:skip",
                    style="success",
                    icon_custom_emoji_id=settings.emoji_skip,
                ),
                styled_button(
                    "□",
                    callback_data="player:stop",
                    style="danger",
                    icon_custom_emoji_id=settings.emoji_stop,
                ),
            ],
            [
                styled_button(
                    progress_text(elapsed, duration),
                    callback_data="player:progress",
                    style="primary",
                )
            ],
            [
                styled_button(
                    "Close",
                    callback_data="player:close",
                    style="danger",
                    icon_custom_emoji_id=settings.emoji_close,
                )
            ],
        ]
    )


def queued_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                styled_button(
                    "Close",
                    callback_data="player:close",
                    style="danger",
                    icon_custom_emoji_id=settings.emoji_close,
                ),
            ],
        ]
    )


def now_playing_caption(track) -> str:
    title = short_title(track.title)
    return (
        f"{premium_emoji(settings.emoji_text_started, '🪽')} <b>Started Streaming:</b>\n\n"
        f"{premium_emoji(settings.emoji_text_title, '🦢')} <b>Title :</b> <a href=\"{track.webpage_url}\">{title}</a>\n"
        f"{premium_emoji(settings.emoji_text_duration, '🕧')} <b>Duration :</b> {format_duration(track.duration)}\n"
        f"{premium_emoji(settings.emoji_text_requested, '⛄')} <b>Requested By :</b> {track.requester_name}"
    )


def queued_caption(track, position: int) -> str:
    title = short_title(track.title)
    return (
        f"{premium_emoji(settings.emoji_text_queue, '＋')} <b>Added To Queue</b>\n\n"
        f"{premium_emoji(settings.emoji_text_title, '🦢')} <b>Title :</b> {title}\n"
        f"{premium_emoji(settings.emoji_text_position, '🥂')} <b>Position :</b> #{position}\n"
        f"{premium_emoji(settings.emoji_text_requested, '🐳')} <b>Requested By :</b> {track.requester_name}\n\n"
        "<blockquote>I will play it automatically.</blockquote>"
    )
