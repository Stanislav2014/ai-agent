# Sprint 3 · 2026-04-25 → ?

**Goal:** инструментовать агента — токены, кеш-метрики, более чистый формат вывода. Подготовить почву для бенча моделей.
**Status:** 🟢 Active.

## Kanban

### To Do
(пусто пока)

### In Progress
(пусто)

### Done

- **D-06** — Token usage в выводе (`N in / M out` per step + total) ([spec](../tasks/D-06_TOKEN_USAGE.md)) · 2026-04-25
- **D-07** — Lemonade timings: cache_n + prefill/gen rate в шаге ([spec](../tasks/D-07_LEMONADE_TIMINGS.md)) · 2026-04-25

## Definition of Done (sprint-level)

- [x] D-06 закрыт: 60/60 unit, acceptance-лог в `docs/dialogs/test6-token-usage.log`
- [x] D-07 закрыт: 61/61 unit, acceptance-лог в `docs/dialogs/test7-lemonade-timings.log`
- [ ] Sprint retrospective написан (когда закроем)

## Backlog (кандидаты на этот же спринт)

- **D-08** — `bench.sh` (TASK × модели последовательно, складывать SAVE-логи в `docs/dialogs/bench-<ts>/`).
- **D-09** — Hardening: `final_answer` должен быть строкой; иначе ParseError + retry. Закрывает баг 0.6B с двойной обёрткой.
- **D-10** — llm.py unit-тест с моком `openai.OpenAI` (последний пробел в покрытии).

## Retrospective

(пусто, спринт активен)

---

## Архив

- Sprint 1 (2026-04-19 → 2026-04-21) — D-01 MVP agent loop. См. git history.
- [Sprint 2](../change-request.md) (2026-04-22 → 2026-04-23) — D-02 web_search, D-03 --model, D-04 timings, D-05 SAVE=1.
