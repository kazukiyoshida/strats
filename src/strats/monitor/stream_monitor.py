import asyncio
import logging
from typing import Optional, TypeVar

from strats.core import Monitor, State
from strats.exchange import StreamClient

logger = logging.getLogger(__name__)


S = TypeVar("S")


class StreamMonitor(Monitor):
    _counter = 0

    def __init__(
        self,
        client: StreamClient,
        data_name: Optional[str] = None,
        name: Optional[str] = None,
        init_callback=None,
        del_callback=None,
        pre_event_callback=None,
        post_event_callback=None,
    ):
        self.client = client
        self.data_name = data_name

        if name is None:
            name = f"StreamMonitor{StreamMonitor._counter}"
            StreamMonitor._counter += 1
        self._name = name

        # Callbacks
        self.init_callback = init_callback
        self.del_callback = del_callback
        self.pre_event_callback = pre_event_callback
        self.post_event_callback = post_event_callback

    @property
    def name(self) -> str:
        return self._name

    async def run(self, state: State, stop_event: asyncio.Event):
        """
        Monitor を開始する.
        戻り値はなく、あくまで client からの msg を state_data に流し込むだけ.
        stop_event 通知により Monitor は停止する. この stop_event は client と共有される.
        """
        if self.data_name:
            if self.data_name in type(state).__dict__:
                data_descriptor = type(state).__dict__[self.data_name]
            else:
                raise ValueError(f"data_name: `{self.data_name}` is not found in State")
        else:
            data_descriptor = None

        current = asyncio.current_task()
        if current is None:
            raise Exception("current_task not found")

        name = current.get_name()

        if self.init_callback is not None:
            self.init_callback()

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
                if self.pre_event_callback is not None:
                    self.pre_event_callback()

                # the body of an async generator function does not execute
                # until the first `__anext__()` call. Therefore, exceptions
                # raised before the first `yield` are not visible until iteration begins.
                try:
                    data = data_task.result()
                except StopAsyncIteration:
                    logger.info(f"{name}: streaming client stopped")
                    break
                except Exception as e:
                    logger.error(f"{name}: streaming client got error: {e}")
                    break

                if data_descriptor is not None:
                    try:
                        data_descriptor.__set__(state, data)
                    except Exception as e:
                        logger.error(f"{name}: failed to update state.{self.data_name}: {e}")

                if self.post_event_callback is not None:
                    self.post_event_callback(data)

        if self.del_callback is not None:
            self.del_callback()

        await client.aclose()
        logger.info(f"{name}: stopped")
