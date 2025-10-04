"""
Event Emitter - Central event broadcasting system for Codorch.

Used for:
- Real-time change notifications
- WebSocket updates
- Cross-module communication
- Alert broadcasting
"""

from typing import Any, Callable, Dict, List, Optional
import asyncio


class EventEmitter:
    """
    Central event emission system.

    Allows components to subscribe to events and receive notifications
    when those events occur.
    """

    def __init__(self) -> None:
        self.listeners: Dict[str, List[Callable]] = {}
        self._event_queue: List[Dict] = []

    def on(self, event_name: str, callback: Callable) -> None:
        """
        Register event listener.

        Args:
            event_name: Name of event to listen for
            callback: Function to call when event occurs
        """
        if event_name not in self.listeners:
            self.listeners[event_name] = []

        self.listeners[event_name].append(callback)

    def off(self, event_name: str, callback: Callable) -> None:
        """Remove event listener."""
        if event_name in self.listeners:
            try:
                self.listeners[event_name].remove(callback)
            except ValueError:
                pass

    def emit(self, event_name: str, data: Any) -> None:
        """
        Emit event to all listeners synchronously.

        Args:
            event_name: Name of event
            data: Event data to send to listeners
        """
        if event_name in self.listeners:
            for callback in self.listeners[event_name]:
                try:
                    callback(data)
                except Exception as e:
                    print(f"Error in event listener for {event_name}: {e}")

    async def emit_async(self, event_name: str, data: Any) -> None:
        """
        Emit event to all listeners asynchronously.

        For async callbacks.
        """
        if event_name in self.listeners:
            tasks = []
            for callback in self.listeners[event_name]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        tasks.append(callback(data))
                    else:
                        callback(data)
                except Exception as e:
                    print(f"Error in async event listener for {event_name}: {e}")

            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)

    def once(self, event_name: str, callback: Callable) -> None:
        """Register one-time event listener."""

        def wrapper(data: Any) -> None:
            callback(data)
            self.off(event_name, wrapper)

        self.on(event_name, wrapper)

    def remove_all_listeners(self, event_name: Optional[str] = None) -> None:
        """Remove all listeners for event or all events."""
        if event_name:
            if event_name in self.listeners:
                self.listeners[event_name] = []
        else:
            self.listeners.clear()

    def listener_count(self, event_name: str) -> int:
        """Get number of listeners for event."""
        return len(self.listeners.get(event_name, []))


# ============================================================================
# Global Event Emitter Instance
# ============================================================================

# Singleton instance used throughout application
_global_emitter: Optional[EventEmitter] = None


def get_event_emitter() -> EventEmitter:
    """Get global event emitter instance."""
    global _global_emitter
    if _global_emitter is None:
        _global_emitter = EventEmitter()
    return _global_emitter


# Convenience exports
event_emitter = get_event_emitter()
emit = event_emitter.emit
emit_async = event_emitter.emit_async
on = event_emitter.on
off = event_emitter.off
