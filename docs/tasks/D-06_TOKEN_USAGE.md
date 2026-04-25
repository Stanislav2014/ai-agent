# D-06 · Token usage in step output

**Status:** ✅ Done (Sprint 3, day 1)
**Branch:** `main`

## Problem

После D-04 у нас есть тайминги, но не видно, **сколько токенов** улетает на каждом шаге и за весь прогон. Без этих чисел нельзя:

- сравнивать модели по «бюджету» промпта;
- ловить раздувание контекста (tool observation залип в истории, system prompt разросся);
- оценивать, оправдан ли поход в `web_search` / `http_get` по объёму ответа.

Lemonade-сервер уже возвращает `usage.prompt_tokens` / `usage.completion_tokens` в каждом chat-completion ответе (OpenAI-spec). Мы их выкидывали в `llm.py`.

## Scope

### In scope
- `ChatResult(content, prompt_tokens, completion_tokens)` как новый возвращаемый тип `LLMClient.chat()`.
- `LLMProvider.chat()` читает `completion.usage` и заполняет поля.
- `Agent.run()` накапливает `total_in` / `total_out` и печатает:
  - в шаге: `(llm X.XXs · tool X.XXs · N in / M out)`;
  - в `Total:`: `Total: X.XXs, K step(s), TIN in / TOUT out`.
- Если `usage` отсутствует (старый сервер / не-lemonade endpoint) — суффикс с токенами просто не печатается, остальное поведение неизменно.

### Out of scope
- `cache_n` / `prompt_per_second` из lemonade-расширения `timings` (отдельная D-07, если потребуется).
- Денежная стоимость прогона (нет смысла на локальной модели).
- JSON-формат usage-логов для бенча (когда понадобится — D-08+).

## Design

```python
# llm.py
@dataclass(frozen=True)
class ChatResult:
    content: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
```

- `LLMProvider.chat()` читает `getattr(completion, "usage", None)` и оба `*_tokens`-поля через `getattr(... or 0)` — устойчиво к отсутствию.
- `Agent.run()` зовёт `result = self._llm.chat(messages)`, далее `raw = result.content`, плюс аккумулятор.
- Хелпер `_tok_segment(p, c) -> str` возвращает `" · {p} in / {c} out"` либо пустую строку.
- `_print_total(...)` печатает итоговую строку, опуская tokens-сегмент при нулевых значениях.

`ScriptedLLM` в тестах оборачивает голую строку в `ChatResult(content=...)` — старые тесты живут как раньше; новые могут передавать готовый `ChatResult` с usage.

## Success criteria

- [x] `make test` — 60/60 (+2: usage печатается, usage-сегмент опускается без данных).
- [x] Live-прогон с lemonade печатает `(llm X.XXs · tool X.XXs · N in / M out)` и `Total: …, T in / T out`.
- [x] Acceptance-лог [docs/dialogs/test6-token-usage.log](../dialogs/test6-token-usage.log).
- [x] Запросы к не-lemonade серверу без `usage` не падают (юнит покрывает).

## Files touched

| Файл | Что изменилось |
|---|---|
| `src/agent/llm.py` | +`ChatResult` dataclass, `LLMProvider.chat()` теперь возвращает `ChatResult`, читает `completion.usage` |
| `src/agent/agent.py` | импорт `ChatResult`, `_tok_segment()` хелпер, аккумуляторы `total_in/total_out`, `_print_total()` хелпер, обновлены все три ветки печати шага (parse-error, final, loop-abort, normal) |
| `tests/unit/test_agent.py` | `ScriptedLLM` авто-оборачивает str → `ChatResult`; +`test_token_usage_is_printed_and_summed`; +`test_token_segment_omitted_when_usage_absent` |
| `docs/dialogs/test6-token-usage.log` | acceptance-снимок: 461 in / 93 out на шаге 1, 571 in / 14 out на шаге 2, итого 1032 in / 107 out |

## Regression watch

- Если lemonade перестанет отдавать `usage` (например, после апгрейда) — суффикс просто исчезнет, агент продолжит работать. Юнит `test_token_segment_omitted_when_usage_absent` это закрепляет.
- `ChatResult` — frozen dataclass, нельзя случайно мутировать.
- Не-OpenAI-совместимые провайдеры (если когда-нибудь подключим) должны возвращать `ChatResult` целиком — Protocol это требует.

## History

- 2026-04-25 — открыт по запросу пользователя («а где-то смотришь кол-во потраченных токенов?»), реализован, проверен на live-прогоне с 4B-моделью. Merged.
