import asyncio
import importlib
import logging

from pyrogram import idle
from pyrogram.types import BotCommand

from Shizu.logging import setup_logging
from Shizu.core.bot import bot
from Shizu.core.userbot import assistant
from Shizu.core.call import calls
from Shizu.core.mongo import ensure_indexes
from Shizu.plugins import ALL_MODULES


COMMANDS = [
    BotCommand(
        "start",
        "Start the bot",
    ),
    BotCommand(
        "play",
        "Play a song",
    ),
    BotCommand(
        "queue",
        "Show music queue",
    ),
    BotCommand(
        "pause",
        "Pause music",
    ),
    BotCommand(
        "resume",
        "Resume music",
    ),
    BotCommand(
        "skip",
        "Skip current song",
    ),
    BotCommand(
        "shuffle",
        "Shuffle queue",
    ),
    BotCommand(
        "stop",
        "Stop music",
    ),
    BotCommand(
        "help",
        "Show commands",
    ),
]


def load_plugins():
    logger = logging.getLogger("Shizu.plugins")

    for module in ALL_MODULES:
        module_path = (
            "Shizu.plugins"
            + module.replace("/", ".")
        )

        importlib.import_module(module_path)

        logger.info(
            "Loaded %s",
            module_path,
        )


async def start_shizu():
    logger = logging.getLogger("Shizu")

    logger.info("Starting Shizu...")

    await ensure_indexes()

    # Start main Telegram bot
    await bot.start()

    me = await bot.get_me()

    logger.info(
        "Bot connected as @%s",
        me.username,
    )

    # Load handlers
    load_plugins()

    logger.info(
        "Shizu handlers loaded."
    )

    # Telegram command menu
    try:
        await bot.set_bot_commands(COMMANDS)
    except Exception as exc:
        logger.warning(
            "Command setup failed: %s",
            exc,
        )

    # Start assistant
    await assistant.start()

    assistant_me = await assistant.get_me()

    logger.info(
        "Assistant connected as %s",
        assistant_me.first_name,
    )

    # Start voice engine
    await calls.start()

    logger.info(
        "Shizu music engine ready."
    )

    # Logger group startup message
    try:
        from Shizu.utils.logger import log_startup

        await log_startup(me)

    except Exception as exc:
        logger.warning(
            "Startup logger failed: %s",
            exc,
        )

    logger.info(
        "Shizu is fully online."
    )

    await idle()


def main():
    setup_logging()

    # IMPORTANT:
    # DO NOT use asyncio.run() here.
    #
    # Pyrofork clients were already created using
    # the current/default event loop.
    #
    # We therefore run Shizu on that SAME loop.
    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(
            start_shizu()
        )

    except KeyboardInterrupt:
        pass

    finally:
        async def shutdown():
            try:
                await calls.stop()
            except Exception:
                pass

            try:
                await assistant.stop()
            except Exception:
                pass

            try:
                await bot.stop()
            except Exception:
                pass

        try:
            loop.run_until_complete(
                shutdown()
            )
        except Exception:
            pass


if __name__ == "__main__":
    main()