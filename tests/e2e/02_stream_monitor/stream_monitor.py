import asyncio
from collections.abc import AsyncGenerator

from strats import Strats
from strats.exchange import StreamClient
from strats.monitor import StreamMonitor


class TestStreamClient(StreamClient):
    def set_name(self, name: str):
        self.name = name

    async def stream(self) -> AsyncGenerator[int]:
        try:
            for i in range(10):
                await asyncio.sleep(1)
                yield i
        except asyncio.CancelledError:
            raise
        except Exception:
            pass


def main():
    stream_monitor = StreamMonitor(
        monitor_name="stream_monitor",
        data_name="prices",
        client=TestStreamClient(),
    )
    Strats(
        monitors=[stream_monitor],
    ).serve()


if __name__ == "__main__":
    main()
