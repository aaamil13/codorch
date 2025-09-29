"""AI client for OpenAI-compatible API (Gemini)."""

import asyncio
from typing import Any, Optional

from openai import AsyncOpenAI, OpenAI
from openai.types.chat import ChatCompletion

from backend.core.config import settings


class AIClient:
    """
    OpenAI-compatible client for AI operations.

    Supports Gemini models through OpenAI-compatible API.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ) -> None:
        """Initialize AI client."""
        self.base_url = base_url or settings.OPENAI_BASE_URL
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.DEFAULT_MODEL

        # Initialize sync and async clients
        self._sync_client = OpenAI(base_url=self.base_url, api_key=self.api_key)
        self._async_client = AsyncOpenAI(base_url=self.base_url, api_key=self.api_key)

        # Rate limiting
        self._semaphore = asyncio.Semaphore(settings.AI_RATE_LIMIT)
        self._call_count = 0

    def create_completion(
        self,
        messages: list[dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> ChatCompletion:
        """
        Create chat completion (synchronous).

        Args:
            messages: List of message dicts with role and content
            model: Model to use (default: settings.DEFAULT_MODEL)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional arguments for API

        Returns:
            ChatCompletion object
        """
        self._call_count += 1

        try:
            response = self._sync_client.chat.completions.create(
                model=model or self.model,
                messages=messages,  # type: ignore
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )
            return response
        except Exception as e:
            raise AIClientError(f"Failed to create completion: {e}") from e

    async def create_completion_async(
        self,
        messages: list[dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> ChatCompletion:
        """
        Create chat completion (asynchronous).

        Args:
            messages: List of message dicts with role and content
            model: Model to use (default: settings.DEFAULT_MODEL)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional arguments for API

        Returns:
            ChatCompletion object
        """
        async with self._semaphore:  # Rate limiting
            self._call_count += 1

            try:
                response = await self._async_client.chat.completions.create(
                    model=model or self.model,
                    messages=messages,  # type: ignore
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs,
                )
                return response
            except Exception as e:
                raise AIClientError(f"Failed to create completion: {e}") from e

    async def create_completion_with_retry(
        self,
        messages: list[dict[str, str]],
        model: Optional[str] = None,
        max_retries: Optional[int] = None,
        **kwargs: Any,
    ) -> ChatCompletion:
        """
        Create completion with automatic retry on failure.

        Args:
            messages: List of message dicts
            model: Model to use
            max_retries: Maximum retry attempts
            **kwargs: Additional arguments

        Returns:
            ChatCompletion object
        """
        max_retries = max_retries or settings.AI_MAX_RETRIES
        last_error = None

        for attempt in range(max_retries):
            try:
                return await self.create_completion_async(messages, model=model, **kwargs)
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    # Exponential backoff
                    wait_time = 2**attempt
                    await asyncio.sleep(wait_time)
                continue

        raise AIClientError(
            f"Failed after {max_retries} retries: {last_error}"
        ) from last_error

    def extract_text_from_completion(self, completion: ChatCompletion) -> str:
        """Extract text content from completion response."""
        if not completion.choices:
            return ""

        message = completion.choices[0].message
        return message.content or ""

    def get_call_count(self) -> int:
        """Get total number of API calls made."""
        return self._call_count

    def reset_call_count(self) -> None:
        """Reset call counter."""
        self._call_count = 0


class AIClientError(Exception):
    """Exception raised for AI client errors."""

    pass


# Global AI client instance
_ai_client: Optional[AIClient] = None


def get_ai_client() -> AIClient:
    """Get global AI client instance."""
    global _ai_client
    if _ai_client is None:
        _ai_client = AIClient()
    return _ai_client


def get_advanced_ai_client() -> AIClient:
    """Get AI client with advanced model."""
    return AIClient(model=settings.ADVANCED_MODEL)
