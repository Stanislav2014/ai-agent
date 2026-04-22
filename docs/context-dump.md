# Context dump — карта кода

Все file:line ссылки актуальны для Sprint 1 (commit TBD).

## src/agent/

### `__main__.py` — CLI entry point
- `build_agent()` — `__main__.py:17` — собирает `LLMProvider + Executor + Agent` из `Settings`.
- `main(argv)` — `__main__.py:27` — argparse, override `--max-steps`, exit codes (0/1/2).

### `agent.py` — главный loop
- `Agent.run(task)` — `agent.py:28` — инициализирует history, крутит цикл, логирует `[Step N] Thought/Action/Args/Observation`.
- `LOOP_ABORT_MESSAGE` — `agent.py:17` — строка на repeat-action.
- `MAX_STEPS_MESSAGE` — `agent.py:16` — fallback на исчерпание шагов.
- `_OBSERVATION_CAP = 4000` — `agent.py:19` — обрезка перед записью в history.

### `parser.py` — JSON extraction
- `parse_llm_response(raw)` — `parser.py:16` — главный API, возвращает dict c `final_answer` либо нормализованным `action`.
- `_try_first_object(text)` — `parser.py:58` — balanced-brace scanner, допускает вложенные объекты в `args`.
- `_CODE_FENCE` — `parser.py:13` — regex для ``` ```json … ``` ```.

### `tools.py` — три инструмента
- `calculator(expression)` — `tools.py:34` — AST-whitelist (Constant/BinOp/UnaryOp).
- `read_file(path)` — `tools.py:82` — `pathlib.Path.read_text`, cap 50 KB.
- `http_get(url)` — `tools.py:102` — `httpx.get`, scheme-check, cap 5 KB body.
- `ToolError` — `tools.py:14`.

### `executor.py` — tool dispatch
- `Executor.execute(name, args)` — `executor.py:30` — dict-lookup, ловит `ToolError`/`TypeError` → observation строкой.
- `Executor.describe()` — `executor.py:47` — генерирует `{{TOOLS_DESCRIPTION}}` для system prompt.
- `DEFAULT_TOOLS` — `executor.py:15` — реестр `calculator/read_file/http_get`.
- `_TOOL_DOCS` — `executor.py:21` — человекочитаемые описания.

### `llm.py` — OpenAI SDK → lemonade
- `LLMProvider.chat(messages)` — `llm.py:30` — один chat.completions, `temperature=0.2`, ловит `APIConnectionError/APITimeoutError/APIError` → `LLMError`.

### `prompts.py` — системный промпт
- `SYSTEM_PROMPT` — `prompts.py:5` — точный текст из ТЗ с маркером `{{TOOLS_DESCRIPTION}}`.
- `render_system_prompt(tools_description)` — `prompts.py:47` — подставляет описание тулов.

### `config.py` — env settings
- `Settings` dataclass — `config.py:9`.
- `load_settings()` — `config.py:18` — читает `LLM_BASE_URL / LLM_MODEL / LLM_API_KEY / MAX_STEPS / LLM_TIMEOUT`.

## tests/

### `tests/unit/` — 47 unit-тестов, mocked
- `test_parser.py` — 10 кейсов JSON-recovery
- `test_tools.py` — 17 кейсов на три tool'а (пара-метризованный calc + read_file + http_get через respx)
- `test_executor.py` — 7 кейсов диспатча
- `test_agent.py` — 8 кейсов loop'а с `ScriptedLLM`
- `test_cli.py` — 5 кейсов аргументов + exit-кодов

### `tests/integration/test_live.py` — 3 smoke-теста против live lemonade
- `test_calculator_task` — пример №1 из ТЗ
- `test_read_file_task` — пример №2
- `test_http_get_task` — пример №3
- Helper `_endpoint_reachable()` → `pytest.skip` если `:8000` не отвечает.

## Infra

- `Dockerfile` — python:3.11-slim, non-root user `agent`, editable install.
- `docker-compose.yml` — один сервис `agent` на external `llm-net`, volumes `src/tests/workspace/dialogs`.
- `Makefile` — targets: `network / build / run / test / test-int / test-cov / shell / clean / venv`.
- `.env.example` — шаблон окружения.
- `workspace/test.txt` — fixture из 5 строк для tool `read_file`.

## docs/

- `docs/` — см. [README.md](README.md) за полным оглавлением.
- `docs/dialogs/test{1,2,3}-*.log` — зафиксированные acceptance-прогоны.
- `docs/superpowers/specs/2026-04-21-mvp-agent-loop-design.md` — утверждённый дизайн-док.
