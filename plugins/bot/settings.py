from pyrogram import filters

from Shizu.core.bot import bot
from Shizu.config import settings as app_settings
from Shizu.utils.premium import premium_emoji


@bot.on_message(filters.command("settings") & filters.group)
async def settings_command(_, message):
    await message.reply_text(
        f"{premium_emoji(app_settings.emoji_text_settings, '⚙️')} <b>Settings</b>\n\n"
        "• Queue limit is configured globally.\n"
        "• Personal playlists and favourites are private to each user.\n"
        "• Playback controls are available from the player card."
    )
