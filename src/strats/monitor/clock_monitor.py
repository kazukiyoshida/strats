import asyncio
import logging
from typing import Callable, Optional

from strats.core import Monitor, State

logger = logging.getLogger(__name__)


class ClockMonitor(Monitor):
    _counter = 0

    def __init__(
        self,
        job: Callable,
        interval_sec: int = 60,
        monitor_name: Optional[str] = None,
        data_name: Optional[str] = None,
        on_init: Optional[Callable] = None,
        on_delete: Optional[Callable] = None,
        start_delay_seconds: int = 0,
    ):
        self.job = job
        self.interval_sec = interval_sec

        if monitor_name is None:
            monitor_name = f"ClockMonitor{ClockMonitor._counter}"
            ClockMonitor._counter += 1
        self._monitor_name = monitor_name

        self.data_name = data_name

        # Lifecycle Hook
        self.on_init = on_init
        self.on_delete = on_delete

        self.start_delay_seconds = start_delay_seconds

    @property
    def name(self) -> str:
        return self._monitor_name

    async def run(self, state: Optional[State]):
        if self.start_delay_seconds > 0:
            await asyncio.sleep(self.start_delay_seconds)

        try:
            logger.info(f"{self.name} start")

            if self.on_init is not None:
                self.on_init()

            while True:
                await self.job(state)
                await asyncio.sleep(self.interval_sec)

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
