# D-07 · Surface lemonade timings (cache_n + rates)

**Status:** ✅ Done (Sprint 3, day 1)
**Branch:** `main`

## Problem

D-06 показал `prompt_tokens` / `completion_tokens` от стандартного OpenAI-поля `usage`. Но lemonade отдаёт более богатую секцию `timings` (расширение OpenAI-spec), которую мы выкидывали:

```json
"timings": {
  "cache_n": 462,
  "prompt_per_second": 17.4,
  "predicted_per_second": 12.8,
  "prompt_ms": 57.5,
  "predicted_ms": 1052.3
}
```

Без неё нельзя:
- **Подтвердить факт KV-cache hit** — раньше делали косвенно через арифметику wall-time vs prefill rate.
- **Видеть реальную скорость prefill/generation** на твоём CPU — для честных сравнений моделей.
- **Замечать аномалии** — например, если рейт вдруг провалился, значит lemonade перегружает веса между запросами.

## Scope

### In scope
- `ChatResult` расширяется 5 полями: `cache_n`, `prompt_per_second`, `predicted_per_second`, `prompt_ms`, `predicted_ms`.
- `LLMProvider.chat()` читает `completion.timings` или `completion.model_extra["timings"]` (Pydantic v2 OpenAI SDK кладёт расширения туда).
- Помощник `_extract_timings()` устойчив к отсутствию полей (любой `None` → `0` / `0.0`).
- Step header дополняется `· cache N · pf X/s · gen Y/s` сегментом, **только** если хоть одно поле timings ненулевое.
- При работе с не-lemonade провайдером (стандартный OpenAI и т.п.) сегмент молча отсутствует.

### Out of scope
- Усреднение rates по всему прогону (можно добавить в Total: позже, когда понадобится).
- Графики / экспорт в JSON для бенча — D-08.
- `prompt_ms` / `predicted_ms` сейчас не печатаются (есть в `ChatResult`, но в шаге показываем только rates) — деталь приберечь под `--verbose` если будет нужно.

## Design

```python
# llm.py
@dataclass(frozen=True)
class ChatResult:
    content: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cache_n: int = 0
    prompt_per_second: float = 0.0
    predicted_per_second: float = 0.0
    prompt_ms: float = 0.0
    predicted_ms: float = 0.0


def _extract_timings(completion) -> dict:
    timings = getattr(completion, "timings", None)
    if timings is None:
        model_extra = getattr(completion, "model_extra", None)
        if isinstance(model_extra, dict):
            timings = model_extra.get("timings")
    if timings is None:
        return {}
    if isinstance(timings, dict):
        return timings
    fields = ("cache_n", "prompt_per_second", "predicted_per_second", "prompt_ms", "predicted_ms")
    return {f: getattr(timings, f, None) for f in fields}
```

В `agent.py` старый `_tok_segment(p, c)` стал `_tok_segment(result: ChatResult)` — собирает через `parts: list[str]` все доступные сегменты и склеивает через ` · `:
- tokens (если есть)
- cache (если timings present)
- pf X/s · gen Y/s (если rates present)

## Success criteria

- [x] `make test` — 61/61 (+1 тест на печать timings).
- [x] Live-прогон 4B на task `read_file → final`:
  - Step 1: `cache 462 · pf 17/s · gen 17/s` (горячий cache от предыдущего прогона!)
  - Step 2: `cache 489 · pf 97/s · gen 18/s`
  - Total: 2.64s (vs 10.08s в D-06 прогоне с холодным cache)
- [x] Acceptance-лог [docs/dialogs/test7-lemonade-timings.log](../dialogs/test7-lemonade-timings.log).
- [x] Без `timings` в ответе сегмент молча отсутствует (юнит `test_token_segment_omitted_when_usage_absent` это закрепил, проверка `"cache " not in out`).

## Files touched

| Файл | Что изменилось |
|---|---|
| `src/agent/llm.py` | +5 полей в `ChatResult`, +`_extract_timings()`, чтение через `model_extra` fallback |
| `src/agent/agent.py` | сигнатура `_tok_segment(result)` (was `(p, c)`), сборка через `parts` list |
| `tests/unit/test_agent.py` | +`test_lemonade_timings_are_printed_in_step_header`, `omitted_when_usage_absent` теперь проверяет cache/pf тоже |
| `docs/dialogs/test7-lemonade-timings.log` | acceptance-лог 4B |

## Регрессии

- OpenAI SDK Pydantic v2 поведение `model_extra` — потенциальная точка хрупкости. Если SDK обновится и перестанет так делать, `_extract_timings()` корректно вернёт `{}` и поля будут нулевыми. Защищено fallback'ом.
- Если lemonade когда-нибудь поменяет схему `timings` (переименует поля) — у нас будут нули вместо crash'а.
- `cache_n` неожиданно высокий **между разными процессами агента** (разные `docker compose run --rm` контейнеры) — не баг, а особенность lemonade: он держит KV-cache в своём процессе, привязка к клиенту нет. Полезно знать при бенчах: первый прогон после рестарта lemonade честный, последующие могут быть «бесплатными» из-за горячего префикса system prompt.

## Findings (live)

Запуск повторно той же задачи через `make run` дал radically разные тайминги:
- D-06 cold prog: Step 1 = 9.13s (full prefill 463 tokens), cache_n=0
- D-07 warm prog: Step 1 = 1.73s, cache_n=462 (462 из 463 токенов горячие)

Это значит **системный промпт остаётся в KV-cache lemonade между независимыми запусками агента**. Для бенча моделей это важно учитывать: или прогревать одинаково, или явно сбрасывать cache между прогонами (если lemonade поддерживает).

## History

- 2026-04-25 — открыт сразу после D-06 на запрос «уровень 1» из списка дополнительных метрик; реализован, проверен; обнаружено, что lemonade держит prefix cache между запусками. Merged.
