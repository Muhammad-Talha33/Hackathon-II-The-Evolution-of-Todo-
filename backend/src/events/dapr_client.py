"""Dapr HTTP client for pub/sub event publishing.

Phase V Part B: Publishes domain events to Kafka via Dapr sidecar.
"""
import json
import logging
import os
from dataclasses import asdict
from datetime import datetime
from typing import Any
from uuid import UUID

import httpx

logger = logging.getLogger("events.dapr")

# Dapr configuration from environment
DAPR_HTTP_PORT = int(os.environ.get("DAPR_HTTP_PORT", "3500"))
PUBSUB_NAME = os.environ.get("PUBSUB_NAME", "taskpubsub")
TOPIC_NAME = os.environ.get("TOPIC_NAME", "tasks")


def _json_serializer(obj: Any) -> Any:
    """Custom JSON serializer for event dataclass fields."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, UUID):
        return str(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def serialize_event(event: Any) -> dict:
    """Serialize a domain event dataclass to a JSON-compatible dict."""
    raw = asdict(event)
    # Re-serialize through JSON to handle datetime/UUID
    return json.loads(json.dumps(raw, default=_json_serializer))


class DaprPubSubClient:
    """Async HTTP client for publishing events via Dapr sidecar."""

    def __init__(
        self,
        dapr_port: int = DAPR_HTTP_PORT,
        pubsub_name: str = PUBSUB_NAME,
        topic: str = TOPIC_NAME,
    ):
        self.base_url = f"http://localhost:{dapr_port}"
        self.publish_url = f"{self.base_url}/v1.0/publish/{pubsub_name}/{topic}"
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Lazy-initialize the async HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=5.0)
        return self._client

    async def publish(self, event: Any) -> bool:
        """Publish a domain event to Dapr pub/sub.

        Args:
            event: A domain event dataclass instance.

        Returns:
            True if published successfully, False on failure.
        """
        try:
            payload = serialize_event(event)
            client = await self._get_client()
            response = await client.post(
                self.publish_url,
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            if response.status_code in (200, 204):
                logger.info(
                    "Event published via Dapr: %s | task_id=%s",
                    event.event_type,
                    payload.get("task_id", payload.get("new_task_id", "N/A")),
                )
                return True
            else:
                logger.warning(
                    "Dapr publish returned status %d: %s",
                    response.status_code,
                    response.text,
                )
                return False
        except httpx.ConnectError:
            logger.warning(
                "Dapr sidecar unavailable (port %d) - event not published: %s",
                DAPR_HTTP_PORT,
                event.event_type,
            )
            return False
        except Exception as e:
            logger.warning("Failed to publish event via Dapr: %s", e)
            return False

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
