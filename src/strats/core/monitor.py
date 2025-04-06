import asyncio
from abc import ABC, abstractmethod
from typing import Optional

from .state import State


class Monitor(ABC):
    @abstractmethod
    async def run(self, state: Optional[State], stop_event: asyncio.Event):
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass
