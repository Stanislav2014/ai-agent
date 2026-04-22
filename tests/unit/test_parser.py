import pytest

from agent.parser import ParseError, parse_llm_response


def test_plain_action_json():
    raw = '{"thought": "think", "action": "calculator", "args": {"expression": "1+1"}}'
    data = parse_llm_response(raw)
    assert data["action"] == "calculator"
    assert data["args"] == {"expression": "1+1"}
    assert data["thought"] == "think"


def test_plain_final_answer_json():
    raw = '{"final_answer": "42"}'
    data = parse_llm_response(raw)
    assert data == {"final_answer": "42"}


def test_json_inside_code_fences():
    raw = '```json\n{"final_answer": "ok"}\n```'
    assert parse_llm_response(raw) == {"final_answer": "ok"}


def test_preamble_before_json():
    raw = 'Here is my answer:\n{"final_answer": "hi"}\nthanks'
    assert parse_llm_response(raw) == {"final_answer": "hi"}


def test_nested_object_in_args():
    raw = '{"action": "tool", "args": {"x": {"y": 1}}}'
    data = parse_llm_response(raw)
    assert data["args"] == {"x": {"y": 1}}


def test_missing_required_keys_raises():
    with pytest.raises(ParseError):
        parse_llm_response('{"foo": "bar"}')


def test_garbage_raises():
    with pytest.raises(ParseError):
        parse_llm_response("not json at all")


def test_empty_raises():
    with pytest.raises(ParseError):
        parse_llm_response("")


def test_final_answer_wins_over_action():
    raw = '{"action": "tool", "final_answer": "done"}'
    data = parse_llm_response(raw)
    assert "final_answer" in data
    assert data["final_answer"] == "done"


def test_args_missing_is_ok_for_action():
    raw = '{"action": "calculator"}'
    data = parse_llm_response(raw)
    assert data["action"] == "calculator"
