"""Thin wrapper around the OpenAI-compatible lemonade chat endpoint."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from openai import OpenAI
from openai import APIError, APIConnectionError, APITimeoutError


class LLMError(RuntimeError):
    """Raised for any transport or API failure talking to the LLM."""


@dataclass(frozen=True)
class ChatResult:
    content: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cache_n: int = 0
    prompt_per_second: float = 0.0
    predicted_per_second: float = 0.0
    prompt_ms: float = 0.0
    predicted_ms: float = 0.0


class LLMClient(Protocol):
    def chat(self, messages: Sequence[dict]) -> ChatResult: ...


def _extract_timings(completion) -> dict:
    """Pull lemonade's `timings` extension off an OpenAI-SDK completion object."""
    timings = getattr(completion, "timings", None)
    if timings is None:
        model_extra = getattr(completion, "model_extra", None)
        if isinstance(model_extra, dict):
            timings = model_extra.get("timings")
    if timings is None:
        return {}
    if isinstance(timings, dict):
        return timings
    fields = ("cache_n", "prompt_per_second", "predicted_per_second", "prompt_ms", "predicted_ms")
    return {f: getattr(timings, f, None) for f in fields}


class LLMProvider:
    """OpenAI-SDK-based client pointed at a local lemonade server."""

    def __init__(
        self,
        base_url: str,
        model: str,
        api_key: str = "not-needed",
        timeout: float = 60.0,
    ) -> None:
        self._model = model
        self._timeout = timeout
        self._client = OpenAI(base_url=base_url, api_key=api_key, timeout=timeout)

    def chat(self, messages: Sequence[dict]) -> ChatResult:
        try:
            completion = self._client.chat.completions.create(
                model=self._model,
                messages=list(messages),
                temperature=0.2,
            )
        except (APIConnectionError, APITimeoutError) as exc:
            raise LLMError(f"LLM transport error: {exc}") from exc
        except APIError as exc:
            raise LLMError(f"LLM API error: {exc}") from exc
        if not completion.choices:
            raise LLMError("LLM returned no choices")
        content = completion.choices[0].message.content
        if content is None:
            raise LLMError("LLM returned empty content")
        usage = getattr(completion, "usage", None)
        prompt_tokens = int(getattr(usage, "prompt_tokens", 0) or 0)
        completion_tokens = int(getattr(usage, "completion_tokens", 0) or 0)
        t = _extract_timings(completion)
        return ChatResult(
            content=content,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cache_n=int(t.get("cache_n") or 0),
            prompt_per_second=float(t.get("prompt_per_second") or 0.0),
            predicted_per_second=float(t.get("predicted_per_second") or 0.0),
            prompt_ms=float(t.get("prompt_ms") or 0.0),
            predicted_ms=float(t.get("predicted_ms") or 0.0),
        )
