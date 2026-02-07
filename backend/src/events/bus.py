"""Event bus for domain event emission via Dapr pub/sub.

Phase V Part A: Events were stored in-memory and logged.
Phase V Part B: Events are published to Kafka via Dapr sidecar.
Falls back to in-memory logging if Dapr is unavailable (graceful degradation).
"""
import asyncio
import logging
import os
from typing import Any, List

from src.events.dapr_client import DaprPubSubClient

logger = logging.getLogger("events")


class EventBus:
    """Event bus that publishes events via Dapr pub/sub.

    Maintains backward compatibility with the Phase V Part A interface.
    If Dapr sidecar is unavailable, events are logged and stored in-memory
    (graceful degradation).
    """

    def __init__(self) -> None:
        self._events: List[Any] = []
        self._dapr = DaprPubSubClient()
        self._dapr_available: bool | None = None

    def emit(self, event: Any) -> None:
        """Emit a domain event.

        Attempts to publish via Dapr pub/sub asynchronously.
        Falls back to in-memory storage if Dapr is unavailable.
        The method signature is kept synchronous for backward compatibility
        with all existing call sites.
        """
        # Always store in-memory for testing/debugging
        self._events.append(event)

        # Attempt Dapr publish via fire-and-forget async task
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._publish_async(event))
        except RuntimeError:
            # No running event loop (e.g., in tests)
            logger.info(
                "Event emitted (in-process, no event loop): %s | %s",
                event.event_type,
                event,
            )

    async def _publish_async(self, event: Any) -> None:
        """Internal async method to publish event via Dapr."""
        success = await self._dapr.publish(event)
        if not success:
            logger.info(
                "Event stored in-memory (Dapr unavailable): %s | %s",
                event.event_type,
                event,
            )

    def get_events(self) -> List[Any]:
        """Return a copy of all emitted events."""
        return list(self._events)

    def clear(self) -> None:
        """Clear all stored events."""
        self._events.clear()

    async def close(self) -> None:
        """Close the Dapr client."""
        await self._dapr.close()


# Module-level singleton for FastAPI dependency injection
_bus = EventBus()


def get_event_bus() -> EventBus:
    """FastAPI dependency that returns the singleton EventBus."""
    return _bus
