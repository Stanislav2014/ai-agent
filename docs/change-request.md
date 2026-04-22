# Change Request — Sprint 1 · 2026-04-21

Зеркало активного спринта. Блоки остаются до sprint close, меняется только статус.

---

## D-01 — MVP AI-agent loop with 3 tools

### Метадата

| Поле | Значение |
|---|---|
| **Task ID** | `D-01` |
| **Branch** | `feature/BAU/mvp-agent-loop` |
| **Task spec** | [docs/tasks/D-01_MVP_AGENT_LOOP.md](tasks/D-01_MVP_AGENT_LOOP.md) |
| **Started** | 2026-04-19 |
| **Status** | `Merged` |
| **Owner** | stan |

### Goal

Реализовать autonomous AI-agent на Python с локальной LLM (Qwen3-4B через lemonade): JSON-prompting loop, 3 tool'а (calculator/read_file/http_get), loop-guard, MAX_STEPS, полный Docker compose wrapper.

### Success criteria (verifiable)

- [x] Unit-тесты зелёные → `make test` — 47 passed
- [x] Coverage ≥ 85 % → `make test-cov` — 85 %
- [x] 3 live-теста из ТЗ проходят → `make test-int` — 3 passed, логи в [docs/dialogs/](dialogs/)
- [x] Docker образ собирается → `make build` — OK
- [x] Структура `docs/` развёрнута по `docs-organization.md §1` — все файлы и директории на месте

### Scope

**In scope**
- Python 3.11 package `src/agent/` с модулями: llm, tools, executor, parser, agent, prompts, config, __main__
- Три tool'а (calculator/read_file/http_get) с жёсткими caps
- Docker compose обёртка + Makefile
- TDD-юниты + 3 integration smoke-теста
- Полная структура docs/

**Out of scope**
- Долгосрочная память / vector store
- Planner / multi-step planning before execution
- Streaming LLM responses
- Function-calling API lemonade
- Web UI / REST API

### Impact / change surface

Новый проект — все файлы созданы с нуля.

### Uncertainty list

1. ~~Модель «qwen3.5:4b» из ТЗ~~ — как отдельной не существует. Использовали `Qwen3-4B-Instruct-2507-GGUF` через lemonade.
2. ~~Формат вывода модели~~ — parser допускает ```json fences``` и preamble; подтверждено на live-прогоне.

### Pending action items

(пусто — задача закрыта)

### TDD phases

- [x] Phase 0 — Research: lemonade доступен, модель есть в каталоге
- [x] Phase 1 — Core: parser, tools, executor, agent loop
- [x] Phase 2 — UI: CLI (`python -m agent`)
- [x] Phase 3 — Gating: LLMError, ParseError-retry, loop-guard, caps
- [x] Phase 4 — Testing: 47 unit + 3 integration, coverage 85 %
- [x] Phase 5 — Review & docs: структура docs/ развёрнута

### Regression watch

- При расширении tools — не забыть `_TOOL_DOCS` в `executor.py`, иначе system prompt получит пустое описание.
- При смене модели — проверить, что она уважает JSON-format (некоторые Qwen-варианты любят обернуть в ```json). Parser это уже покрывает, но для новых моделей стоит прогнать `make test-int`.

### Checkpoints

**Phase 1 checkpoint:** parser 10/10, tools 17/17, executor 7/7, agent 8/8 — все mocked юниты зелёные.

**Phase 4 checkpoint:** 47 unit passed, coverage 85 %. `make build` OK. Три live-прогона → `1158`, `5`, `200 OK`. Логи в `docs/dialogs/`.

### History

- 2026-04-19 — started (ТЗ получено)
- 2026-04-21 — design утверждён (4/4 A), реализация завершена
- 2026-04-21 — 47/47 unit + 3/3 integration зелёные, Merged
