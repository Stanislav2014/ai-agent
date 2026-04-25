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

### 🧟 0.6B-модель возвращает вложенный `final_answer`
**Где:** проявление — в `=== ANSWER ===` печатается `{'final_answer': '5'}` вместо `5`.
**Почему:** `Qwen3-0.6B-GGUF` иногда нарушает схему и возвращает `{"final_answer": {"final_answer": "..."}}`. Парсер пропускает это (берёт значение любого типа), `agent.py:72` оборачивает в `str()` — получается Python repr.
**Минус:** косметика для CLI, но потенциально портит downstream-интеграции если кто-то парсит финальный ответ.
**Решение:** отложено как D-09 в Sprint 3 backlog — добавить проверку `isinstance(final_answer, str)` в `parser.py` + ParseError → retry.
**Воспроизведение:** `make run TASK='Прочитай файл /workspace/test.txt и скажи сколько в нём строк' MODEL=Qwen3-0.6B-GGUF` → акт-лог [test6-token-usage.log](dialogs/test6-token-usage.log) в 4B даёт `Final: 1158`, но 0.6B на той же задаче давал `Final: {'final_answer': '5'}`.

---

## Resolved

(пусто — пока ни одного решённого долга)
