"""In-process event bus for domain event emission and logging.

Phase V Part A: Events are stored in-memory and logged.
Phase V Part B: emit() will be replaced with Dapr/Kafka publishing.
"""
import logging
from typing import List, Any


logger = logging.getLogger("events")


class EventBus:
    """Simple in-process event bus that logs and stores events."""

    def __init__(self):
        self._events: List[Any] = []

    def emit(self, event: Any) -> None:
        """Emit a domain event: append to store and log."""
        self._events.append(event)
        logger.info("Event emitted: %s | %s", event.event_type, event)

    def get_events(self) -> List[Any]:
        """Return a copy of all emitted events."""
        return list(self._events)

    def clear(self) -> None:
        """Clear all stored events."""
        self._events.clear()


# Module-level singleton for FastAPI dependency injection
_bus = EventBus()


def get_event_bus() -> EventBus:
    """FastAPI dependency that returns the singleton EventBus."""
    return _bus
