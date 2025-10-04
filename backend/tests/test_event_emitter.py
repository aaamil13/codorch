"""
Tests for EventEmitter - Central event system.
"""

import pytest
from typing import Any
from backend.core.event_emitter import EventEmitter, get_event_emitter


class TestEventEmitter:
    """Test EventEmitter functionality."""

    def test_event_emitter_singleton(self) -> None:
        """Test singleton pattern."""
        emitter1 = get_event_emitter()
        emitter2 = get_event_emitter()

        assert emitter1 is emitter2

    def test_on_and_emit(self) -> None:
        """Test event subscription and emission."""
        emitter = EventEmitter()
        received_data = []

        def callback(data: Any) -> None:
            received_data.append(data)

        emitter.on("test_event", callback)
        emitter.emit("test_event", {"message": "hello"})

        assert len(received_data) == 1
        assert received_data[0]["message"] == "hello"

    def test_multiple_listeners(self) -> None:
        """Test multiple listeners for same event."""
        emitter = EventEmitter()
        call_count = [0]

        def callback1(data: Any) -> None:
            call_count[0] += 1

        def callback2(data: Any) -> None:
            call_count[0] += 10

        emitter.on("event", callback1)
        emitter.on("event", callback2)
        emitter.emit("event", {})

        assert call_count[0] == 11  # Both called

    def test_off_removes_listener(self) -> None:
        """Test removing event listener."""
        emitter = EventEmitter()
        received = []

        def callback(data: Any) -> None:
            received.append(data)

        emitter.on("event", callback)
        emitter.emit("event", "first")

        emitter.off("event", callback)
        emitter.emit("event", "second")

        assert len(received) == 1  # Only first received

    def test_once(self) -> None:
        """Test one-time event listener."""
        emitter = EventEmitter()
        call_count = [0]

        def callback(data: Any) -> None:
            call_count[0] += 1

        emitter.once("event", callback)
        emitter.emit("event", {})
        emitter.emit("event", {})  # Should not trigger

        assert call_count[0] == 1  # Called only once

    def test_listener_count(self) -> None:
        """Test counting listeners."""
        emitter = EventEmitter()

        def cb1(data: Any) -> None:
            pass

        def cb2(data: Any) -> None:
            pass

        assert emitter.listener_count("event") == 0

        emitter.on("event", cb1)
        assert emitter.listener_count("event") == 1

        emitter.on("event", cb2)
        assert emitter.listener_count("event") == 2

    def test_remove_all_listeners_for_event(self) -> None:
        """Test removing all listeners for specific event."""
        emitter = EventEmitter()

        def cb_event1_1(d: Any) -> None: pass
        def cb_event1_2(d: Any) -> None: pass
        def cb_event2_1(d: Any) -> None: pass

        emitter.on("event1", cb_event1_1)
        emitter.on("event1", cb_event1_2)
        emitter.on("event2", cb_event2_1)

        emitter.remove_all_listeners("event1")

        assert emitter.listener_count("event1") == 0
        assert emitter.listener_count("event2") == 1

    def test_error_in_callback_doesnt_crash(self) -> None:
        """Test that error in callback doesn't crash emitter."""
        emitter = EventEmitter()
        received = []

        def bad_callback(data: Any) -> None:
            raise Exception("Oops!")

        def good_callback(data: Any) -> None:
            received.append(data)

        emitter.on("event", bad_callback)
        emitter.on("event", good_callback)

        # Should not crash
        emitter.emit("event", "test")

        # Good callback should still execute
        assert len(received) == 1


@pytest.mark.asyncio
class TestEventEmitterAsync:
    """Test async event emission."""

    async def test_emit_async(self) -> None:
        """Test async event emission."""
        emitter = EventEmitter()
        received = []

        async def async_callback(data: Any) -> None:
            received.append(data)

        emitter.on("async_event", async_callback)
        await emitter.emit_async("async_event", {"test": "data"})

        assert len(received) == 1
