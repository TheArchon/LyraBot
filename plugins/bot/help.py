from pyrogram import filters

from Shizu.core.bot import bot
from Shizu.config import settings
from Shizu.utils.premium import premium_emoji
from Shizu.utils.inline.start import (
    commands_page,
)


COMMAND_HOME = (
    f"{premium_emoji(settings.emoji_help, '🕸️')} <b>Help & Commands</b>\n\n"
    "Your music, your way — everything is just a tap away. Pick a category below to explore commands & controls.\n\n"
    "<i>Tip: You can control playback directly from the music player too.</i>"
)


@bot.on_message(
    filters.command("help")
)
async def help_command(
    _,
    message,
):
    await message.reply_text(
        COMMAND_HOME,
        reply_markup=commands_page(),
    )