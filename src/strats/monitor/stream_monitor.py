import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Callable, Optional

from strats.core import Monitor, State

logger = logging.getLogger(__name__)


class StreamClient(ABC):
    @abstractmethod
    def prepare(self, name: str):
        pass

    @abstractmethod
    async def stream(self):
        pass


class StreamMonitor(Monitor):
    _counter = 0

    def __init__(
        self,
        client: StreamClient,
        monitor_name: Optional[str] = None,
        data_name: Optional[str] = None,
        on_init: Optional[Callable] = None,
        on_delete: Optional[Callable] = None,
        on_pre_event: Optional[Callable] = None,
        on_post_event: Optional[Callable] = None,
        start_delay_seconds: int = 0,
    ):
        if monitor_name is None:
            monitor_name = f"StreamMonitor{StreamMonitor._counter}"
            StreamMonitor._counter += 1
        self._monitor_name = monitor_name

        self.client = client
        self.client.prepare(f"{client.__class__.__name__} for {self.name}")
        self.data_name = data_name

        # Lifecycle Hook
        self.on_init = on_init
        self.on_delete = on_delete
        self.on_pre_event = on_pre_event
        self.on_post_event = on_post_event

        self.start_delay_seconds = start_delay_seconds

    @property
    def name(self) -> str:
        return self._monitor_name

    async def run(self, state: Optional[State]):
        if self.start_delay_seconds > 0:
            await asyncio.sleep(self.start_delay_seconds)

        try:
            logger.info(f"{self.name} start")

            data_descriptor = None
            if state is not None and self.data_name:
                if self.data_name in type(state).__dict__:
                    data_descriptor = type(state).__dict__[self.data_name]
                else:
                    raise ValueError(f"data_name: `{self.data_name}` is not found in State")

            if self.on_init is not None:
                self.on_init()

            async for source in self.client.stream():
                if self.on_pre_event is not None:
                    self.on_pre_event(source)

                if data_descriptor is not None:
                    try:
                        data_descriptor.__set__(state, source)
                    except Exception as e:
                        logger.error(f"failed to update state.{self.data_name}: {e}")

                if self.on_post_event is not None:
                    self.on_post_event(source)

        except asyncio.CancelledError:
            # To avoid "ERROR:asyncio:Task exception was never retrieved",
            # Re-raise the CancelledError
            raise
        except Exception as e:
            logger.error(f"Unhandled exception in {self.name}: {e}")
        finally:
            if self.on_delete is not None:
                self.on_delete()
            logger.info(f"{self.name} stopped")
