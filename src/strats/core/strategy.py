from abc import ABC, abstractmethod
from typing import Optional

from .state import State


class Strategy(ABC):
    @abstractmethod
    async def run(self, state: Optional[State]):
        pass
