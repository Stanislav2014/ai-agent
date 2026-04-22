"""Tools available to the agent: calculator, read_file, http_get, web_search."""

from __future__ import annotations

import ast
import operator
import re
from pathlib import Path
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
from markdownify import markdownify


class ToolError(RuntimeError):
    """Raised when a tool cannot complete its action."""


# ---------------- calculator ----------------

_BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_UNARY_OPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def calculator(expression: str) -> str:
    """Evaluate an arithmetic expression safely (AST whitelist)."""
    if not expression or not expression.strip():
        raise ToolError("empty expression")
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise ToolError(f"invalid expression: {exc.msg}") from exc
    try:
        value = _eval(tree.body)
    except ZeroDivisionError as exc:
        raise ToolError("division by zero") from exc
    except ToolError:
        raise
    except Exception as exc:  # pragma: no cover — defensive
        raise ToolError(f"evaluation failed: {exc}") from exc
    return _format_number(value)


def _eval(node: ast.AST) -> float | int:
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ToolError(f"unsupported constant: {node.value!r}")
    if isinstance(node, ast.BinOp):
        op = _BIN_OPS.get(type(node.op))
        if op is None:
            raise ToolError(f"unsupported operator: {type(node.op).__name__}")
        return op(_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp):
        op = _UNARY_OPS.get(type(node.op))
        if op is None:
            raise ToolError(f"unsupported unary operator: {type(node.op).__name__}")
        return op(_eval(node.operand))
    raise ToolError(f"disallowed expression element: {type(node).__name__}")


def _format_number(value: float | int) -> str:
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


# ---------------- read_file ----------------

_FILE_CAP = 50_000


def read_file(path: str) -> str:
    p = Path(path)
    if not p.exists():
        raise ToolError(f"file not found: {path}")
    if not p.is_file():
        raise ToolError(f"not a regular file: {path}")
    try:
        data = p.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        raise ToolError(f"cannot read {path}: {exc}") from exc
    if len(data) > _FILE_CAP:
        return data[:_FILE_CAP] + "...[truncated]"
    return data


# ---------------- http_get ----------------

_HTTP_CAP = 5_000
_HTTP_TIMEOUT = 10.0
_UA = "Mozilla/5.0 (compatible; ai-agent/0.1; +https://example.invalid)"


def http_get(url: str) -> str:
    """GET a URL; if response is HTML, convert to Markdown to save tokens."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ToolError(f"only http(s) URLs allowed, got: {parsed.scheme!r}")
    try:
        response = httpx.get(
            url,
            timeout=_HTTP_TIMEOUT,
            follow_redirects=True,
            headers={"User-Agent": _UA},
        )
    except httpx.TimeoutException as exc:
        raise ToolError(f"request timed out after {_HTTP_TIMEOUT}s") from exc
    except httpx.HTTPError as exc:
        raise ToolError(f"HTTP error: {exc}") from exc

    content_type = response.headers.get("content-type", "").lower()
    if "html" in content_type:
        body = _html_to_markdown(response.text)
    else:
        body = response.text

    body = body[:_HTTP_CAP]
    return f"{response.status_code} {response.reason_phrase}\n{body}"


def _html_to_markdown(html: str) -> str:
    """Strip script/style/nav, convert to MD, collapse whitespace."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "nav", "header", "footer", "aside", "svg", "form"]):
        tag.decompose()
    main = soup.find("main") or soup.find("article") or soup.body or soup
    md = markdownify(str(main), heading_style="ATX", strip=["a"])
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md.strip()


# ---------------- web_search ----------------

_SEARCH_URL = "https://html.duckduckgo.com/html/"
_SEARCH_MAX = 5


def web_search(query: str) -> str:
    """Search DuckDuckGo (HTML endpoint); return top results as compact text."""
    if not query or not query.strip():
        raise ToolError("empty query")
    try:
        response = httpx.post(
            _SEARCH_URL,
            data={"q": query},
            timeout=_HTTP_TIMEOUT,
            follow_redirects=True,
            headers={"User-Agent": _UA},
        )
    except httpx.TimeoutException as exc:
        raise ToolError(f"search timed out after {_HTTP_TIMEOUT}s") from exc
    except httpx.HTTPError as exc:
        raise ToolError(f"search HTTP error: {exc}") from exc

    soup = BeautifulSoup(response.text, "html.parser")
    results: list[str] = []
    for i, item in enumerate(soup.select("div.result")[:_SEARCH_MAX], start=1):
        title_el = item.select_one("a.result__a")
        snippet_el = item.select_one(".result__snippet")
        if not title_el:
            continue
        title = title_el.get_text(" ", strip=True)
        link = title_el.get("href", "")
        snippet = snippet_el.get_text(" ", strip=True) if snippet_el else ""
        results.append(f"{i}. {title}\n   {link}\n   {snippet}")

    if not results:
        return "No results."
    return "\n\n".join(results)
