from pyrogram import Client
from Shizu.config import settings

bot = Client(
    "ShizuBot",
    api_id=settings.api_id,
    api_hash=settings.api_hash,
    bot_token=settings.bot_token,
    in_memory=True,
)
