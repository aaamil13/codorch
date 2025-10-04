from unittest.mock import MagicMock, patch
import pytest
from backend.ai_agents.requirements_team import analyze_requirement, RequirementAnalysis


@pytest.mark.asyncio
@patch("backend.ai_agents.requirements_team.analyze_requirement")
async def test_analyze_requirement(mock_analyze_requirement):
    # Arrange
    mock_analyze_requirement.return_value = RequirementAnalysis(
        completeness_score=10.0,
        clarity_score=10.0,
        consistency_score=10.0,
        feasibility_score=10.0,
        issues=[],
        suggestions=[],
        improved_description="test",
        recommended_acceptance_criteria=[],
    )

    # Act
    result = await analyze_requirement("", "", "", [])

    # Assert
    assert result is not None
    assert hasattr(result, "completeness_score")
