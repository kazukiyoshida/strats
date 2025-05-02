import asyncio
import logging
import threading
from typing import Optional

from .monitor import Monitor
from .state import State
from .strategy import Strategy

logger = logging.getLogger(__name__)


class Kernel:
    def __init__(
        self,
        *,
        state: Optional[State] = None,
        strategy: Optional[Strategy] = None,
        monitors: Optional[list[Monitor]] = None,
    ):
        self.state = state
        self.state_stop_event = None

        # There is no event loop yet, so don't create an `asyncio.Event`.
        self.monitors = monitors
        self.monitor_tasks: dict[str, asyncio.Task] = {}

        self.strategy = strategy
        self.strategy_task = None

    async def start_strategy(self):
        if self.strategy is None:
            raise ValueError("Missing strategy configuration")

        if self.state is not None:
            self.state.set_queues()

        if self.strategy_task and not self.strategy_task.done():
            return

        self.strategy.prepare(self.state)
        self.strategy_task = asyncio.create_task(
            _handle_error(self.strategy.run)(),
            name="strategy",
        )

    async def stop_strategy(self, timeout=5.0):
        if self.strategy is None:
            raise ValueError("Missing strategy configuration")
        if self.strategy_task.done():
            raise ValueError("Strategy is already stopped")

        self.strategy_task.cancel()
        try:
            await self.strategy_task
        except asyncio.CancelledError:
            pass

    async def start_monitors(self):
        if self.monitors is None:
            raise ValueError("Missing monitors configuration")

        if self.state is not None:
            self.state.set_queues()

            self.state_stop_event = threading.Event()
            self.state.run(self.state_stop_event)

        for monitor in self.monitors:
            task = self.monitor_tasks.get(monitor.name)
            if task and not task.done():
                continue

            self.monitor_tasks[monitor.name] = asyncio.create_task(
                _handle_error(monitor.run)(self.state),
                name=monitor.name,
            )

    async def stop_monitors(self, timeout=5.0):
        if self.monitors is None:
            raise ValueError("Missing monitors configuration")

        for task in self.monitor_tasks.values():
            if not task.done():
                # we should await canceled task complete
                # cf. https://docs.python.org/ja/3.13/library/asyncio-task.html#asyncio.Task.cancel
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        if self.state is not None:
            self.state_stop_event.set()
            self.state.sync_to_async_queue_thread.join()


def _handle_error(func):
    async def wrapper(*args, **kwargs):
        try:
            await func(*args, **kwargs)
        except asyncio.CancelledError:
            logger.info("handle cancel process")
            raise
        except Exception as e:
            logger.error(f"got unexpected exception: {e}")

    return wrapper
