import asyncio
import logging
import time

from datetime import (
    datetime,
    timezone,
)

from pytgcalls import (
    filters as call_filters,
)

from pytgcalls.types import (
    MediaStream,
    StreamEnded,
)

from Shizu.core.bot import bot
from Shizu.core.call import calls
from Shizu.core.mongo import db

from Shizu.utils.assistant import (
    ensure_assistant,
)

from Shizu.utils.inline.player import (
    now_playing_caption,
    player_keyboard,
)

from Shizu.utils.stream.queue import (
    queue,
)


logger = logging.getLogger(
    __name__
)


class Player:
    def __init__(
        self,
    ) -> None:

        self._started_at = {}
        self._pause_started = {}
        self._paused_total = {}
        self._paused = set()

        self._cards = {}
        self._progress_tasks = {}
        self._end_tasks = {}

        # Loop is stored separately for every group.
        self._loop_chats: set[int] = set()


    # ─────────────────────────────
    # LOOP
    # ─────────────────────────────

    def is_loop_enabled(
        self,
        chat_id: int,
    ) -> bool:
        return (
            chat_id
            in self._loop_chats
        )


    def enable_loop(
        self,
        chat_id: int,
    ) -> None:
        self._loop_chats.add(
            chat_id
        )


    def disable_loop(
        self,
        chat_id: int,
    ) -> None:
        self._loop_chats.discard(
            chat_id
        )


    # ─────────────────────────────
    # TIME / PROGRESS
    # ─────────────────────────────

    def reset_clock(
        self,
        chat_id: int,
    ) -> None:

        self._started_at[
            chat_id
        ] = time.monotonic()

        self._paused_total[
            chat_id
        ] = 0.0

        self._pause_started.pop(
            chat_id,
            None,
        )

        self._paused.discard(
            chat_id
        )


    def elapsed(
        self,
        chat_id: int,
    ) -> int:

        started = (
            self._started_at.get(
                chat_id
            )
        )

        if started is None:
            return 0

        now = time.monotonic()

        if chat_id in self._paused:
            now = (
                self._pause_started.get(
                    chat_id,
                    now,
                )
            )

        paused_total = (
            self._paused_total.get(
                chat_id,
                0.0,
            )
        )

        value = (
            now
            - started
            - paused_total
        )

        return max(
            0,
            int(value),
        )


    def is_paused(
        self,
        chat_id: int,
    ) -> bool:

        return (
            chat_id
            in self._paused
        )


    # ─────────────────────────────
    # PLAYER CARD
    # ─────────────────────────────

    async def register_player_card(
        self,
        chat_id: int,
        message_id: int,
    ) -> None:

        self._cards[
            chat_id
        ] = message_id

        old_task = (
            self._progress_tasks.get(
                chat_id
            )
        )

        if (
            old_task
            and not old_task.done()
        ):
            old_task.cancel()

        self._progress_tasks[
            chat_id
        ] = asyncio.create_task(
            self._progress_loop(
                chat_id
            )
        )


    async def _progress_loop(
        self,
        chat_id: int,
    ) -> None:

        try:
            while True:

                await asyncio.sleep(
                    4
                )

                track = queue.current(
                    chat_id
                )

                if not track:
                    return

                message_id = (
                    self._cards.get(
                        chat_id
                    )
                )

                if not message_id:
                    return

                elapsed = self.elapsed(
                    chat_id
                )

                if track.duration:
                    elapsed = min(
                        elapsed,
                        track.duration,
                    )

                try:
                    await bot.edit_message_reply_markup(
                        chat_id=chat_id,
                        message_id=message_id,

                        reply_markup=(
                            player_keyboard(
                                track.id,
                                track.duration,
                                elapsed,
                                self.is_paused(
                                    chat_id
                                ),
                            )
                        ),
                    )

                except Exception as exc:

                    if (
                        "MESSAGE_NOT_MODIFIED"
                        not in str(
                            exc
                        ).upper()
                    ):
                        logger.debug(
                            "Progress update failed: %s",
                            exc,
                        )

        except asyncio.CancelledError:
            return


    async def send_player_card(
        self,
        chat_id: int,
        track,
    ):

        caption = (
            now_playing_caption(
                track
            )
        )

        keyboard = (
            player_keyboard(
                track.id,
                track.duration,
                0,
                False,
            )
        )

        sent = None

        if track.thumbnail:

            try:
                sent = await bot.send_photo(
                    chat_id=chat_id,
                    photo=track.thumbnail,
                    caption=caption,
                    reply_markup=keyboard,
                )

            except Exception as exc:

                logger.debug(
                    "Thumbnail card failed: %s",
                    exc,
                )

        if not sent:

            sent = await bot.send_message(
                chat_id=chat_id,
                text=caption,
                reply_markup=keyboard,
            )

        await self.register_player_card(
            chat_id,
            sent.id,
        )

        return sent


    # ─────────────────────────────
    # END WATCHDOG
    # ─────────────────────────────

    async def _cancel_end_task(
        self,
        chat_id: int,
    ) -> None:

        task = (
            self._end_tasks.pop(
                chat_id,
                None,
            )
        )

        current = (
            asyncio.current_task()
        )

        if (
            task
            and task is not current
            and not task.done()
        ):
            task.cancel()


    async def _start_end_watchdog(
        self,
        chat_id: int,
        track,
    ) -> None:

        await self._cancel_end_task(
            chat_id
        )

        if not track.duration:
            return

        self._end_tasks[
            chat_id
        ] = asyncio.create_task(
            self._end_watchdog(
                chat_id,
                track.id,
                track.duration,
            )
        )


    async def _end_watchdog(
        self,
        chat_id: int,
        track_id: str,
        duration: int,
    ) -> None:

        try:

            while True:

                current = queue.current(
                    chat_id
                )

                if (
                    not current
                    or current.id != track_id
                ):
                    return

                if self.is_paused(
                    chat_id
                ):

                    await asyncio.sleep(
                        2
                    )

                    continue

                elapsed = self.elapsed(
                    chat_id
                )

                remaining = (
                    duration
                    - elapsed
                )

                if remaining <= 1:
                    break

                await asyncio.sleep(
                    min(
                        max(
                            remaining,
                            1,
                        ),
                        5,
                    )
                )

            # Natural end.
            # Loop IS respected here.
            await self.finish_track(
                chat_id,
                track_id,
                respect_loop=True,
            )

        except asyncio.CancelledError:
            return

        except Exception:

            logger.exception(
                "End watchdog failed."
            )


    # ─────────────────────────────
    # PLAYBACK
    # ─────────────────────────────

    async def enqueue_or_play(
        self,
        chat_id: int,
        track,
    ):

        async with queue.lock(
            chat_id
        ):

            if queue.current(
                chat_id
            ):

                position = queue.add(
                    chat_id,
                    track,
                )

                return (
                    "queued",
                    position,
                )

            await ensure_assistant(
                chat_id
            )

            await self._play_locked(
                chat_id,
                track,
            )

            return (
                "playing",
                0,
            )


    async def _play_locked(
        self,
        chat_id: int,
        track,
    ) -> None:

        stream = MediaStream(
            track.stream_url,

            video_flags=(
                MediaStream
                .Flags
                .IGNORE
            ),
        )

        await asyncio.wait_for(
            calls.play(
                chat_id,
                stream,
            ),
            timeout=35,
        )

        queue.set_current(
            chat_id,
            track,
        )

        self.reset_clock(
            chat_id
        )

        await self._start_end_watchdog(
            chat_id,
            track,
        )

        try:

            await db.history.insert_one(
                {
                    "chat_id": chat_id,

                    "track": (
                        track.to_dict()
                    ),

                    "played_at": (
                        datetime.now(
                            timezone.utc
                        )
                    ),
                }
            )

        except Exception as exc:

            logger.warning(
                "History save failed: %s",
                exc,
            )


    # ─────────────────────────────
    # RESTART CURRENT SONG
    # ─────────────────────────────

    async def _restart_current_locked(
        self,
        chat_id: int,
        track,
    ) -> None:

        stream = MediaStream(
            track.stream_url,

            video_flags=(
                MediaStream
                .Flags
                .IGNORE
            ),
        )

        await asyncio.wait_for(
            calls.play(
                chat_id,
                stream,
            ),
            timeout=35,
        )

        queue.set_current(
            chat_id,
            track,
        )

        self.reset_clock(
            chat_id
        )

        await self._start_end_watchdog(
            chat_id,
            track,
        )


    # ─────────────────────────────
    # TRACK END
    # ─────────────────────────────

    async def finish_track(
        self,
        chat_id: int,
        expected_track_id: str,
        respect_loop: bool = True,
    ):

        next_track = None

        looped_track = None

        async with queue.lock(
            chat_id
        ):

            current = queue.current(
                chat_id
            )

            if not current:
                return None

            # Another task/event already
            # switched this song.
            if (
                current.id
                != expected_track_id
            ):
                return current


            # ─────────────────────────
            # LOOP
            # ─────────────────────────

            if (
                respect_loop
                and self.is_loop_enabled(
                    chat_id
                )
            ):

                await self._restart_current_locked(
                    chat_id,
                    current,
                )

                looped_track = current


            # ─────────────────────────
            # NORMAL NEXT SONG
            # ─────────────────────────

            else:

                next_track = queue.next(
                    chat_id
                )

                if next_track:

                    await self._play_locked(
                        chat_id,
                        next_track,
                    )


                # ─────────────────────
                # QUEUE FINISHED
                # ─────────────────────

                else:

                    queue.set_current(
                        chat_id,
                        None,
                    )

                    await self._cancel_end_task(
                        chat_id
                    )

                    await self._cancel_progress(
                        chat_id
                    )

                    self._clear_clock(
                        chat_id
                    )

                    # No song playing anymore,
                    # so reset loop too.
                    self.disable_loop(
                        chat_id
                    )

                    try:

                        await asyncio.wait_for(
                            calls.leave_call(
                                chat_id
                            ),
                            timeout=15,
                        )

                        logger.info(
                            "Queue ended — assistant "
                            "left VC in %s",
                            chat_id,
                        )

                    except Exception as exc:

                        logger.warning(
                            "Could not leave VC %s: %s",
                            chat_id,
                            exc,
                        )

                    return None


        # Loop does NOT send a new player card.
        # Existing card's progress simply
        # starts from 0 again.
        if looped_track:

            return looped_track


        # Automatic next song gets same
        # normal player UI.
        if next_track:

            await self.send_player_card(
                chat_id,
                next_track,
            )

        return next_track


    # ─────────────────────────────
    # AUTO NEXT
    # ─────────────────────────────

    async def play_next(
        self,
        chat_id: int,
    ):

        current = queue.current(
            chat_id
        )

        if not current:
            return None

        return await self.finish_track(
            chat_id,
            current.id,

            # Natural next respects loop.
            respect_loop=True,
        )


    # ─────────────────────────────
    # MANUAL REPLAY
    # ─────────────────────────────

    async def replay(
        self,
        chat_id: int,
    ) -> None:

        async with queue.lock(
            chat_id
        ):

            track = queue.current(
                chat_id
            )

            if not track:

                raise RuntimeError(
                    "Nothing is playing."
                )

            await self._restart_current_locked(
                chat_id,
                track,
            )


    # ─────────────────────────────
    # PAUSE
    # ─────────────────────────────

    async def pause(
        self,
        chat_id: int,
    ) -> None:

        if not queue.current(
            chat_id
        ):

            raise RuntimeError(
                "Nothing is playing."
            )

        if chat_id in self._paused:
            return

        await calls.pause(
            chat_id
        )

        self._pause_started[
            chat_id
        ] = time.monotonic()

        self._paused.add(
            chat_id
        )


    # ─────────────────────────────
    # RESUME
    # ─────────────────────────────

    async def resume(
        self,
        chat_id: int,
    ) -> None:

        if not queue.current(
            chat_id
        ):

            raise RuntimeError(
                "Nothing is playing."
            )

        if (
            chat_id
            not in self._paused
        ):
            return

        await calls.resume(
            chat_id
        )

        paused_at = (
            self._pause_started.pop(
                chat_id,
                None,
            )
        )

        if paused_at is not None:

            self._paused_total[
                chat_id
            ] = (
                self._paused_total.get(
                    chat_id,
                    0.0,
                )
                + (
                    time.monotonic()
                    - paused_at
                )
            )

        self._paused.discard(
            chat_id
        )


    # ─────────────────────────────
    # MANUAL SKIP
    # ─────────────────────────────

    async def skip(
        self,
        chat_id: int,
    ):

        current = queue.current(
            chat_id
        )

        if not current:
            return None

        # IMPORTANT:
        # Manual skip ignores Loop.
        #
        # Loop ON + /skip
        # still plays next song.
        return await self.finish_track(
            chat_id,
            current.id,
            respect_loop=False,
        )


    # ─────────────────────────────
    # CLEANUP
    # ─────────────────────────────

    async def _cancel_progress(
        self,
        chat_id: int,
    ) -> None:

        task = (
            self._progress_tasks.pop(
                chat_id,
                None,
            )
        )

        if (
            task
            and not task.done()
        ):
            task.cancel()

        self._cards.pop(
            chat_id,
            None,
        )


    def _clear_clock(
        self,
        chat_id: int,
    ) -> None:

        self._started_at.pop(
            chat_id,
            None,
        )

        self._paused_total.pop(
            chat_id,
            None,
        )

        self._pause_started.pop(
            chat_id,
            None,
        )

        self._paused.discard(
            chat_id
        )


    # ─────────────────────────────
    # STOP
    # ─────────────────────────────

    async def stop(
        self,
        chat_id: int,
    ) -> None:

        async with queue.lock(
            chat_id
        ):

            queue.clear(
                chat_id
            )

            # Stop also disables loop.
            self.disable_loop(
                chat_id
            )

            await self._cancel_end_task(
                chat_id
            )

            await self._cancel_progress(
                chat_id
            )

            self._clear_clock(
                chat_id
            )

            try:

                await asyncio.wait_for(
                    calls.leave_call(
                        chat_id
                    ),
                    timeout=15,
                )

            except Exception as exc:

                logger.warning(
                    "Stop leave_call failed: %s",
                    exc,
                )


player = Player()


# ─────────────────────────────
# NATURAL STREAM END
# ─────────────────────────────

@calls.on_update(
    call_filters.stream_end()
)
async def stream_ended(
    _,
    update: StreamEnded,
) -> None:

    chat_id = (
        update.chat_id
    )

    try:

        current = queue.current(
            chat_id
        )

        if not current:

            try:
                await calls.leave_call(
                    chat_id
                )

            except Exception:
                pass

            return


        # Natural song ending:
        # Loop ON → repeat same song.
        # Loop OFF → next / leave VC.
        await player.finish_track(
            chat_id,
            current.id,
            respect_loop=True,
        )

    except Exception:

        logger.exception(
            "Failed to handle "
            "stream end."
        )