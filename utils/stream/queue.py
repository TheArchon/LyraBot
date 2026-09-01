import asyncio
import random
from collections import deque

from Shizu.config import settings
from Shizu.models import Track


class QueueManager:
    def __init__(self) -> None:
        self._queues: dict[int, deque[Track]] = {}
        self._current: dict[int, Track] = {}
        self._locks: dict[int, asyncio.Lock] = {}

    def lock(self, chat_id: int) -> asyncio.Lock:
        return self._locks.setdefault(chat_id, asyncio.Lock())

    def current(self, chat_id: int) -> Track | None:
        return self._current.get(chat_id)

    def set_current(self, chat_id: int, track: Track | None) -> None:
        if track is None:
            self._current.pop(chat_id, None)
        else:
            self._current[chat_id] = track

    def pending(self, chat_id: int) -> list[Track]:
        return list(self._queues.get(chat_id, deque()))

    def add(self, chat_id: int, track: Track) -> int:
        queue = self._queues.setdefault(chat_id, deque())

        if len(queue) >= settings.max_queue_size:
            raise OverflowError("Queue is full.")

        queue.append(track)
        return len(queue)

    def next(self, chat_id: int) -> Track | None:
        queue = self._queues.setdefault(chat_id, deque())
        return queue.popleft() if queue else None

    def shuffle(self, chat_id: int) -> int:
        queue = self._queues.setdefault(chat_id, deque())
        items = list(queue)
        random.shuffle(items)
        self._queues[chat_id] = deque(items)
        return len(items)

    def clear(self, chat_id: int) -> None:
        self._queues.pop(chat_id, None)
        self._current.pop(chat_id, None)


queue = QueueManager()
