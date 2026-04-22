"""Route tool invocations from the LLM to the pure tool functions."""

from __future__ import annotations

import inspect
from collections.abc import Callable, Mapping

from agent.tools import ToolError, calculator, http_get, read_file, web_search

ToolFunc = Callable[..., str]

DEFAULT_TOOLS: dict[str, ToolFunc] = {
    "calculator": calculator,
    "read_file": read_file,
    "http_get": http_get,
    "web_search": web_search,
}

_TOOL_DOCS: dict[str, str] = {
    "calculator": "Evaluate an arithmetic expression. args: {expression: string}",
    "read_file": "Read a text file from disk. args: {path: string}",
    "http_get": "Perform an HTTP(S) GET request. HTML is auto-converted to Markdown. args: {url: string}",
    "web_search": "Search the web via DuckDuckGo; returns top-5 titles + links + snippets. args: {query: string}",
}


class Executor:
    """Dispatch a tool name + args dict to the underlying Python function."""

    def __init__(self, tools: Mapping[str, ToolFunc] | None = None) -> None:
        self._tools: dict[str, ToolFunc] = dict(tools) if tools is not None else dict(DEFAULT_TOOLS)

    def execute(self, name: str, args: Mapping[str, object] | None) -> str:
        func = self._tools.get(name)
        if func is None:
            return f"Error: unknown tool {name!r}. Available: {sorted(self._tools)}"
        kwargs: dict[str, object] = dict(args or {})
        try:
            result = func(**kwargs)
        except ToolError as exc:
            return f"Error: {exc}"
        except TypeError as exc:
            return f"Error: invalid args for {name!r}: {exc}"
        except Exception as exc:  # pragma: no cover — tool bug, not expected
            return f"Error: tool {name!r} crashed: {exc}"
        return str(result)

    def describe(self) -> str:
        """Human-readable description of registered tools (fed into the system prompt)."""
        lines: list[str] = []
        for name, func in self._tools.items():
            doc = _TOOL_DOCS.get(name) or _extract_summary(func) or f"tool {name}"
            lines.append(f"- {name}: {doc}")
        return "\n".join(lines)


def _extract_summary(func: ToolFunc) -> str:
    doc = inspect.getdoc(func)
    if not doc:
        return ""
    return doc.splitlines()[0].strip()
