import asyncio
import json
from typing import Set

class SpectralBroadcaster:
    _subscribers: Set[asyncio.Queue] = set()

    @classmethod
    def subscribe(cls) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue()
        cls._subscribers.add(q)
        return q

    @classmethod
    def unsubscribe(cls, q: asyncio.Queue):
        cls._subscribers.discard(q)

    @classmethod
    def broadcast_sync(cls, event_data: dict):
        """Pushes data into async queues from synchronous SQLAlchemy execution paths."""
        for q in list(cls._subscribers):
            try:
                q.put_nowait(event_data)
            except Exception:
                cls._subscribers.discard(q)
