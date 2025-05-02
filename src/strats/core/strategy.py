from abc import ABC, abstractmethod
from typing import Optional

from .state import State


class Strategy(ABC):
    def prepare(self, state: Optional[State]):
        self.state = state

    @abstractmethod
    async def run(self):
        pass
