# Testing

## Стек

- `pytest ≥ 8` — runner
- `pytest-mock` — fixture-based mocking
- `pytest-cov` — coverage
- `respx` — httpx mocking для `http_get`

Marker: `@pytest.mark.integration` — тесты, которым нужен живой lemonade на `llm-net`; в юнит-прогонах они отсеиваются через `pytestmark` в модуле + fallback `_endpoint_reachable()` → `pytest.skip`.

## Команды

| Цель | Команда |
|---|---|
| Unit (в Docker) | `make test` |
| Unit + coverage | `make test-cov` |
| Integration (live lemonade) | `make test-int` |
| Unit (hostside venv) | `.venv/bin/pytest tests/unit -v` |

## Текущие цифры

- **47** unit тестов, все зелёные
- **Coverage:** 85 % (`llm.py` 40 % — покрыт через integration)
- **3** integration теста — все зелёные против `Qwen3-4B-Instruct-2507-GGUF`, ~7 s на прогон

## Покрытие по модулям

| Модуль | Unit-тестов | Что тестируем |
|---|---|---|
| `parser.py` | 10 | bare JSON, ```fences```, preamble, nested args, missing keys, garbage, empty, final_answer precedence, args missing |
| `tools.py` | 17 | calc parametrized, reject names/attr, div-by-zero, empty; read_file happy/not-found/truncate; http_get ok/404/timeout/non-http/cap |
| `executor.py` | 7 | known tool, unknown, tool exception, missing arg, custom registry, describe, ToolError propagation |
| `agent.py` | 8 | happy / final-first / max-steps / loop-guard / parse-retry / history-includes-tool / unknown-tool-recovery / log-format |
| `__main__.py` (CLI) | 5 | happy / fallback exit / --max-steps / missing arg |

## Integration tests (tests/integration/test_live.py)

Все помечены `pytestmark = pytest.mark.integration`. Перед каждым fixture проверяет TCP-коннект к `LLM_BASE_URL` — если не открывается, весь модуль skip.

1. `test_calculator_task` — «Посчитай (123 + 456) * 2» → assert `"1158" in answer`
2. `test_read_file_task` — «Прочитай /workspace/test.txt» → assert `"5" in answer`
3. `test_http_get_task` — «GET https://api.github.com» → assert `"200" in answer`

## Фикстуры и mocks

- `ScriptedLLM` (в `tests/unit/test_agent.py`) — очередь raw-строк, фиксирует `calls`.
- `respx.mock` — для `http_get`, чтобы не ходить наружу.
- `tmp_path` (pytest builtin) — для `read_file` тестов.
