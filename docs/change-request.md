# Change Request — Sprint 3 · 2026-04-25 → ?

Зеркало активного спринта. Блоки остаются до sprint close, меняется только статус.

Закрытые спринты: [Sprint 2 archive](sprints/sprint-2-archive.md) · [Sprint 2 delivery](sprints/sprint-2-delivery.md).

---

## D-06 — Token usage в выводе шага

### Метадата

| Поле | Значение |
|---|---|
| **Task ID** | `D-06` |
| **Branch** | `main` |
| **Task spec** | [docs/tasks/D-06_TOKEN_USAGE.md](tasks/D-06_TOKEN_USAGE.md) |
| **Started** | 2026-04-25 |
| **Status** | `Merged` |
| **Owner** | stan |

### Goal

Печатать токены, потраченные на каждом шаге (`N in / M out`) и за весь прогон. Lemonade уже отдаёт `usage` в OpenAI-совместимом ответе — мы их игнорировали.

### Success criteria (verifiable)

- [x] `make test` — 60/60 (было 58, +2 теста на usage)
- [x] Live-прогон 4B на задаче `(123 + 456) * 2`: Step 1 = 461 in / 93 out, Step 2 = 571 in / 14 out, итого 1032 in / 107 out
- [x] Acceptance-лог [docs/dialogs/test6-token-usage.log](dialogs/test6-token-usage.log)
- [x] Без `usage` от сервера агент работает как раньше (нет фактического суффикса)

### Scope

**In scope**
- `ChatResult(content, prompt_tokens, completion_tokens)` как новый возвращаемый тип `LLMClient.chat()`.
- `LLMProvider.chat()` читает `completion.usage`.
- `Agent.run()` накапливает `total_in` / `total_out` и печатает их в шаге и в `Total:`.
- Защитный fallback: при отсутствии `usage` — суффикс не печатается.

**Out of scope**
- `cache_n` / `prompt_per_second` из lemonade-extension `timings` (D-07).
- Денежная стоимость прогона (нет смысла на локальной модели).
- JSON-формат usage-логов для бенча (D-08+).

### Impact / change surface

| Файл | Что изменилось |
|---|---|
| `src/agent/llm.py` | +`ChatResult` dataclass, `chat()` возвращает `ChatResult` вместо str |
| `src/agent/agent.py` | импорт `ChatResult`, `_tok_segment()` хелпер, аккумуляторы, `_print_total()` хелпер |
| `tests/unit/test_agent.py` | `ScriptedLLM` авто-оборачивает str → `ChatResult`; +2 теста |
| `docs/dialogs/test6-token-usage.log` | acceptance-лог |
| `README.md` | обновлён формат вывода и счётчик тестов (60) |

### Regression watch

- Если lemonade перестанет отдавать `usage` (после апгрейда или со сменой провайдера) — суффикс просто исчезнет. Юнит `test_token_segment_omitted_when_usage_absent` это закрепляет.
- `ChatResult` — frozen dataclass, нельзя случайно мутировать.

### History

- 2026-04-25 — открыт после live-сравнения 0.6B vs 4B; пользователь спросил «где смотришь токены?» — оказалось, lemonade отдаёт по дефолту, выкидывали зря. Реализован, Merged.
