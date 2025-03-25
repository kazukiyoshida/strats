import asyncio
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

S = TypeVar("S")


class Strategy(ABC, Generic[S]):
    @abstractmethod
    async def run(
        self,
        state: S,
        stop_event: asyncio.Event,
    ):
        pass
