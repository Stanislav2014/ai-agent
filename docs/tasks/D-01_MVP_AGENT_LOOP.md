# D-01 · MVP AI-agent loop

**Status:** ✅ Done (Sprint 1)
**Branch:** `feature/BAU/mvp-agent-loop`
**Design:** [../superpowers/specs/2026-04-21-mvp-agent-loop-design.md](../superpowers/specs/2026-04-21-mvp-agent-loop-design.md)

## Problem

Учебная домашка: построить простого autonomous AI-агента с локальной LLM (qwen3-4b), который:
- принимает задачу от пользователя,
- работает по циклу `thought → action → observation → …`,
- использует инструменты (≥ 1, рекомендовано 3),
- сам решает, когда остановиться (`final_answer`),
- защищён от бесконечного цикла.

## Design

См. полный дизайн-док: [2026-04-21-mvp-agent-loop-design.md](../superpowers/specs/2026-04-21-mvp-agent-loop-design.md).

TL;DR:
- Python 3.11, 8 модулей в `src/agent/`.
- OpenAI SDK → `lemonade-server` (`Qwen3-4B-Instruct-2507-GGUF`).
- Три tool'а: `calculator` (AST-safe), `read_file` (50 KB cap), `http_get` (httpx, 10 s, 5 KB cap).
- Agent loop: `MAX_STEPS=8` + loop-guard (repeat action abort).
- Docker compose на общей `llm-net` + Makefile.

## Success criteria

- [x] `pytest tests/unit -v` — all green (47 passed)
- [x] coverage ≥ 85 % (`make test-cov` — 85 %)
- [x] `make build` проходит
- [x] Три live-теста из ТЗ проходят вживую:
  - [x] `"Посчитай (123 + 456) * 2"` → final_answer содержит `1158`
  - [x] `"Прочитай /workspace/test.txt …"` → final_answer содержит `5`
  - [x] `"Сделай GET к https://api.github.com …"` → final_answer содержит `200`
- [x] Логи прогонов сохранены в [docs/dialogs/](../dialogs/)
- [x] Структура `docs/` развёрнута по `docs-organization.md §1`

## Scope

### In scope
- Агент + 3 tools + CLI + Docker + TDD юниты + integration smoke
- docs/: все файлы из `docs-organization.md §1`

### Out of scope (перенос в Sprint 2+)
- Долгосрочная память (vector store)
- Planner (planning step перед execution)
- Streaming LLM ответов
- Native function-calling API (lemonade)
- Web UI / REST API

## Uncertainty list → resolved

1. **Модель `qwen3.5:4b` из ТЗ** — её не существует как отдельной серии. Используем `Qwen3-4B-Instruct-2507-GGUF` (Qwen3 + Q4_K_M), доступна в lemonade-каталоге.
2. **Бэкенд — ollama / vllm / lemonade?** — у пользователя нет ollama, но есть работающий lemonade-server (сосед на `llm-net`). Выбран lemonade.
3. **Формат ответов модели — чистый JSON или будет ```json fences```?** — на практике Qwen3-4B возвращает чистый JSON, но parser всё равно устойчив к обёрткам.

## Pending action items

(пусто — все решены)

## TDD phases

### Phase 0 — Research
- [x] Lemonade живой: `curl http://localhost:8000/api/v1/models` вернул 3 модели включая Qwen3-4B-Instruct.
- [x] `llm-net` активна, ai-bot и lemonade на ней.
- [x] Ollama/python3-venv недоступны на хосте → venv через `virtualenv` + Docker как основной deploy target.

### Phase 1 — Core
- [x] `parser.py` + 10 тестов (bare JSON, fences, preamble, missing keys, garbage, final_answer precedence)
- [x] `tools.py` + 17 тестов (calc parametrized, read_file happy/notfound/truncate, http_get ok/404/timeout/non-http/cap)
- [x] `executor.py` + 7 тестов (known/unknown/exception/missing-arg/custom-registry/describe/tool-error)
- [x] `agent.py` + 8 тестов (happy / final-first / max-steps / loop-guard / parse-retry / history / unknown-tool-recovery / log-format)

### Phase 2 — UI (CLI)
- [x] `__main__.py` + 5 тестов (happy / fallback-exits / --max-steps override / missing arg)

### Phase 3 — Gating
- [x] `LLMError` перехвачен в CLI → exit 2
- [x] `ParseError` → retry-hint observation, count в MAX_STEPS
- [x] Loop-guard: repeat action abort
- [x] `_OBSERVATION_CAP = 4000` в history
- [x] `http_get`/`read_file` собственные caps

### Phase 4 — Testing
- [x] `make test` — 47/47
- [x] `make test-cov` — 85 %
- [x] `make test-int` — 3/3 (22.6 s live прогон)

### Phase 5 — Review & docs
- [x] `architecture.md` с § Edge cases (15 пунктов)
- [x] `context-dump.md` file:line карта
- [x] `tech-stack.md` версии и env
- [x] `contracts/external/lemonade.md`
- [x] `sprints/current-sprint.md` — в Done
- [x] `change-request.md` — статус Merged
- [x] `prompts/prompts-sprint-1.md` — архив диалога с AI-собеседником

## Regression watch

- Расширение tools → обновить `_TOOL_DOCS` в `executor.py`, иначе system prompt недоописан.
- Смена модели → `make test-int` (parser устойчив, но стоит проверить).
- Изменение `_OBSERVATION_CAP` / `_FILE_CAP` / `_HTTP_CAP` → влияет на context window агента и стоимость prompt'а.

## Checkpoints

**Phase 1:** mocked юниты — parser 10/10, tools 17/17, executor 7/7, agent 8/8. Всё зелёное.

**Phase 4:** `make test` — 47/47. Coverage 85 % (`llm.py` 40 % — покрыт через integration, не беда). Docker image собран. Live lemonade — 3/3 ТЗ-теста, логи сохранены.

## History

- 2026-04-19 — задача получена (ТЗ + спек от пользователя)
- 2026-04-21 — 4/4 уточняющих вопроса отвечены «A» (lemonade / 3 tools / full docs / strict TDD)
- 2026-04-21 — design-док утверждён → `docs/superpowers/specs/2026-04-21-mvp-agent-loop-design.md`
- 2026-04-21 — парсер (10 зелёных)
- 2026-04-21 — tools (17 зелёных)
- 2026-04-21 — executor (7 зелёных)
- 2026-04-21 — agent loop (8 зелёных)
- 2026-04-21 — CLI (5 зелёных)
- 2026-04-21 — Docker image собран, unit в контейнере 47/47
- 2026-04-21 — live-прогон 3/3, логи в `docs/dialogs/`
- 2026-04-21 — docs заполнены, D-01 closed
