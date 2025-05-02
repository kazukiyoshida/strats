from abc import ABC, abstractmethod
from typing import Optional

from .state import State


class Strategy(ABC):
    def prepare(self, state: Optional[State]):
        self.state = state
        if self.state is not None:
            self.state.flush_queue()

    @abstractmethod
    async def run(self):
        pass
