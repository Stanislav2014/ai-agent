from collections.abc import Iterable

import pytest

from agent.agent import (
    Agent,
    LOOP_ABORT_MESSAGE,
    MAX_STEPS_MESSAGE,
)
from agent.executor import Executor


class ScriptedLLM:
    """Replays a list of raw response strings in order."""

    def __init__(self, responses: Iterable[str]) -> None:
        self._responses = list(responses)
        self.calls: list[list[dict]] = []

    def chat(self, messages):
        self.calls.append(list(messages))
        if not self._responses:
            raise AssertionError("ScriptedLLM ran out of responses")
        return self._responses.pop(0)


def test_happy_path_single_tool_then_final():
    llm = ScriptedLLM(
        [
            '{"thought": "calc", "action": "calculator", "args": {"expression": "(123+456)*2"}}',
            '{"final_answer": "1158"}',
        ]
    )
    agent = Agent(llm=llm, executor=Executor(), max_steps=5)
    assert agent.run("Посчитай (123+456)*2") == "1158"
    assert len(llm.calls) == 2


def test_final_answer_on_first_response():
    llm = ScriptedLLM(['{"final_answer": "42"}'])
    agent = Agent(llm=llm, executor=Executor(), max_steps=5)
    assert agent.run("task") == "42"


def test_max_steps_exceeded_returns_fallback():
    # always requests the same legitimate (but useless) action every step
    never_final = '{"action": "calculator", "args": {"expression": "1+1"}}'
    llm = ScriptedLLM([never_final] * 10)
    agent = Agent(llm=llm, executor=Executor(), max_steps=3)
    result = agent.run("loop forever")
    # either max steps OR loop detect will fire — both are acceptable guard outcomes
    assert result in {MAX_STEPS_MESSAGE, LOOP_ABORT_MESSAGE}


def test_loop_guard_aborts_on_repeated_action():
    same = '{"action": "calculator", "args": {"expression": "1+1"}}'
    llm = ScriptedLLM([same, same])
    agent = Agent(llm=llm, executor=Executor(), max_steps=8)
    assert agent.run("x") == LOOP_ABORT_MESSAGE


def test_parse_error_triggers_retry_and_final():
    llm = ScriptedLLM(
        [
            "not json at all",                          # parse error
            '{"final_answer": "recovered"}',            # correct
        ]
    )
    agent = Agent(llm=llm, executor=Executor(), max_steps=5)
    assert agent.run("x") == "recovered"


def test_history_contains_system_and_user_and_tool_messages():
    llm = ScriptedLLM(
        [
            '{"action": "calculator", "args": {"expression": "2+2"}}',
            '{"final_answer": "4"}',
        ]
    )
    agent = Agent(llm=llm, executor=Executor(), max_steps=3)
    agent.run("compute")
    # second LLM call must include the tool observation message
    roles_second_call = [m["role"] for m in llm.calls[1]]
    assert "tool" in roles_second_call


def test_unknown_tool_observation_lets_agent_recover():
    llm = ScriptedLLM(
        [
            '{"action": "no_such_tool", "args": {}}',
            '{"final_answer": "ok after recovery"}',
        ]
    )
    agent = Agent(llm=llm, executor=Executor(), max_steps=5)
    assert agent.run("x") == "ok after recovery"


def test_logs_printed_in_required_format(capsys):
    llm = ScriptedLLM(
        [
            '{"thought": "add", "action": "calculator", "args": {"expression": "1+1"}}',
            '{"final_answer": "2"}',
        ]
    )
    agent = Agent(llm=llm, executor=Executor(), max_steps=3)
    agent.run("add")
    out = capsys.readouterr().out
    assert "[Step 1]" in out
    assert "Thought:" in out
    assert "Action: calculator" in out
    assert "Observation" in out
    assert "Final:" in out
