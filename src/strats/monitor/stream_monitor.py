import asyncio
import logging
from typing import Callable, Optional, TypeVar

from strats.core import Monitor, State
from strats.exchange import StreamClient

logger = logging.getLogger(__name__)


S = TypeVar("S")


class StreamMonitor(Monitor):
    def __init__(
        self,
        client: StreamClient,
        data_name: Optional[str] = None,
        on_init: Optional[Callable] = None,
        on_delete: Optional[Callable] = None,
        on_pre_event: Optional[Callable] = None,
        on_post_event: Optional[Callable] = None,
    ):
        self.client = client
        self.data_name = data_name

        # Lifecycle Hook
        self.on_init = on_init
        self.on_delete = on_delete
        self.on_pre_event = on_pre_event
        self.on_post_event = on_post_event

    @property
    def name(self) -> str:
        return f"StreamMonitor/{self.data_name}"

    async def run(self, state: Optional[State], stop_event: asyncio.Event):
        """
        Monitor を開始する.
        戻り値はなく、あくまで client からの msg を state_data に流し込むだけ.
        stop_event 通知により Monitor は停止する. この stop_event は client と共有される.
        """
        logger.info(f"start {self.name}")

        if state is not None:
            if self.data_name:
                if self.data_name in type(state).__dict__:
                    data_descriptor = type(state).__dict__[self.data_name]
                else:
                    raise ValueError(f"data_name: `{self.data_name}` is not found in State")
            else:
                data_descriptor = None

        if self.on_init is not None:
            self.on_init()

        client = self.client.stream(stop_event)

        while not stop_event.is_set():
            data_task = asyncio.create_task(
                client.__anext__(),
                name="stream-monitor-data-task",
            )
            stop_task = asyncio.create_task(
                stop_event.wait(),
                name="stream-monitor-stop-event",
            )

            done, pending = await asyncio.wait(
                [data_task, stop_task],
                return_when=asyncio.FIRST_COMPLETED,
            )

            for task in pending:
                task.cancel()

            if stop_task in done:
                break

            if data_task in done:
                if self.on_pre_event is not None:
                    self.on_pre_event()

                # the body of an async generator function does not execute
                # until the first `__anext__()` call. Therefore, exceptions
                # raised before the first `yield` are not visible until iteration begins.
                try:
                    data = data_task.result()
                except StopAsyncIteration:
                    break
                except Exception as e:
                    logger.error(f"{self.name} streaming client got error: {e}")
                    break

                if data_descriptor is not None:
                    try:
                        data_descriptor.__set__(state, data)
                    except Exception as e:
                        logger.error(f"failed to update state.{self.data_name}: {e}")

                if self.on_post_event is not None:
                    self.on_post_event(data)

        if self.on_delete is not None:
            self.on_delete()

        await client.aclose()
        logger.info(f"{self.name} stopped")
