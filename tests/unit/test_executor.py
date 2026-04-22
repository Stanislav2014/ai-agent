import pytest

from agent.executor import Executor
from agent.tools import ToolError


def test_calls_known_tool():
    ex = Executor()
    assert ex.execute("calculator", {"expression": "2+2"}) == "4"


def test_unknown_tool_returns_error_string():
    ex = Executor()
    out = ex.execute("nope", {})
    assert out.startswith("Error:")
    assert "unknown tool" in out.lower()
    assert "nope" in out


def test_tool_exception_is_returned_as_observation():
    ex = Executor()
    out = ex.execute("calculator", {"expression": "1/0"})
    assert out.startswith("Error:")
    assert "division" in out.lower()


def test_missing_required_arg_returns_error():
    ex = Executor()
    out = ex.execute("calculator", {})
    assert out.startswith("Error:")


def test_custom_registry_overrides_defaults():
    calls = []

    def fake(note: str) -> str:
        calls.append(note)
        return "ok"

    ex = Executor(tools={"echo": fake})
    assert ex.execute("echo", {"note": "hi"}) == "ok"
    assert calls == ["hi"]
    # default tools are no longer registered
    assert ex.execute("calculator", {"expression": "1+1"}).startswith("Error:")


def test_describe_lists_tool_specs():
    ex = Executor()
    desc = ex.describe()
    for name in ("calculator", "read_file", "http_get"):
        assert name in desc


def test_tool_error_from_custom_registered_tool():
    def always_fails(**_: object) -> str:
        raise ToolError("nope")

    ex = Executor(tools={"bad": always_fails})
    out = ex.execute("bad", {})
    assert out.startswith("Error:")
    assert "nope" in out
