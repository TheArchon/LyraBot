import logging

from pyrogram import filters

from Shizu.core.bot import bot
from Shizu.config import settings
from Shizu.utils.premium import premium_emoji

from Shizu.plugins.bot.help import (
    COMMAND_HOME,
)

from Shizu.plugins.bot.start import (
    home_caption,
)

from Shizu.utils.database.favourites import (
    add_favourite,
)

from Shizu.utils.inline.player import format_duration, now_playing_caption, player_keyboard, short_title
from Shizu.utils.inline.start import (
    command_back,
    commands_page,
    start_keyboard,
)

from Shizu.utils.stream.player import (
    player,
)

from Shizu.utils.stream.queue import (
    queue,
)


logger = logging.getLogger(
    __name__
)


MUSIC_TEXT = (
    f"{premium_emoji(settings.emoji_text_music or settings.emoji_music, '🥂')} <b>Music</b>\n\n"
    "<blockquote>Search it, play it — I'll handle the rest.</blockquote>\n\n"
    "<code>/play song name</code> — Search & play a song.\n"
    "<code>/play YouTube URL</code> — Play directly from a link.\n"
    "<code>/queue</code> — See what's playing next."
)

CONTROLS_TEXT = (
    f"{premium_emoji(settings.emoji_text_controls or settings.emoji_controls, '🦋')} <b>Playback Controls</b>\n\n"
    "<blockquote>Simple controls for your voice chat.</blockquote>\n\n"
    "<code>/pause</code> — Pause the current song.\n"
    "<code>/resume</code> — Continue playback.\n"
    "<code>/skip</code> — Play the next song.\n"
    "<code>/shuffle</code> — Shuffle the queue.\n"
    "<code>/stop</code> — Stop music & leave VC."
)

GENERAL_TEXT = (
    f"{premium_emoji(settings.emoji_text_general or settings.emoji_general, '🕧')} <b>General</b>\n\n"
    "<blockquote>Everything you need to get around.</blockquote>\n\n"
    "<code>/start</code> — Open the main menu.\n"
    "<code>/help</code> — Open the command centre.\n"
    "<code>/settings</code> — View group settings."
)


async def edit_page(
    query,
    text,
    keyboard,
):
    try:
        if query.message.photo:
            await (
                query.message
                .edit_caption(
                    caption=text,
                    reply_markup=keyboard,
                )
            )

        else:
            await (
                query.message
                .edit_text(
                    text=text,
                    reply_markup=keyboard,
                    disable_web_page_preview=True,
                )
            )

    except Exception as exc:
        logger.warning(
            "Page edit failed: %s",
            exc,
        )

    await query.answer()


@bot.on_callback_query(
    filters.regex(
        r"^shizu:"
    )
)
async def shizu_pages(
    _,
    query,
):
    data = query.data.split(
        ":"
    )

    action = data[1]

    if action == "home":
        return await edit_page(
            query,
            await home_caption(
                query.from_user
            ),
            start_keyboard(),
        )

    if action == "commands":
        return await edit_page(
            query,
            COMMAND_HOME,
            commands_page(),
        )


@bot.on_callback_query(
    filters.regex(
        r"^cmd:"
    )
)
async def command_pages(
    _,
    query,
):
    action = query.data.split(
        ":",
        1,
    )[1]

    pages = {
        "music": MUSIC_TEXT,
        "controls": CONTROLS_TEXT,
        "general": GENERAL_TEXT,
    }

    text = pages.get(
        action
    )

    if not text:
        return await query.answer(
            "This section isn't available.",
            show_alert=True,
        )

    await query.answer()

    return await edit_page(
        query,
        text,
        command_back(),
    )

@bot.on_callback_query(
    filters.regex(
        r"^player:"
    )
)
async def player_callbacks(
    _,
    query,
):
    chat_id = (
        query.message.chat.id
    )

    action = query.data.split(
        ":",
        1,
    )[1]

    if action == "pause":
        try:
            await player.pause(
                chat_id
            )

            track = queue.current(
                chat_id
            )

            if track:
                await query.message.edit_reply_markup(
                    reply_markup=(
                        player_keyboard(
                            track.id,
                            track.duration,
                            player.elapsed(
                                chat_id
                            ),
                            True,
                        )
                    )
                )

            return await query.answer(
                "Paused ⏸"
            )

        except Exception:
            return await query.answer(
                "Nothing is playing.",
                show_alert=True,
            )

    if action == "resume":
        try:
            await player.resume(
                chat_id
            )

            track = queue.current(
                chat_id
            )

            if track:
                await query.message.edit_reply_markup(
                    reply_markup=(
                        player_keyboard(
                            track.id,
                            track.duration,
                            player.elapsed(
                                chat_id
                            ),
                            False,
                        )
                    )
                )

            return await query.answer(
                "Playing ▷"
            )

        except Exception:
            return await query.answer(
                "Nothing is paused.",
                show_alert=True,
            )

    if action == "replay":
        try:
            await player.replay(
                chat_id
            )

            track = queue.current(
                chat_id
            )

            if track:
                await query.message.edit_reply_markup(
                    reply_markup=(
                        player_keyboard(
                            track.id,
                            track.duration,
                            0,
                            False,
                        )
                    )
                )

            return await query.answer(
                "Restarted ↻"
            )

        except Exception:
            return await query.answer(
                "Couldn't replay.",
                show_alert=True,
            )

    if action == "skip":
        try:
            next_track = (
                await player.skip(
                    chat_id
                )
            )

            try:
                await query.message.delete()
            except Exception:
                pass

            if not next_track:
                return await query.answer(
                    "Queue finished."
                )

            await player.send_player_card(
                chat_id,
                next_track,
            )

            return await query.answer(
                "Skipped ⏭"
            )

        except Exception:
            return await query.answer(
                "Couldn't skip.",
                show_alert=True,
            )

    if action == "stop":
        try:
            await player.stop(
                chat_id
            )

            try:
                await query.message.edit_caption(
                    caption=(
                        "□ <b>Playback Stopped</b>\n\n"
                        "<blockquote>"
                        "Queue cleared and "
                        "Assistent left the voice chat."
                        "</blockquote>"
                    ),
                    reply_markup=None,
                )

            except Exception:
                try:
                    await query.message.edit_text(
                        "□ <b>Playback Stopped</b>\n\n"
                        "<blockquote>"
                        "Queue cleared and "
                        "Assistent left the voice chat."
                        "</blockquote>",
                        reply_markup=None,
                    )
                except Exception:
                    pass

            return await query.answer(
                "Stopped"
            )

        except Exception:
            return await query.answer(
                "Couldn't stop.",
                show_alert=True,
            )

    if action == "progress":
        track = queue.current(
            chat_id
        )

        if not track:
            return await query.answer(
                "Nothing is playing.",
                show_alert=True,
            )

        elapsed = player.elapsed(
            chat_id
        )

        return await query.answer(
            f"{format_duration(elapsed)} / "
            f"{format_duration(track.duration)}"
        )

    if action == "queue":
        current = queue.current(
            chat_id
        )

        pending = queue.pending(
            chat_id
        )

        lines = []

        if current:
            lines.append(
                "▶ "
                + short_title(
                    current.title
                )
            )

        for index, track in enumerate(
            pending[:7],
            1,
        ):
            lines.append(
                f"{index}. "
                f"{short_title(track.title)}"
            )

        return await query.answer(
            "\n".join(lines)[:190]
            or "Queue is empty.",
            show_alert=True,
        )

    if action == "close":
        try:
            await query.message.delete()
        except Exception:
            pass

        return await query.answer()
    
@bot.on_callback_query(
    filters.regex(
        r"^fav:add:"
    )
)
async def favourite_callback(
    _,
    query,
):
    track = queue.current(
        query.message.chat.id
    )

    if not track:
        return await query.answer(
            "That song is no "
            "longer playing.",
            show_alert=True,
        )

    requested_id = (
        query.data.rsplit(
            ":",
            1,
        )[1]
    )

    if track.id != requested_id:
        return await query.answer(
            "That song is no "
            "longer current.",
            show_alert=True,
        )

    await add_favourite(
        query.from_user.id,
        track,
    )

    await query.answer(
        "Saved ♡"
    )