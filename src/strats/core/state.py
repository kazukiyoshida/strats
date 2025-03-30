import asyncio
import queue


class State:
    _sync_queue: queue.Queue = queue.Queue()
    queue: asyncio.Queue = asyncio.Queue()
