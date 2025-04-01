import asyncio
import logging
import threading

from .monitor import Monitor
from .state import State
from .strategy import Strategy

logger = logging.getLogger(__name__)


class Kernel:
    def __init__(
        self,
        *,
        state: State,
        strategy: Strategy,
        monitors: list[Monitor],
    ):
        self.state = state
        self.state_stop_event = None

        # There is no event loop yet, so don't create an `asyncio.Event`.
        self.monitors = monitors
        self.monitor_tasks: dict[str, asyncio.Task] = {}
        self.monitor_stop_events: dict[str, asyncio.Event] = {}

        self.strategy = strategy
        self.strategy_task = None
        self.strategy_stop_event = None

    async def start_strategy(self):
        self.state.set_queues()

        if self.strategy_task and not self.strategy_task.done():
            return

        self.strategy_stop_event = asyncio.Event()
        self.strategy_task = asyncio.create_task(
            self.strategy.run(
                self.state,
                self.strategy_stop_event,
            ),
            name="strategy",
        )

    async def stop_strategy(self, timeout=5.0):
        self.strategy_stop_event.set()

        try:
            await asyncio.wait_for(self.strategy_task, timeout=timeout)
        except asyncio.TimeoutError:
            logger.error("Timeout waiting for strategy to stop. Forcing cancellation...")

            if not self.strategy_task.done():
                self.strategy_task.cancel()

            try:
                await self.strategy_task
            except Exception as e:
                logger.error(f"(After cancel) Strategy task raised an exception: {e}")

    async def start_monitors(self):
        self.state.set_queues()

        self.state_stop_event = threading.Event()
        self.state.run(self.state_stop_event)

        for monitor in self.monitors:
            task = self.monitor_tasks.get(monitor.name)
            if task and not task.done():
                continue

            stop_event = asyncio.Event()
            self.monitor_stop_events[monitor.name] = stop_event

            self.monitor_tasks[monitor.name] = asyncio.create_task(
                monitor.run(self.state, stop_event),
                name=monitor.name,
            )

    async def stop_monitors(self, timeout=5.0):
        self.state_stop_event.set()

        for stop_event in self.monitor_stop_events.values():
            stop_event.set()

        try:
            results = await asyncio.wait_for(
                asyncio.gather(*self.monitor_tasks.values(), return_exceptions=True),
                timeout=timeout,
            )
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Monitor task {i} raised an exception: {result}")

        except asyncio.TimeoutError:
            logger.error("Timeout waiting for monitors to stop. Forcing cancellation...")

            for task in self.monitor_tasks.values():
                if not task.done():
                    task.cancel()

            results = await asyncio.gather(*self.monitor_tasks.values(), return_exceptions=True)
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"(After cancel) Monitor task {i} raised an exception: {result}")
