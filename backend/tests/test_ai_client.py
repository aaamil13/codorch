"""Tests for AI client."""

import pytest
from unittest.mock import MagicMock

from backend.core.ai_client import AIClient, AIClientError


@pytest.fixture
def ai_client(mock_ai_client: MagicMock) -> AIClient:
    """Get AI client with mocked API."""
    client = AIClient()
    client._sync_client = mock_ai_client
    client._async_client = mock_ai_client
    return client


def test_ai_client_creation() -> None:
    """Test AI client creation."""
    client = AIClient()
    assert client.base_url is not None
    assert client.api_key is not None
    assert client.model is not None


@pytest.mark.ai
def test_create_completion(ai_client: AIClient) -> None:
    """Test creating completion."""
    messages = [{"role": "user", "content": "Hello, AI!"}]

    # This will be mocked in actual tests
    with pytest.raises(AIClientError):
        response = ai_client.create_completion(messages)


def test_call_count(ai_client: AIClient) -> None:
    """Test call counting."""
    initial_count = ai_client.get_call_count()
    ai_client.reset_call_count()
    assert ai_client.get_call_count() == 0
