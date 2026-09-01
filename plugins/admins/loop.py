from pyrogram import filters

from Shizu.core.bot import bot

from Shizu.utils.decorators.admin import (
    admin_required,
)

from Shizu.utils.stream.player import (
    player,
)

from Shizu.utils.stream.queue import (
    queue,
)


@bot.on_message(
    filters.command("loop")
    & filters.group
)
@admin_required
async def loop_command(
    _,
    message,
):
    chat_id = (
        message.chat.id
    )

    parts = message.text.split(
        maxsplit=1
    )


    # /loop
    # Shows current status.
    if len(parts) == 1:

        enabled = (
            player.is_loop_enabled(
                chat_id
            )
        )

        status = (
            "ON"
            if enabled
            else "OFF"
        )

        return await message.reply_text(
            "🔁 <b>Loop</b>\n\n"

            f"Current status: "
            f"<b>{status}</b>\n\n"

            "<code>/loop on</code>\n"
            "<code>/loop off</code>"
        )


    action = (
        parts[1]
        .strip()
        .lower()
    )


    if action not in {
        "on",
        "off",
    }:

        return await message.reply_text(
            "🔁 <b>Loop</b>\n\n"

            "<blockquote>"
            "Choose whether the current "
            "song should repeat."
            "</blockquote>\n\n"

            "<code>/loop on</code>\n"
            "<code>/loop off</code>"
        )


    # ─────────────────────────────
    # LOOP ON
    # ─────────────────────────────

    if action == "on":

        if not queue.current(
            chat_id
        ):

            return await message.reply_text(
                "🎧 <b>Nothing is playing.</b>\n\n"

                "<blockquote>"
                "Start a song before "
                "turning loop on."
                "</blockquote>"
            )

        if player.is_loop_enabled(
            chat_id
        ):

            return await message.reply_text(
                "🔁 <b>Loop is already ON.</b>"
            )

        player.enable_loop(
            chat_id
        )

        return await message.reply_text(
            "🔁 <b>Loop ON</b>\n\n"

            "<blockquote>"
            "The current song will repeat "
            "automatically when it ends."
            "</blockquote>"
        )


    # ─────────────────────────────
    # LOOP OFF
    # ─────────────────────────────

    if not player.is_loop_enabled(
        chat_id
    ):

        return await message.reply_text(
            "🔁 <b>Loop is already OFF.</b>"
        )

    player.disable_loop(
        chat_id
    )

    await message.reply_text(
        "🔁 <b>Loop OFF</b>\n\n"

        "<blockquote>"
        "Songs will continue through "
        "the queue normally."
        "</blockquote>"
    )