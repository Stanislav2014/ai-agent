# Design — MVP AI-agent on local LLM (qwen3-4b via lemonade)

**Date:** 2026-04-21
**Status:** Approved by user (all 4 clarifying questions answered "A")
**Scope:** Sprint 1, задача `D-01_MVP_AGENT_LOOP`

---

## 1. Goal

Реализовать простого autonomous AI-агента:
- принимает текстовую задачу от пользователя
- думает пошагово (`thought → action → observation → …`)
- вызывает инструменты (minimum 3)
- работает в цикле, завершается `final_answer`
- использует локальную модель `Qwen3-4B-Instruct-2507-GGUF` через lemonade-server (OpenAI-compatible)

## 2. Architecture

```
┌─────────────┐   task    ┌───────────┐   messages  ┌──────────────┐
│   CLI       │──────────▶│  Agent    │────────────▶│ LLMProvider  │
│ __main__.py │           │ agent.py  │◀────────────│  (openai →   │
└─────────────┘           └─────┬─────┘   raw JSON  │  lemonade)   │
                                │                    └──────────────┘
                                ▼
                          ┌───────────┐          ┌─────────────┐
                          │  parser   │          │  Executor   │
                          │(JSON+fix) │          │ executor.py │
                          └─────┬─────┘          └──────┬──────┘
                                │                        │ dispatch
                                │                        ▼
                                │            ┌───────────────────────┐
                                │            │ tools.py              │
                                │            │  • calculator         │
                                │            │  • read_file          │
                                │            │  • http_get           │
                                │            └───────────────────────┘
                                │
                                ▼
                         final_answer (str)
```

## 3. Components

| Module | Responsibility |
|---|---|
| `src/agent/config.py` | env-driven constants: `LLM_BASE_URL`, `LLM_MODEL`, `MAX_STEPS` |
| `src/agent/prompts.py` | `SYSTEM_PROMPT` (текст из ТЗ) + `render_tools_description()` |
| `src/agent/llm.py` | `LLMProvider.chat(messages) → raw_content`, OpenAI SDK + lemonade base_url |
| `src/agent/tools.py` | Pure functions: `calculator`, `read_file`, `http_get` |
| `src/agent/executor.py` | `Executor.execute(name, args) → observation` |
| `src/agent/parser.py` | `parse_llm_response(raw) → dict` c recovery от ```json fences``` |
| `src/agent/agent.py` | `Agent.run(task) → final_answer`, loop, history, step limit, loop-guard |
| `src/agent/__main__.py` | CLI: `python -m agent "<task>"` |

## 4. Agent loop

```
init  : messages = [system, user(task)]
step N (1..MAX_STEPS):
  raw  = llm.chat(messages)                # log [Step N] raw
  try:
    data = parser.parse_llm_response(raw)
  except ParseError:
    messages += [assistant(raw), tool("Error: respond STRICTLY as JSON …")]
    continue
  messages += [assistant(raw)]
  if "final_answer" in data → return data["final_answer"]
  if "action" in data:
    if (action, args) seen last step → return "Loop detected, abort."
    obs = executor.execute(data["action"], data.get("args") or {})
    messages += [tool(str(obs)[:4000])]
exit loop → return "Не удалось решить за отведённое количество шагов"
```

## 5. JSON contract

Agent-side **INPUT** (from LLM), два валидных формата:

```json
{"thought": "...", "action": "tool_name", "args": {...}}
{"final_answer": "..."}
```

Parser допускает:
- preamble/epilog мусор вокруг первого `{…}`
- ```` ```json … ``` ```` fences
- Required keys: либо `final_answer`, либо `action` (+опционально `thought`, `args`)

## 6. Tools

| Name | Args | Behaviour |
|---|---|---|
| `calculator` | `{expression: str}` | AST-whitelist eval (`Num, BinOp, UnaryOp, …`), no names/imports |
| `read_file` | `{path: str}` | `pathlib.Path.read_text()`, cap 50 KB, truncate suffix |
| `http_get` | `{url: str}` | `httpx.get`, 10s timeout, http(s) only, cap 5 KB body |

Все кидают `ToolError` на невалид, `Executor` ловит и возвращает `"Error: <msg>"` в observation.

## 7. Controls

- **MAX_STEPS = 8** (override через env)
- **Loop-guard:** одинаковая пара `(action, json.dumps(args, sort_keys=True))` подряд → abort
- **Observation cap:** 4 KB в history, 5 KB в http_get raw, 50 KB в read_file raw
- **Timeouts:** LLM 60s, http_get 10s

## 8. Stack

- Python 3.11+ (Docker: `python:3.11-slim`)
- `openai>=1.40` (OpenAI-compatible SDK → lemonade)
- `httpx>=0.27`
- `pytest>=8`, `pytest-mock`, `respx` (httpx mocking)
- `lemonade-server` на `llm-net` docker network (`http://lemonade:8000/api/v1`)

## 9. Docker

- Свой `Dockerfile` (python:3.11-slim, non-root user)
- `docker-compose.yml` — services: `agent`, network: `llm-net` (external)
- `Makefile`: `network / build / run TASK=… / test / test-int / shell / clean`
- Volume `./workspace:/workspace:ro` для тестовых файлов tool `read_file`

## 10. Testing (TDD)

Unit (pytest, mocked):
- `parser` — 5 кейсов
- каждый tool — happy + error
- `executor` — known/unknown/exception
- `agent` loop — happy / max-steps / loop-detect / parse-retry

Integration (live lemonade):
- 3 теста из ТЗ (calc / read_file / http_get)
- Вывод в `docs/dialogs/` для acceptance

Coverage target: ≥ 85 % юнитов.

## 11. Edge cases (полный список → в `architecture.md`)

1. LLM возвращает ``` ```json ``` ``` fences → parser вытаскивает
2. LLM вернул не-JSON → retry-с-подсказкой (не падаем)
3. LLM зациклился на одной и той же action → loop-guard
4. LLM галлюцинирует tool-имя → executor возвращает error, агент может исправиться
5. `args` отсутствуют / null → передаём `{}`
6. LLM вернул оба ключа (action + final_answer) → приоритет `final_answer`
7. Observation > cap → обрезаем + суффикс
8. Lemonade таймаут/OOM → `LLMError`, agent.run возвращает fallback, exit code 1
9. http_get: не-http(s) URL → ToolError
10. read_file: absolute path outside `/workspace` → допускаем (доверяем юзеру), но размер-guard

## 12. Success criteria (Definition of Done)

- [ ] `pytest tests/unit -v` — all green
- [ ] coverage ≥ 85 %
- [ ] `make build` проходит без ошибок
- [ ] Три интеграционных теста из ТЗ проходят вживую с lemonade:
  1. `"Посчитай (123 + 456) * 2"` → final_answer содержит `1158`
  2. `"Прочитай /workspace/test.txt и скажи сколько строк"` → корректное число
  3. `"Сделай GET к https://api.github.com и верни статус"` → 200
- [ ] Логи прогонов сохранены в `docs/dialogs/`
- [ ] `docs/` структура полностью развёрнута по `docs-organization.md §1`
- [ ] task spec `docs/tasks/D-01_*.md` заполнена

## 13. Out of scope (Sprint 1)

- Долгосрочная память (vector store, conversations persistence)
- Planner / multi-step planning before execution
- Streaming LLM responses
- Function-calling API lemonade (используем чистый JSON-prompting)
- Web UI / REST API — только CLI в этом спринте
