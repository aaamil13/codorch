"""Event bus for application-wide event handling."""

import asyncio
from collections import defaultdict
from typing import Any, Callable, Coroutine


class EventBus:
    """
    Event bus for pub/sub pattern.

    Allows components to publish and subscribe to events.
    """

    def __init__(self) -> None:
        """Initialize event bus."""
        self._subscribers: dict[str, list[Callable[..., Coroutine[Any, Any, None]]]] = (
            defaultdict(list)
        )

    def subscribe(self, event_type: str, handler: Callable[..., Coroutine[Any, Any, None]]) -> None:
        """
        Subscribe to event type.

        Args:
            event_type: Type of event to subscribe to
            handler: Async function to call when event is published
        """
        self._subscribers[event_type].append(handler)

    def unsubscribe(
        self, event_type: str, handler: Callable[..., Coroutine[Any, Any, None]]
    ) -> None:
        """
        Unsubscribe from event type.

        Args:
            event_type: Type of event to unsubscribe from
            handler: Handler to remove
        """
        if event_type in self._subscribers:
            self._subscribers[event_type].remove(handler)

    async def publish(self, event_type: str, event_data: dict[str, Any]) -> None:
        """
        Publish event to all subscribers.

        Args:
            event_type: Type of event
            event_data: Event data dictionary
        """
        if event_type not in self._subscribers:
            return

        tasks = []
        for handler in self._subscribers[event_type]:
            tasks.append(handler(event_data))

        # Execute all handlers concurrently
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    def get_subscriber_count(self, event_type: str) -> int:
        """Get number of subscribers for event type."""
        return len(self._subscribers.get(event_type, []))


# Global event bus instance
_event_bus: EventBus | None = None


def get_event_bus() -> EventBus:
    """Get global event bus instance."""
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus
