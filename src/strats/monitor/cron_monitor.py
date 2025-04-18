import asyncio
import logging
from typing import Callable, Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from strats.core import Monitor, State

logger = logging.getLogger(__name__)


class CronMonitor(Monitor):
    _counter = 0

    def __init__(
        self,
        cron_job: Callable,
        cron_schedule: str,
        monitor_name: Optional[str] = None,
        data_name: Optional[str] = None,
        on_init: Optional[Callable] = None,
        on_delete: Optional[Callable] = None,
        start_delay_seconds: int = 0,
    ):
        self.cron_job = cron_job
        self.cron_schedule = cron_schedule

        if monitor_name is None:
            monitor_name = f"CronMonitor{CronMonitor._counter}"
            CronMonitor._counter += 1
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

        self.scheduler = AsyncIOScheduler()
        self.scheduler.add_job(
            self.cron_job,
            trigger=CronTrigger.from_crontab(self.cron_schedule),
            args=[state],
        )

        try:
            logger.info(f"{self.name} start")

            if self.on_init is not None:
                self.on_init()

            self.scheduler.start()

            while True:
                await asyncio.sleep(3600)  # effectively "do nothing" for a long time

        except asyncio.CancelledError:
            # To avoid "ERROR:asyncio:Task exception was never retrieved",
            # Re-raise the CancelledError
            raise
        except Exception as e:
            logger.error(f"Unhandled exception in {self.name}: {e}")
        finally:
            if self.on_delete is not None:
                self.on_delete()

            self.scheduler.shutdown()

            logger.info(f"{self.name} stopped")
