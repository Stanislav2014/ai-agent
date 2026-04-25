"""Main agent loop: thought → action → observation → … → final_answer."""

from __future__ import annotations

import json
import sys
import time
from collections.abc import Sequence
from typing import Protocol

from agent.executor import Executor
from agent.llm import ChatResult
from agent.parser import ParseError, parse_llm_response
from agent.prompts import render_system_prompt


MAX_STEPS_MESSAGE = "Не удалось решить за отведённое количество шагов"
LOOP_ABORT_MESSAGE = "Loop detected, abort."
_OBSERVATION_CAP = 4_000


class _Chatty(Protocol):
    def chat(self, messages: Sequence[dict]) -> ChatResult: ...


def _tok_segment(prompt_tokens: int, completion_tokens: int) -> str:
    if prompt_tokens or completion_tokens:
        return f" · {prompt_tokens} in / {completion_tokens} out"
    return ""


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
        run_start = time.perf_counter()
        steps_taken = 0
        total_in = 0
        total_out = 0

        for step in range(1, self._max_steps + 1):
            steps_taken = step
            llm_start = time.perf_counter()
            result = self._llm.chat(messages)
            llm_dt = time.perf_counter() - llm_start
            raw = result.content
            total_in += result.prompt_tokens
            total_out += result.completion_tokens
            tok = _tok_segment(result.prompt_tokens, result.completion_tokens)

            try:
                data = parse_llm_response(raw)
            except ParseError as exc:
                print(f"\n[Step {step}]  (llm {llm_dt:.2f}s{tok})")
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
                total_dt = time.perf_counter() - run_start
                print(f"\n[Step {step}]  (llm {llm_dt:.2f}s{tok})")
                print(f"Final: {answer}")
                self._print_total(total_dt, step, total_in, total_out)
                return answer

            action = data["action"]
            args = data.get("args") or {}
            thought = data.get("thought", "")

            key = (action, json.dumps(args, sort_keys=True, ensure_ascii=False))
            if previous_action is not None and previous_action == key:
                print(f"\n[Step {step}]  (llm {llm_dt:.2f}s{tok})")
                print(f"Thought: {thought}")
                print(f"Action: {action}")
                print(f"Args: {args}")
                print(LOOP_ABORT_MESSAGE, file=sys.stderr)
                return LOOP_ABORT_MESSAGE
            previous_action = key

            tool_start = time.perf_counter()
            observation = self._executor.execute(action, args)
            tool_dt = time.perf_counter() - tool_start
            if len(observation) > _OBSERVATION_CAP:
                observation = observation[:_OBSERVATION_CAP] + "...[truncated]"

            print(f"\n[Step {step}]  (llm {llm_dt:.2f}s · tool {tool_dt:.2f}s{tok})")
            print(f"Thought: {thought}")
            print(f"Action: {action}")
            print(f"Args: {args}")
            print(f"Observation: {observation}")
            messages.append({"role": "tool", "content": observation})

        total_dt = time.perf_counter() - run_start
        self._print_total(total_dt, steps_taken, total_in, total_out, suffix=" (max-steps reached)", stream=sys.stderr)
        print(MAX_STEPS_MESSAGE, file=sys.stderr)
        return MAX_STEPS_MESSAGE

    @staticmethod
    def _print_total(total_dt: float, steps: int, total_in: int, total_out: int,
                     suffix: str = "", stream=None) -> None:
        tok = f", {total_in} in / {total_out} out" if (total_in or total_out) else ""
        line = f"\nTotal: {total_dt:.2f}s, {steps} step(s){tok}{suffix}"
        if stream is None:
            print(line)
        else:
            print(line, file=stream)
