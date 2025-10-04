from typing import Any, Dict
from unittest.mock import MagicMock, patch
import pytest
from backend.ai_agents.code_generation_team import (
    get_code_generator_agent,
    generate_scaffold,
)


@pytest.mark.asyncio
@patch("backend.ai_agents.code_generation_team.generate_scaffold")
async def test_generate_scaffold(mock_generate_scaffold: MagicMock) -> None:
    # Arrange
    mock_generate_scaffold.return_value = {
        "project_structure": {"src": ["main.py"]},
        "files": [{"file_path": "src/main.py", "content": "print('hello world')"}],
    }

    # Act
    result = await generate_scaffold({}, [], [])

    # Assert
    assert result is not None
    assert hasattr(result, "project_structure")
