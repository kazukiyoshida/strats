import asyncio
import logging
from typing import Callable, Generic, TypeVar

from strats.exchange import StreamClient

from .monitor import Monitor

logger = logging.getLogger(__name__)


S = TypeVar("S")
D = TypeVar("D")
HandlerFunction = Callable[[S, D], None]


class StreamMonitor(Monitor, Generic[S, D]):
    def __init__(
        self,
        state: S,
        client: StreamClient,
        handler: HandlerFunction,
    ):
        self.state = state
        self.client = client
        self.handler = handler

    async def run(self, stop_event: asyncio.Event):
        """
        Monitor を開始する.
        戻り値はなく、あくまで client からの msg を handler で処理するだけ.
        stop_event 通知により Monitor は停止する. この stop_event は client と共有される.
        """
        current = asyncio.current_task()
        if current is None:
            raise Exception("current_task not found")

        name = current.get_name()

        client = self.client.stream(stop_event)

        while not stop_event.is_set():
            # 一時的な task を開始
            data_task = asyncio.create_task(client.__anext__())
            stop_task = asyncio.create_task(stop_event.wait(), name="tmp-stop-event")

            done, pending = await asyncio.wait(
                [data_task, stop_task],
                return_when=asyncio.FIRST_COMPLETED,
            )

            # 不必要になった一時的な task は終了
            for task in pending:
                task.cancel()

            if stop_task in done:
                logger.info(f"monitor={name}: stop_event received")
                break

            if data_task in done:
                # the body of an async generator function does not execute
                # until the first `__anext__()` call. Therefore, exceptions
                # raised before the first `yield` are not visible until iteration begins.
                try:
                    item = data_task.result()
                except StopAsyncIteration:
                    logger.info(f"{name}: streaming client stopped")
                    break
                except Exception as e:
                    logger.error(f"{name}: streaming client got error: {e}")
                    break
                self.handler(self.state, item)

        await client.aclose()
        logger.info(f"{name}: stopped")
