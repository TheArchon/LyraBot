from pyrogram import filters

from Shizu.core.bot import bot
from Shizu.config import settings
from Shizu.utils.premium import premium_emoji
from Shizu.utils.formatters import duration_text
from Shizu.utils.stream.queue import queue


@bot.on_message(filters.command("queue") & filters.group)
async def queue_command(_, message):
    current = queue.current(message.chat.id)
    pending = queue.pending(message.chat.id)

    if not current and not pending:
        return await message.reply_text(
            f"{premium_emoji(settings.emoji_text_queue, '📄')} Queue is empty."
        )

    lines = [f"{premium_emoji(settings.emoji_text_queue, '📄')} <b>Queue</b>", ""]

    if current:
        lines.append(
            f"{premium_emoji(settings.emoji_text_play, '▶️')} <b>{current.title}</b> · "
            f"{duration_text(current.duration)}"
        )

    if pending:
        lines.append("")

    for index, track in enumerate(pending[:12], 1):
        lines.append(
            f"{index}. {track.title} · "
            f"{duration_text(track.duration)}"
        )

    if len(pending) > 12:
        lines.append(
            f"\n+{len(pending) - 12} more"
        )

    await message.reply_text("\n".join(lines))
