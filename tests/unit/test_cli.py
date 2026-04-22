import pytest

import agent.__main__ as cli_module
from agent.agent import LOOP_ABORT_MESSAGE, MAX_STEPS_MESSAGE


class DummyAgent:
    def __init__(self, answer: str) -> None:
        self._answer = answer
        self.runs: list[str] = []

    def run(self, task: str) -> str:
        self.runs.append(task)
        return self._answer


def test_main_runs_task_and_prints_answer(monkeypatch, capsys):
    dummy = DummyAgent("hello")
    monkeypatch.setattr(cli_module, "build_agent", lambda settings: dummy)
    rc = cli_module.main(["compute stuff"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "hello" in out
    assert dummy.runs == ["compute stuff"]


@pytest.mark.parametrize("fallback", [MAX_STEPS_MESSAGE, LOOP_ABORT_MESSAGE])
def test_main_returns_non_zero_on_fallback(monkeypatch, fallback):
    dummy = DummyAgent(fallback)
    monkeypatch.setattr(cli_module, "build_agent", lambda settings: dummy)
    rc = cli_module.main(["x"])
    assert rc == 1


def test_max_steps_flag_override(monkeypatch):
    captured = {}

    def fake_build(settings):
        captured["max_steps"] = settings.max_steps
        return DummyAgent("done")

    monkeypatch.setattr(cli_module, "build_agent", fake_build)
    cli_module.main(["--max-steps", "3", "task"])
    assert captured["max_steps"] == 3


def test_missing_task_errors_out(monkeypatch, capsys):
    # argparse exits with SystemExit(2) on missing positional
    monkeypatch.setattr(cli_module, "build_agent", lambda s: DummyAgent("x"))
    with pytest.raises(SystemExit):
        cli_module.main([])
