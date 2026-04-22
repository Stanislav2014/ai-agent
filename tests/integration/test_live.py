"""End-to-end smoke tests that hit a live lemonade-server on llm-net.

Run with:  ``make test-int``
Skipped automatically if the LLM endpoint is unreachable.
"""

from __future__ import annotations

import os
import socket
from urllib.parse import urlparse

import httpx
import pytest

from agent.agent import Agent
from agent.config import load_settings
from agent.executor import Executor
from agent.llm import LLMProvider

pytestmark = pytest.mark.integration


def _endpoint_reachable(url: str) -> bool:
    try:
        parsed = urlparse(url)
        host = parsed.hostname or "localhost"
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        with socket.create_connection((host, port), timeout=2):
            return True
    except OSError:
        return False


@pytest.fixture(scope="module")
def agent() -> Agent:
    settings = load_settings()
    if not _endpoint_reachable(settings.llm_base_url):
        pytest.skip(f"LLM endpoint not reachable: {settings.llm_base_url}")
    llm = LLMProvider(
        base_url=settings.llm_base_url,
        model=settings.llm_model,
        api_key=settings.llm_api_key,
        timeout=settings.request_timeout,
    )
    return Agent(llm=llm, executor=Executor(), max_steps=settings.max_steps)


def test_calculator_task(agent: Agent):
    answer = agent.run("Посчитай (123 + 456) * 2")
    assert "1158" in answer


def test_read_file_task(agent: Agent, tmp_path):
    # workspace/test.txt is mounted read-only with 5 lines
    answer = agent.run("Прочитай файл /workspace/test.txt и скажи сколько в нём строк")
    assert "5" in answer


def test_http_get_task(agent: Agent):
    answer = agent.run("Сделай GET запрос к https://api.github.com и верни HTTP статус-код")
    assert "200" in answer
