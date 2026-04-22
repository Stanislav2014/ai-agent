# Legacy warning

Тех-долг, костыли, known issues. Приоритеты:
- 🔥 критично — блокирует работу или масштабирование
- ⚠ архитектурное — усложняет расширение
- 🧟 стилистическое — хочется, но не срочно

После задачи — отмечать ✅ РЕШЕНО, не удалять. История решений.

---

## Текущий тех-долг

### ⚠ JSON-prompting вместо function calling
**Где:** `src/agent/prompts.py` — SYSTEM_PROMPT просит модель строго отвечать в JSON.
**Почему:** работает на любом бэкенде, не требует поддержки tools-API.
**Минус:** модель может нарушить схему (на практике redeemит через parser-retry).
**Решение:** D-04 (Sprint 2+) — native function calling, если доедет без регрессии.

### ⚠ `Executor.describe()` не экспортит JSON-schema args
**Где:** `src/agent/executor.py:47` + `_TOOL_DOCS`.
**Почему:** подрумана вручную строкой «args: {expression: string}» — модель не видит типы формально.
**Минус:** если добавить tool с complex args, легко описать не так.
**Решение:** D-02/D-04 — схемы через `inspect.signature` + pydantic.

### 🧟 `llm.py` слабое coverage (40 %)
**Где:** unit-тесты не мокают OpenAI-клиента глубоко.
**Почему:** основная логика — маппинг исключений SDK в `LLMError`; покрывается integration.
**Решение:** можно добавить юниты с `patch("openai.OpenAI")`, но при смене SDK всё равно сломаются — текущий approach OK.

### 🧟 `workspace/` — read-only mount
**Где:** `docker-compose.yml`.
**Почему:** `read_file` только читает, `write_file` ещё не реализован.
**Решение:** при добавлении `write_file` поменять на `rw`.

---

## Resolved

(пусто — это Sprint 1)
