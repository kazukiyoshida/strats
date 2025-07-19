import asyncio
from collections.abc import AsyncGenerator

from strats import Strats
from strats.monitor import StreamClient, StreamMonitor


class SampleStreamClient(StreamClient):
    async def stream(self) -> AsyncGenerator[int]:
        for i in range(10):
            await asyncio.sleep(1)
            yield i


def main():
    stream_monitor = StreamMonitor(client=SampleStreamClient())
    Strats(monitors=[stream_monitor]).serve()


if __name__ == "__main__":
    main()
