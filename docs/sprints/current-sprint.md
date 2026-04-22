# Sprint 1 · 2026-04-19 → 2026-04-21

**Goal:** MVP AI-agent loop + 3 tools + Docker compose + full docs структура.
**Status:** ✅ Closed on 2026-04-21.

## Kanban

### To Do
(пусто)

### In Progress
(пусто)

### Done

- **D-01** — MVP AI-agent loop with 3 tools ([spec](../tasks/D-01_MVP_AGENT_LOOP.md)) · 2026-04-21

## Definition of Done (sprint-level)

- [x] 47 unit-тестов зелёных
- [x] Coverage ≥ 85 %
- [x] 3 integration теста из ТЗ зелёных
- [x] Docker image собирается
- [x] `docs/` структура развёрнута полностью по `docs-organization.md §1`
- [x] Три acceptance-лога в `docs/dialogs/`

## Retrospective

**Что пошло хорошо:**
- TDD-подход оправдал себя — первый live-прогон агента сработал с первой попытки, никаких regression'ов.
- Parser с balanced-brace scanner справился с реальным JSON от Qwen3-4B без правок (модель пишет чистый JSON).
- Docker compose на общей `llm-net` — нулевая настройка сети, переиспользовали инфру `ai-bot`.

**Что можно улучшить:**
- Изначально не знал, что `python3-venv` недоступен — потратил минуту на `virtualenv`. Стоит прописать в `instructions.md` для будущих проектов.
- `llm.py` тестируется только integration. Для Sprint 2 добавить юнит с `openai.OpenAI` mocked.

**Что уехало в Sprint 2+:**
- Native function calling API (D-04)
- Долгосрочная память (B-01/B-02)
- Streaming (D-02)
