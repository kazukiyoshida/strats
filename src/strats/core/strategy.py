import asyncio
from abc import ABC, abstractmethod
from typing import Optional

from .state import State


class Strategy(ABC):
    @abstractmethod
    async def run(
        self,
        state: Optional[State],
        stop_event: asyncio.Event,
    ):
        pass
