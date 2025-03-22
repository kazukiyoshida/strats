import asyncio
import logging

logger = logging.getLogger(__name__)


class Kernel:
    def __init__(self, state, monitors):
        self.state = state
        self.monitors = monitors
        self.monitor_stop_events = {}  # 注意: event_loop 開始前なので Event を作成しない
        self.monitor_tasks = {}

    async def start_monitors(self):
        for name, monitor in self.monitors.items():
            task = self.monitor_tasks.get(name)
            if task and not task.done():
                continue

            # ここでは event_loop が作成済みなので Event を作成できる.
            stop_event = asyncio.Event()
            self.monitor_stop_events[name] = stop_event

            self.monitor_tasks[name] = asyncio.create_task(
                monitor.run(stop_event),
                name=name,
            )

    async def stop_monitors(self, timeout=5.0):
        for stop_event in self.monitor_stop_events.values():
            stop_event.set()

        try:
            await asyncio.wait_for(
                asyncio.gather(*self.monitor_tasks.values(), return_exceptions=True),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            logger.error("Timeout waiting for monitors to stop. Forcing cancellation...")

            for task in self.monitor_tasks.values():
                if not task.done():
                    task.cancel()

            await asyncio.gather(*self.monitor_tasks.values(), return_exceptions=True)
