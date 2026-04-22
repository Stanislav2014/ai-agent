"""CLI entry point: ``python -m agent "<task>"``."""

from __future__ import annotations

import argparse
import sys
from dataclasses import replace
from typing import Sequence

from agent.agent import Agent, LOOP_ABORT_MESSAGE, MAX_STEPS_MESSAGE
from agent.config import Settings, load_settings
from agent.executor import Executor
from agent.llm import LLMError, LLMProvider


def build_agent(settings: Settings) -> Agent:
    llm = LLMProvider(
        base_url=settings.llm_base_url,
        model=settings.llm_model,
        api_key=settings.llm_api_key,
        timeout=settings.request_timeout,
    )
    return Agent(llm=llm, executor=Executor(), max_steps=settings.max_steps)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ai-agent", description="MVP AI agent on local LLM")
    parser.add_argument("task", help="Task text for the agent to solve")
    parser.add_argument("--max-steps", type=int, default=None, help="Override MAX_STEPS")
    args = parser.parse_args(argv)

    settings = load_settings()
    if args.max_steps is not None:
        settings = replace(settings, max_steps=args.max_steps)

    print(f"Task: {args.task}")
    print(f"Model: {settings.llm_model} @ {settings.llm_base_url}")

    agent = build_agent(settings)

    try:
        answer = agent.run(args.task)
    except LLMError as exc:
        print(f"\nLLM error: {exc}", file=sys.stderr)
        return 2

    print("\n=== ANSWER ===")
    print(answer)

    if answer in {MAX_STEPS_MESSAGE, LOOP_ABORT_MESSAGE}:
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
