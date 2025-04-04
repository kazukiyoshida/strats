import asyncio
import logging
import queue
import threading

logger = logging.getLogger(__name__)


class State:
    def set_queues(self):
        """
        set_queues initializes both synchronous and asynchronous queues.

        To avoid attaching them to the default event loop,
        this function must be called after the FastAPI server has started.
        """
        if not hasattr(self, "_initialized"):
            self.sync_queue = queue.Queue()
            self.queue = asyncio.Queue()
            self._initialized = True

    def run(self, stop_event: threading.Event):
        loop = asyncio.get_running_loop()
        threading.Thread(
            target=self._sync_to_async_queue,
            args=(loop, stop_event),
        ).start()

    def _sync_to_async_queue(
        self,
        loop: asyncio.AbstractEventLoop,
        stop_event: threading.Event,
    ):
        logger.info("start sync_to_async_queue thread")

        while not stop_event.is_set():
            try:
                item = self.sync_queue.get(timeout=1)
            except self.queue.Empty:
                continue

            if item is None:
                break  # the stop signal

            # When scheduling callbacks from another thread,
            # `call_soon_threadsafe` must be used, since `call_soon` is not thread-safe.
            # cf. https://docs.python.org/ja/3.13/library/asyncio-eventloop.html#asyncio.loop.call_soon_threadsafe
            loop.call_soon_threadsafe(self.queue.put_nowait, item)

        logger.info("sync_to_async_queue thread exiting gracefully")
