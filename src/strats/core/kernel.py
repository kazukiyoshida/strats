from threading import Event, Thread


class Kernel:
    def __init__(self, state, monitors):
        self.state = state
        self.monitors = monitors
        self.monitor_stop_events = {name: Event() for name in self.monitors.keys()}
        self.monitor_threads = {
            name: Thread(
                target=monitor.run,
                args=(name, self.monitor_stop_events[name]),
                daemon=True,
            )
            for name, monitor in self.monitors.items()
        }

    def start_monitors(self):
        for monitor_thread in self.monitor_threads.values():
            if not monitor_thread.is_alive():
                monitor_thread.start()

    def stop_monitors(self):
        for monitor_stop_event in self.monitor_stop_events.values():
            if not monitor_stop_event.is_set():
                monitor_stop_event.set()

        for monitor_thread in self.monitor_threads.values():
            if monitor_thread.is_alive():
                monitor_thread.join()
