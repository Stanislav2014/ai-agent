from pathlib import Path

import httpx
import pytest
import respx

from agent.tools import ToolError, calculator, http_get, read_file


# ---------- calculator ----------


@pytest.mark.parametrize(
    "expr,expected",
    [
        ("1+1", "2"),
        ("(123 + 456) * 2", "1158"),
        ("2**10", "1024"),
        ("-(3 + 4)", "-7"),
        ("10 / 4", "2.5"),
    ],
)
def test_calculator_basic(expr, expected):
    assert calculator(expr) == expected


def test_calculator_rejects_names():
    with pytest.raises(ToolError):
        calculator("__import__('os').system('echo hi')")


def test_calculator_rejects_attribute():
    with pytest.raises(ToolError):
        calculator("(1).__class__")


def test_calculator_div_by_zero_is_tool_error():
    with pytest.raises(ToolError):
        calculator("1/0")


def test_calculator_empty():
    with pytest.raises(ToolError):
        calculator("")


# ---------- read_file ----------


def test_read_file_happy(tmp_path: Path):
    f = tmp_path / "a.txt"
    f.write_text("hello\nworld\n")
    assert read_file(str(f)) == "hello\nworld\n"


def test_read_file_not_found(tmp_path: Path):
    with pytest.raises(ToolError):
        read_file(str(tmp_path / "nope.txt"))


def test_read_file_truncates_large(tmp_path: Path):
    f = tmp_path / "big.txt"
    f.write_text("x" * 60_000)
    out = read_file(str(f))
    assert len(out) <= 50_000 + 64
    assert out.endswith("...[truncated]")


# ---------- http_get ----------


@respx.mock
def test_http_get_ok():
    respx.get("https://example.com/").mock(
        return_value=httpx.Response(200, text="body-content")
    )
    result = http_get("https://example.com/")
    assert result.startswith("200")
    assert "body-content" in result


@respx.mock
def test_http_get_404():
    respx.get("https://example.com/x").mock(
        return_value=httpx.Response(404, text="nope")
    )
    result = http_get("https://example.com/x")
    assert result.startswith("404")


@respx.mock
def test_http_get_timeout():
    respx.get("https://slow.example/").mock(
        side_effect=httpx.TimeoutException("timeout")
    )
    with pytest.raises(ToolError):
        http_get("https://slow.example/")


def test_http_get_rejects_non_http():
    with pytest.raises(ToolError):
        http_get("ftp://example.com/x")


@respx.mock
def test_http_get_caps_body():
    respx.get("https://big.example/").mock(
        return_value=httpx.Response(200, text="a" * 20_000)
    )
    result = http_get("https://big.example/")
    # 200 status line + capped body (<= ~5200)
    assert len(result) <= 5200
