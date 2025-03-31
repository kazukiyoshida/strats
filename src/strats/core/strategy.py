import asyncio
from abc import ABC, abstractmethod

from .state import State


class Strategy(ABC):
    @abstractmethod
    async def run(
        self,
        state: State,
        stop_event: asyncio.Event,
    ):
        pass
