import logging
from typing import Callable, Optional

from strats.core import Monitor, State

logger = logging.getLogger(__name__)


class CronMonitor(Monitor):
    def __init__(
        self,
        cron_job: Callable,
        cron_schedule: str,
        **kwargs,
    ):
        self.cron_job = cron_job
        self.cron_schedule = cron_schedule

        super().__init__(**kwargs)

    async def run(self, state: Optional[State]):
        pass
        # if self.start_delay_seconds > 0:
        #     await asyncio.sleep(self.start_delay_seconds)

        # self.scheduler = AsyncIOScheduler()
        # self.scheduler.add_job(
        #     self.cron_job,
        #     trigger=CronTrigger.from_crontab(self.cron_schedule),
        #     args=[state],
        # )

        # try:
        #     logger.info(f"{self.name} start")

        #     if self.on_init is not None:
        #         self.on_init()

        #     self.scheduler.start()

        #     while True:
        #         await asyncio.sleep(3600)  # effectively "do nothing" for a long time

        # except asyncio.CancelledError:
        #     # To avoid "ERROR:asyncio:Task exception was never retrieved",
        #     # Re-raise the CancelledError
        #     raise
        # except Exception as e:
        #     logger.error(f"Unhandled exception in {self.name}: {e}")
        # finally:
        #     if self.on_delete is not None:
        #         self.on_delete()

        #     self.scheduler.shutdown()

        #     logger.info(f"{self.name} stopped")
