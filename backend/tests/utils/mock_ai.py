"""Mock AI utilities for testing."""

from typing import Any
from unittest.mock import AsyncMock, MagicMock


class MockAIResponse:
    """Mock AI response."""

    def __init__(self, content: str) -> None:
        """Initialize mock response."""
        self.content = content
        self.choices = [MagicMock(message=MagicMock(content=content))]


class MockAIClient:
    """Mock AI client for testing."""

    def __init__(self, responses: list[str] | None = None) -> None:
        """Initialize mock client."""
        self.responses = responses or ["Test AI response"]
        self.call_count = 0

    async def create_completion(self, **kwargs: Any) -> MockAIResponse:
        """Mock completion creation."""
        response = self.responses[self.call_count % len(self.responses)]
        self.call_count += 1
        return MockAIResponse(response)


def create_mock_ai_client(responses: list[str] | None = None) -> MockAIClient:
    """Create mock AI client."""
    return MockAIClient(responses)
