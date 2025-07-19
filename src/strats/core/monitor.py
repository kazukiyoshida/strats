from abc import ABC, abstractmethod
from typing import Callable, Optional

from .state import State


class Monitor(ABC):
    """Base class for monitoring functionality"""

    _counter = 0

    def __init__(
        self,
        name: Optional[str] = None,
        data_name: Optional[str] = None,
        start_delay_seconds: int = 0,
        # Lifecycle Hook
        on_init: Optional[Callable] = None,
        on_delete: Optional[Callable] = None,
        on_pre_event: Optional[Callable] = None,
        on_post_event: Optional[Callable] = None,
    ):
        # Update class-specific counter
        type(self)._counter += 1

        # Initialize common attributes
        self._name = name or f"{type(self).__name__}_{type(self)._counter}"
        self.data_name = data_name
        self.start_delay_seconds = start_delay_seconds

        # Set up lifecycle hooks
        self.on_init = on_init
        self.on_delete = on_delete
        self.on_pre_event = on_pre_event
        self.on_post_event = on_post_event

        # Execute initialization hook
        if self.on_init:
            self.on_init()

    @property
    def name(self) -> str:
        return self._name

    @abstractmethod
    async def run(self, state: Optional[State]):
        pass
