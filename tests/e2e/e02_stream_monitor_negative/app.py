from collections.abc import AsyncGenerator

from strats import Strats
from strats.monitor import StreamClient, StreamMonitor


class SampleStreamClient(StreamClient):
    async def stream(self) -> AsyncGenerator[int]:
        raise ValueError("ERROR IN STREAM_CLIENT")
        yield 1


def main():
    Strats(
        monitors=[
            StreamMonitor(
                client=SampleStreamClient(),
            )
        ],
    ).serve()


if __name__ == "__main__":
    main()
