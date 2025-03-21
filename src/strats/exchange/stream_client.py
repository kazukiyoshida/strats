from abc import ABC, abstractmethod
from queue import Queue


class StreamClient(ABC):
    @abstractmethod
    def start(self, queue: Queue):
        pass

    @abstractmethod
    def stop(self):
        pass
