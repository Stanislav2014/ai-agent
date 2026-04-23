from pathlib import Path

import httpx
import pytest
import respx

from agent.tools import (
    ToolError,
    _html_to_markdown,
    calculator,
    http_get,
    read_file,
    web_search,
)


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


@respx.mock
def test_http_get_html_converts_to_markdown():
    html = (
        "<html><head><style>.x{}</style><script>alert(1)</script></head>"
        "<body><nav>nav</nav>"
        "<main><h1>Title</h1><p>Hello <b>world</b></p>"
        "<ul><li>one</li><li>two</li></ul></main>"
        "<footer>foot</footer></body></html>"
    )
    respx.get("https://page.example/").mock(
        return_value=httpx.Response(
            200,
            text=html,
            headers={"content-type": "text/html; charset=utf-8"},
        )
    )
    result = http_get("https://page.example/")
    assert result.startswith("200")
    assert "# Title" in result
    assert "Hello" in result
    assert "world" in result
    # script/style/nav/footer stripped
    assert "alert(1)" not in result
    assert "nav" not in result.lower().split("\n")[1:]  # no bare 'nav' line
    assert "foot" not in result


# ---------- _html_to_markdown ----------


def test_html_to_markdown_strips_scripts_and_styles():
    out = _html_to_markdown(
        "<html><body><script>x=1</script><style>.a{}</style>"
        "<p>kept</p></body></html>"
    )
    assert "x=1" not in out
    assert ".a{}" not in out
    assert "kept" in out


def test_html_to_markdown_prefers_main():
    out = _html_to_markdown(
        "<html><body><nav>menu</nav>"
        "<main><h2>Body</h2><p>content</p></main>"
        "<aside>ads</aside></body></html>"
    )
    assert "Body" in out
    assert "content" in out
    assert "menu" not in out
    assert "ads" not in out


def test_html_to_markdown_collapses_blank_lines():
    out = _html_to_markdown("<p>a</p>\n\n\n\n\n<p>b</p>")
    assert "\n\n\n" not in out


# ---------- web_search ----------


_DDG_HTML = """
<html><body>
<div class="results">
  <div class="result">
    <h2><a class="result__a" href="https://example.com/a">First Result</a></h2>
    <a class="result__snippet">snippet about first</a>
  </div>
  <div class="result">
    <h2><a class="result__a" href="https://example.com/b">Second</a></h2>
    <a class="result__snippet">snippet two</a>
  </div>
  <div class="result">
    <h2><a class="result__a" href="https://example.com/c">Third</a></h2>
    <a class="result__snippet">snippet three</a>
  </div>
</div>
</body></html>
"""


@respx.mock
def test_web_search_parses_ddg_results():
    respx.post("https://html.duckduckgo.com/html/").mock(
        return_value=httpx.Response(200, text=_DDG_HTML)
    )
    result = web_search("test query")
    assert "1. First Result" in result
    assert "https://example.com/a" in result
    assert "snippet about first" in result
    assert "2. Second" in result
    assert "3. Third" in result


@respx.mock
def test_web_search_no_results():
    respx.post("https://html.duckduckgo.com/html/").mock(
        return_value=httpx.Response(200, text="<html><body></body></html>")
    )
    assert web_search("anything") == "No results."


@respx.mock
def test_web_search_timeout():
    respx.post("https://html.duckduckgo.com/html/").mock(
        side_effect=httpx.TimeoutException("timeout")
    )
    with pytest.raises(ToolError):
        web_search("q")


def test_web_search_empty_query():
    with pytest.raises(ToolError):
        web_search("")


@respx.mock
def test_web_search_caps_at_5():
    many = "".join(
        f'<div class="result">'
        f'<a class="result__a" href="https://ex/{i}">T{i}</a>'
        f'<a class="result__snippet">s{i}</a>'
        f"</div>"
        for i in range(10)
    )
    respx.post("https://html.duckduckgo.com/html/").mock(
        return_value=httpx.Response(200, text=f"<html><body>{many}</body></html>")
    )
    result = web_search("q")
    assert "5. T4" in result
    assert "6. T5" not in result
