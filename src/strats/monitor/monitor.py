from abc import ABC, abstractmethod
from threading import Event


class Monitor(ABC):
    @abstractmethod
    def run(self, name: str, stop_event: Event):
        pass
