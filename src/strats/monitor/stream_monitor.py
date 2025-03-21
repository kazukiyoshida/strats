import logging
from queue import Queue
from threading import Event

from strats.exchange import StreamClient

from .monitor import Monitor

logger = logging.getLogger(__name__)


class StreamMonitor(Monitor):
    def __init__(self, state, client: StreamClient, handler):
        self.state = state
        self.client = client
        self.handler = handler

    def run(self, name: str, stop_event: Event):
        logger.info(f"start {name}")

        queue: Queue = Queue()
        self.client.start(queue)

        while not stop_event.is_set():
            msg = queue.get()
            self.handler(self.state, msg)

        logger.info(f"stop {name}")
        self.client.stop()
