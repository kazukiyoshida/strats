# strats/lifecycle.py
from typing import Callable, Literal

_LIFECYCLE_HANDLERS: dict[str, list[Callable]] = {
    "startup": [],
    "shutdown": [],
}


def on_event(event_type: Literal["startup", "shutdown"]):
    """Decorator to register a lifecycle event handler globally."""

    def decorator(func: Callable):
        _LIFECYCLE_HANDLERS[event_type].append(func)
        return func

    return decorator


def get_lifecycle_handlers(event_type: str) -> list[Callable]:
    return list(_LIFECYCLE_HANDLERS.get(event_type, []))
