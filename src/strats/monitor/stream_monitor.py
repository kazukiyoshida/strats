import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Optional

from strats.core import Monitor, State

logger = logging.getLogger(__name__)


class StreamClient(ABC):
    @abstractmethod
    async def stream(self):
        pass


class StreamMonitor(Monitor):
    def __init__(
        self,
        client: StreamClient,
        **kwargs,
    ):
        self.client = client
        self.client_name = client.__class__.__name__

        super().__init__(**kwargs)

    async def run(self, state: Optional[State]):
        if self.start_delay_seconds > 0:
            await asyncio.sleep(self.start_delay_seconds)

        try:
            logger.info(f"{self.name} start")

            data_descriptor = None

            # Error handling for Initialization
            try:
                if state is not None and self.data_name:
                    if self.data_name in type(state).__dict__:
                        data_descriptor = type(state).__dict__[self.data_name]
                    else:
                        raise ValueError(f"data_name: `{self.data_name}` is not found in State")

                if self.on_init is not None:
                    self.on_init()
            except Exception as e:
                logger.error(f"Initialization error in {self.name}: {e}")
                return

            # Error handling for stream data handling
            try:
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
            except Exception as e:
                logger.error(
                    f"Stream error in {self.name}, but maybe in the `stream` function"
                    f" in {self.client_name}: {e}"
                )

        except asyncio.CancelledError:
            # To avoid "ERROR:asyncio:Task exception was never retrieved",
            # Re-raise the CancelledError
            raise
        except Exception as e:
            # Unexpected error
            logger.error(f"Unhandled exception in {self.name}: {e}")
        finally:
            if self.on_delete is not None:
                self.on_delete()
            logger.info(f"{self.name} stopped")
