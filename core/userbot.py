from pyrogram import Client
from Shizu.config import settings

assistant = Client(
    "ShizuAssistant",
    api_id=settings.api_id,
    api_hash=settings.api_hash,
    session_string=settings.string_session,
    in_memory=True,
)
