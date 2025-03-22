import asyncio
from abc import ABC, abstractmethod


class Monitor(ABC):
    @abstractmethod
    async def run(self, stop_event: asyncio.Event):
        pass
