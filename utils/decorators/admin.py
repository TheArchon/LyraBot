from functools import wraps

from pyrogram.enums import ChatMemberStatus


def admin_required(func):
    @wraps(func)
    async def wrapped(client, message, *args, **kwargs):
        if not message.from_user:
            return

        member = await client.get_chat_member(
            message.chat.id,
            message.from_user.id,
        )

        if member.status not in {
            ChatMemberStatus.OWNER,
            ChatMemberStatus.ADMINISTRATOR,
        }:
            return await message.reply_text(
                "You need to be a group admin to use this control."
            )

        return await func(client, message, *args, **kwargs)

    return wrapped
