import asyncio
from abc import ABC, abstractmethod

from .state import State


class Monitor(ABC):
    @abstractmethod
    async def run(self, state: State, stop_event: asyncio.Event):
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass
