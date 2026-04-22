"""Runtime configuration pulled from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    llm_base_url: str
    llm_model: str
    llm_api_key: str
    max_steps: int
    request_timeout: float


def load_settings() -> Settings:
    return Settings(
        llm_base_url=os.environ.get("LLM_BASE_URL", "http://localhost:8000/api/v1"),
        llm_model=os.environ.get("LLM_MODEL", "Qwen3-4B-Instruct-2507-GGUF"),
        llm_api_key=os.environ.get("LLM_API_KEY", "not-needed"),
        max_steps=int(os.environ.get("MAX_STEPS", "8")),
        request_timeout=float(os.environ.get("LLM_TIMEOUT", "60")),
    )
