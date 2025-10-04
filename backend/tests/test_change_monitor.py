"""
Tests for ChangeMonitor - Real-time change tracking.
"""

from typing import Any, Callable, Dict
import pytest
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.change_monitor import ChangeMonitor
from backend.core.graph_manager import get_graph_manager


class TestChangeMonitor:
    """Test ChangeMonitor functionality."""

    def test_change_monitor_creation(self) -> None:
        """Test ChangeMonitor can be created."""
        graph_manager = get_graph_manager()
        monitor = ChangeMonitor(graph_manager)

        assert monitor is not None
        assert monitor.graph_manager is graph_manager
        assert isinstance(monitor.callbacks, dict)

    def test_get_changed_fields(self) -> None:
        """Test identifying changed fields."""
        monitor = ChangeMonitor(get_graph_manager())

        old_data = {"name": "OldName", "type": "service", "status": "draft"}
        new_data = {"name": "NewName", "type": "service", "status": "approved"}

        changed = monitor._get_changed_fields(old_data, new_data)

        assert "name" in changed
        assert "status" in changed
        assert "type" not in changed  # Unchanged

    def test_change_callback_storage(self) -> None:
        """Test callback storage."""
        monitor = ChangeMonitor(get_graph_manager())
        node_id = uuid4()

        def dummy_callback(change: Any) -> None:
            pass

        # Initially empty
        assert node_id not in monitor.callbacks

        monitor.callbacks[node_id] = [dummy_callback]

        assert node_id in monitor.callbacks
        assert len(monitor.callbacks[node_id]) == 1

    @pytest.mark.asyncio
    async def test_register_watcher_without_refmemtree(self, async_session: AsyncSession) -> None:
        """Test graceful handling when RefMemTree not available."""
        monitor = ChangeMonitor(get_graph_manager())
        project_id = uuid4()
        node_id = uuid4()

        def callback(change: Any) -> None:
            pass

        # Should not crash
        result = await monitor.register_node_watcher(project_id, node_id, callback, async_session)

        assert isinstance(result, bool)
