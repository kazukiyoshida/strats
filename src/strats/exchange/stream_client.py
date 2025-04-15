from abc import ABC, abstractmethod


class StreamClient(ABC):
    @abstractmethod
    def stream(self):
        pass
