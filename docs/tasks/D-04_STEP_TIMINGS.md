# D-04 · Step timings

**Status:** ✅ Done (Sprint 2 add-on)
**Branch:** `main`

## Problem

Агент печатал ReAct-цикл без таймингов. Узнать сколько занимает LLM vs tool vs total можно было только через `time make run …` снаружи — это суммарное wall-clock без разбиения по фазам. Для тюнинга промптов/модели этого мало.

## Scope

### In scope
- Замер времени LLM-запроса (`self._llm.chat`) на каждом шаге.
- Замер времени выполнения tool'а (`executor.execute`) на шагах, где вызывается tool.
- Печать в заголовке шага: `[Step N]  (llm 1.23s · tool 0.45s)` (или только `(llm …)` на финальном шаге и при ParseError).
- Итог после final_answer: `Total: X.XXs, N step(s)`.
- Итог при max-steps: `Total: X.XXs, N step(s) (max-steps reached)` в stderr.
- Юнит-тест, что тайминги попадают в stdout.

### Out of scope
- JSON-формат тайминг-логов (если понадобится графики — D-05).
- Разбиение LLM latency на prefill/decode (недоступно без native streaming).
- Персист в файл (сейчас только stdout — ловится `tee`/`| make ... > log` при желании).

## Design

### Замеры

```python
llm_start = time.perf_counter()
raw = self._llm.chat(messages)
llm_dt = time.perf_counter() - llm_start

tool_start = time.perf_counter()
observation = self._executor.execute(action, args)
tool_dt = time.perf_counter() - tool_start
```

`time.perf_counter()` — монотонный высокоточный таймер, ровно то что нужно для измерения интервалов внутри процесса.

### Формат вывода

```
[Step 1]  (llm 12.34s · tool 0.45s)
Thought: ...
Action: web_search
Args: {'query': '...'}
Observation: ...

[Step 2]  (llm 5.67s)
Final: ...

Total: 18.46s, 2 step(s)
```

Заголовок с таймингами печатается **после** замеров (не до), поэтому строка всегда содержит настоящие цифры. Структура Thought/Action/Args/Observation не поменялась — парсеры существующих логов продолжают работать.

### Edge cases

- **ParseError** — печатается `[Step N]  (llm X.XXs)` + `Parse error: ...` (tool не вызывался).
- **Loop-guard abort** — печатается шаг с `(llm X.XXs)` (без tool-тайминга, т.к. abort до вызова executor'а), затем `LOOP_ABORT_MESSAGE` в stderr.
- **max-steps** — итог `Total: X.XXs, N step(s) (max-steps reached)` в stderr.

## Success criteria

- [x] `make test` — 58/58 (было 57, +1 тест `test_step_and_total_timings_are_printed`)
- [x] Live-прогон показывает `(llm … · tool …)` на каждом шаге и `Total: …` в конце
- [x] ParseError-ветка корректно логирует только llm-тайминг
- [x] Loop-abort ветка логирует llm-тайминг перед abort'ом

## Files touched

- `src/agent/agent.py` — +`import time`, замеры `perf_counter` вокруг `llm.chat` и `executor.execute`, обновлённый формат печати заголовков шагов, `Total:` в конце.
- `tests/unit/test_agent.py` — +`test_step_and_total_timings_are_printed` (ScriptedLLM с проверкой наличия `(llm `, `· tool `, `Total:` в stdout).

## Regression watch

- Если `capsys`/`capfd` в будущих тестах начнёт зависеть от точного формата — мы сменили структуру строки `[Step N]` на `[Step N]  (llm ...)`. Уже поправлено в существующих тестах.
- `time.perf_counter()` может давать `0.00s` на очень быстрых моках (ScriptedLLM) — тест проверяет наличие маркеров, а не положительность.

## History

- 2026-04-23 — открыт и реализован по запросу пользователя, Merged
