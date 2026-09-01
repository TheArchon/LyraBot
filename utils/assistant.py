import logging

from pyrogram.errors import UserAlreadyParticipant

from Shizu.core.bot import bot
from Shizu.core.userbot import assistant

logger = logging.getLogger(__name__)


async def ensure_assistant(chat_id: int) -> None:
    try:
        me = await assistant.get_me()
        await bot.get_chat_member(chat_id, me.id)
        return
    except Exception:
        pass

    try:
        invite = await bot.create_chat_invite_link(
            chat_id,
            name="My Assistant",
            creates_join_request=False,
        )

        try:
            await assistant.join_chat(invite.invite_link)
        except UserAlreadyParticipant:
            return

    except Exception as exc:
        logger.warning(
            "assistant could not auto-join chat %s: %s",
            chat_id,
            exc,
        )
        raise RuntimeError(
            "I couldn't add the assistant to this group. "
            "Please make me admin with invite permissions and try again."
        ) from exc
