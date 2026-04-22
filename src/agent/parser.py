"""Parse structured JSON responses from the LLM."""

from __future__ import annotations

import json
import re


class ParseError(ValueError):
    """Raised when the LLM response cannot be parsed into a valid agent command."""


_CODE_FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)


def parse_llm_response(raw: str) -> dict:
    """Extract the first JSON object from raw and validate agent-command shape.

    Accepts:
      • a bare JSON object
      • JSON wrapped in ```json … ``` fences
      • JSON preceded/followed by free-form text (first balanced object wins)

    Returns a dict that contains either ``final_answer`` or ``action``
    (``final_answer`` takes precedence when both are present).
    """
    if not raw or not raw.strip():
        raise ParseError("empty response")

    candidates: list[str] = []
    for match in _CODE_FENCE.finditer(raw):
        candidates.append(match.group(1).strip())
    candidates.append(raw)

    parsed: dict | None = None
    for chunk in candidates:
        parsed = _try_first_object(chunk)
        if parsed is not None:
            break

    if parsed is None:
        raise ParseError(f"no JSON object found in response: {raw[:200]!r}")

    if "final_answer" in parsed:
        return {"final_answer": parsed["final_answer"]}
    if "action" in parsed:
        return {
            "thought": parsed.get("thought", ""),
            "action": parsed["action"],
            "args": parsed.get("args") or {},
        }
    raise ParseError(
        "response missing both 'final_answer' and 'action' keys: "
        f"{list(parsed.keys())}"
    )


def _try_first_object(text: str) -> dict | None:
    start = text.find("{")
    while start != -1:
        depth = 0
        in_str = False
        escape = False
        for i in range(start, len(text)):
            ch = text[i]
            if in_str:
                if escape:
                    escape = False
                elif ch == "\\":
                    escape = True
                elif ch == '"':
                    in_str = False
                continue
            if ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    chunk = text[start : i + 1]
                    try:
                        obj = json.loads(chunk)
                    except json.JSONDecodeError:
                        break
                    if isinstance(obj, dict):
                        return obj
                    break
        start = text.find("{", start + 1)
    return None
