import asyncio
from abc import ABC, abstractmethod


class StreamClient(ABC):
    @abstractmethod
    def stream(self, stop_event: asyncio.Event):
        pass
