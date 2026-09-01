from pyrogram import filters
from pyrogram.errors import MessageNotModified

from Shizu.core.bot import bot
from Shizu.config import settings
from Shizu.utils.premium import premium_emoji
from Shizu.platforms.youtube import youtube

from Shizu.utils.inline.player import (
    queued_caption,
    queued_keyboard,
)

from Shizu.utils.logger import (
    log_play,
)

from Shizu.utils.stream.player import (
    player,
)


def requester(message):
    user = message.from_user

    if not user:
        return 0, "Anonymous"

    return (
        user.id,
        user.first_name
        or user.username
        or "User",
    )


async def safe_edit(
    message,
    text: str,
    **kwargs,
):
    """
    Telegram throws MESSAGE_NOT_MODIFIED when
    the new content is identical to the old one.

    That is harmless, so i ignore it.
    """

    try:
        return await message.edit_text(
            text,
            **kwargs,
        )

    except MessageNotModified:
        return message

    except Exception as exc:
        if (
            "MESSAGE_NOT_MODIFIED"
            in str(exc).upper()
        ):
            return message

        raise


@bot.on_message(
    filters.command("play")
    & filters.group
)
async def play_command(
    _,
    message,
):
    parts = message.text.split(
        maxsplit=1
    )

    if len(parts) < 2:
        return await message.reply_text(
            f"{premium_emoji(settings.emoji_text_play, '♫')} <b>Play Something</b>\n\n"
            "<blockquote>"
            "Send a song name or "
            "YouTube link."
            "</blockquote>\n\n"
            "<code>/play song name</code>"
        )

    status = await message.reply_text(
        premium_emoji(settings.emoji_text_play, "🦋")
    )

    user_id, name = requester(
        message
    )

    try:
        # ─────────────────────────────
        # SEARCH
        # ─────────────────────────────

        track = await youtube.resolve(
            parts[1],
            user_id,
            name,
        )

        # ─────────────────────────────
        # DOWNLOAD AUDIO
        # ─────────────────────────────

        audio_file = (
            await youtube.download_audio(
                track
            )
        )

        track.stream_url = (
            audio_file
        )

        # ─────────────────────────────
        # PLAY / QUEUE
        # ─────────────────────────────

        state, position = (
            await player.enqueue_or_play(
                message.chat.id,
                track,
            )
        )

    except OverflowError:
        return await safe_edit(
            status,
            f"{premium_emoji(settings.emoji_text_queue_full, '🐳')} <b>Queue is full.</b>\n\n"
            "<i>Skip or stop a song "
            "before adding more.</i>",
        )

    except Exception as exc:
        return await safe_edit(
            status,
            f"{premium_emoji(settings.emoji_text_error, '⚠')} <b>Couldn't play this song.</b>\n\n"
            "<blockquote>"
            f"{str(exc)[:250]}"
            "</blockquote>",
        )

    # ─────────────────────────────
    # LOGGER
    # ─────────────────────────────

    try:
        await log_play(
            message,
            track,
            state,
            position,
        )

    except Exception:
        # Logger should never break playback.
        pass

    # ─────────────────────────────
    # QUEUED SONG
    # ─────────────────────────────

    if state == "queued":
        try:
            return await status.edit_text(
                queued_caption(
                    track,
                    position,
                ),
                reply_markup=(
                    queued_keyboard()
                ),
                disable_web_page_preview=True,
            )

        except MessageNotModified:
            return

        except Exception as exc:
            if (
                "MESSAGE_NOT_MODIFIED"
                in str(exc).upper()
            ):
                return

            raise

    # ─────────────────────────────
    # CURRENT SONG PLAYER
    # ─────────────────────────────

    try:
        await status.delete()
    except Exception:
        pass

    await player.send_player_card(
        message.chat.id,
        track,
    )