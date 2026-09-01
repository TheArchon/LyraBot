from pyrogram import filters

from Shizu.core.bot import bot
from Shizu.utils.logger import log_group_add


@bot.on_message(filters.new_chat_members)
async def group_add_event(client, message):
    me = await client.get_me()

    for member in message.new_chat_members or []:
        if member.id == me.id:
            await log_group_add(message)
            break
