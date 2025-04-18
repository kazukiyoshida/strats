from abc import ABC, abstractmethod


class StreamClient(ABC):
    @abstractmethod
    def set_name(self, name: str):
        pass

    @abstractmethod
    async def stream(self):
        pass
