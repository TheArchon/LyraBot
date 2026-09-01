from pyrogram import filters

from Shizu.core.bot import bot
from Shizu.utils.decorators.admin import admin_required
from Shizu.utils.stream.player import player
from Shizu.utils.stream.queue import queue


@bot.on_message(filters.command("pause") & filters.group)
@admin_required
async def pause_command(_, message):
    try:
        await player.pause(message.chat.id)
        await message.reply_text("⏸ <b>Paused.</b>")
    except Exception:
        await message.reply_text("Nothing is playing.")


@bot.on_message(filters.command("resume") & filters.group)
@admin_required
async def resume_command(_, message):
    try:
        await player.resume(message.chat.id)
        await message.reply_text("▶️ <b>Resumed.</b>")
    except Exception:
        await message.reply_text("Nothing is paused.")


@bot.on_message(filters.command("skip") & filters.group)
@admin_required
async def skip_command(_, message):
    try:
        track = await player.skip(message.chat.id)
    except Exception as exc:
        return await message.reply_text(
            f"Couldn't skip: <code>{str(exc)[:140]}</code>"
        )

    if track:
        await message.reply_text(
            f"⏭ <b>Skipped</b>\n\n"
            f"Now playing: <b>{track.title}</b>"
        )
    else:
        await message.reply_text(
            "🦭 Queue finished. Assistent left the voice chat."
        )


@bot.on_message(filters.command("shuffle") & filters.group)
@admin_required
async def shuffle_command(_, message):
    total = queue.shuffle(message.chat.id)

    if total < 2:
        return await message.reply_text(
            "Not enough queued songs to shuffle."
        )

    await message.reply_text(
        f"🔀 Shuffled <b>{total}</b> queued songs."
    )


@bot.on_message(filters.command("stop") & filters.group)
@admin_required
async def stop_command(_, message):
    await player.stop(message.chat.id)
    await message.reply_text(
        "⏹ <b>Stopped.</b>\nQueue cleared."
    )
