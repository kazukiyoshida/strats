from abc import ABC, abstractmethod


class StreamClient(ABC):
    @abstractmethod
    def prepare(self, name: str):
        pass

    @abstractmethod
    async def stream(self):
        pass
