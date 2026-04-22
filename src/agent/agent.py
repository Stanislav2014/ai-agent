"""Main agent loop: thought → action → observation → … → final_answer."""

from __future__ import annotations

import json
import sys
from collections.abc import Sequence
from typing import Protocol

from agent.executor import Executor
from agent.parser import ParseError, parse_llm_response
from agent.prompts import render_system_prompt


MAX_STEPS_MESSAGE = "Не удалось решить за отведённое количество шагов"
LOOP_ABORT_MESSAGE = "Loop detected, abort."
_OBSERVATION_CAP = 4_000


class _Chatty(Protocol):
    def chat(self, messages: Sequence[dict]) -> str: ...


class Agent:
    def __init__(
        self,
        llm: _Chatty,
        executor: Executor,
        max_steps: int = 8,
    ) -> None:
        self._llm = llm
        self._executor = executor
        self._max_steps = max_steps

    def run(self, task: str) -> str:
        system = render_system_prompt(self._executor.describe())
        messages: list[dict] = [
            {"role": "system", "content": system},
            {"role": "user", "content": task},
        ]
        previous_action: tuple[str, str] | None = None

        for step in range(1, self._max_steps + 1):
            raw = self._llm.chat(messages)
            print(f"\n[Step {step}]")

            try:
                data = parse_llm_response(raw)
            except ParseError as exc:
                print(f"Parse error: {exc}")
                messages.append({"role": "assistant", "content": raw})
                messages.append(
                    {
                        "role": "tool",
                        "content": (
                            "Error: your response was not valid JSON. "
                            "Reply STRICTLY using the specified JSON schema."
                        ),
                    }
                )
                continue

            messages.append({"role": "assistant", "content": raw})

            if "final_answer" in data:
                answer = str(data["final_answer"])
                print(f"Final: {answer}")
                return answer

            action = data["action"]
            args = data.get("args") or {}
            thought = data.get("thought", "")

            print(f"Thought: {thought}")
            print(f"Action: {action}")
            print(f"Args: {args}")

            key = (action, json.dumps(args, sort_keys=True, ensure_ascii=False))
            if previous_action is not None and previous_action == key:
                print(LOOP_ABORT_MESSAGE, file=sys.stderr)
                return LOOP_ABORT_MESSAGE
            previous_action = key

            observation = self._executor.execute(action, args)
            if len(observation) > _OBSERVATION_CAP:
                observation = observation[:_OBSERVATION_CAP] + "...[truncated]"
            print(f"Observation: {observation}")
            messages.append({"role": "tool", "content": observation})

        print(MAX_STEPS_MESSAGE, file=sys.stderr)
        return MAX_STEPS_MESSAGE
