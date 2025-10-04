"""
Tests for AI Governor - Safe AI plan execution.
"""

from typing import Dict, List, Any
import pytest
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.ai_governor import AIGovernor
from backend.core.graph_manager import get_graph_manager


class TestAIGovernor:
    """Test AI Governor functionality."""

    def test_plan_validation(self) -> None:
        """Test plan structure validation."""
        graph_manager = get_graph_manager()
        governor = AIGovernor(graph_manager)

        # Valid plan
        valid_plan: List[Dict[str, Any]] = [
            {"action": "CREATE_NODE", "data": {"name": "Test", "module_type": "service"}},
            {"action": "CREATE_DEPENDENCY", "from": "id1", "to": "id2", "type": "uses"},
        ]

        result = governor._validate_plan_structure(valid_plan)
        assert result["valid"] is True
        assert len(result["errors"]) == 0

    def test_invalid_plan_missing_action(self) -> None:
        """Test validation catches missing action."""
        graph_manager = get_graph_manager()
        governor = AIGovernor(graph_manager)

        invalid_plan: List[Dict[str, Any]] = [{"data": {"name": "Test"}}]  # Missing 'action'

        result = governor._validate_plan_structure(invalid_plan)
        assert result["valid"] is False
        assert len(result["errors"]) > 0
        assert "Missing 'action'" in result["errors"][0]

    def test_invalid_plan_missing_data(self) -> None:
        """Test validation catches missing data."""
        graph_manager = get_graph_manager()
        governor = AIGovernor(graph_manager)

        invalid_plan: List[Dict[str, Any]] = [{"action": "CREATE_NODE"}]  # Missing 'data'

        result = governor._validate_plan_structure(invalid_plan)
        assert result["valid"] is False

    def test_plan_conversion_to_refmem_format(self) -> None:
        """Test conversion from Codorch to RefMemTree format."""
        graph_manager = get_graph_manager()
        governor = AIGovernor(graph_manager)
        project_id = uuid4()

        codorch_plan: List[Dict[str, Any]] = [
            {"action": "CREATE_NODE", "data": {"name": "UserService", "module_type": "service"}},
            {"action": "CREATE_DEPENDENCY", "from": "id1", "to": "id2", "type": "uses"},
        ]

        refmem_plan = governor._convert_to_refmem_plan(codorch_plan, project_id)

        assert len(refmem_plan) == 2
        assert refmem_plan[0]["operation"] == "add_node"
        assert refmem_plan[1]["operation"] == "add_dependency"

    @pytest.mark.asyncio
    async def test_execute_plan_without_refmemtree(self, async_session: AsyncSession) -> None:
        """Test graceful handling when RefMemTree not available."""
        graph_manager = get_graph_manager()
        governor = AIGovernor(graph_manager)
        project_id = uuid4()

        plan: List[Dict[str, Any]] = [{"action": "CREATE_NODE", "data": {"name": "Test", "module_type": "module"}}]

        # Should not crash
        result = await governor.execute_architecture_plan(project_id, plan, async_session, dry_run=True)

        # Either succeeds or returns graceful error
        assert "status" in result
        assert result["status"] in ["success", "error", "validation_failed"]
