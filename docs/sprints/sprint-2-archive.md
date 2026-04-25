# Sprint 2 archive · frozen on 2026-04-23

Замороженный snapshot блоков `change-request.md` на момент закрытия Sprint 2. Не правится — для исторической справки.

---

## D-02 — web_search tool + HTML→Markdown

### Метадата

| Поле | Значение |
|---|---|
| **Task ID** | `D-02` |
| **Branch** | `main` (post-sprint-1 hotfix, ретроактивно оформлено) |
| **Task spec** | [docs/tasks/D-02_WEB_SEARCH.md](../tasks/D-02_WEB_SEARCH.md) |
| **Started** | 2026-04-22 |
| **Status** | `Merged` |
| **Owner** | stan |

### Goal

Расширить арсенал агента: научить искать информацию в интернете (DuckDuckGo HTML endpoint) и получать веб-страницы в Markdown вместо сырого HTML — чтобы не забивать context window разметкой.

### Success criteria

- [x] `make test` — 56 passed (+9 юнитов)
- [x] Acceptance-прогон в [docs/dialogs/test4-web-search.log](../dialogs/test4-web-search.log)
- [x] Live-тест: `"Найди в интернете прогноз погоды в Москве на сегодня"` → 1 `web_search`, топ-5 ссылок, ~30 s
- [x] `executor.describe()` содержит описание `web_search`
- [x] Репозиторий запушен на GitHub (public)

### Impact / change surface

| Файл | Что изменилось |
|---|---|
| `src/agent/tools.py` | +`web_search`, +`_html_to_markdown`, +`_UA`, HTML-ветка в `http_get` |
| `src/agent/executor.py` | +`web_search` в `DEFAULT_TOOLS` и `_TOOL_DOCS` |
| `pyproject.toml` | +`beautifulsoup4>=4.12`, +`markdownify>=0.13` |
| `tests/unit/test_tools.py` | +9 тестов |
| `docs/dialogs/test4-web-search.log` | acceptance-прогон |
| `docker-compose.yml` | env-substitution + `LLM_TIMEOUT=180` |
| `Makefile` | `run` больше не триггерит `build` |

### History

- 2026-04-22 — started, изменения прилетели post-sprint-1 без спеки
- 2026-04-23 — ретроактивно оформлено как D-02 в Sprint 2; добавлены юниты, acceptance-лог, docs; Merged

---

## D-03 — CLI `--model` flag

### Метадата

| Поле | Значение |
|---|---|
| **Task ID** | `D-03` |
| **Branch** | `main` |
| **Task spec** | [docs/tasks/D-03_CLI_MODEL_FLAG.md](../tasks/D-03_CLI_MODEL_FLAG.md) |
| **Started** | 2026-04-23 |
| **Status** | `Merged` |
| **Owner** | stan |

### Success criteria

- [x] `make test` — 57/57 (+1 тест)
- [x] `python -m agent --help` показывает `--model`
- [x] `make run TASK='...' MODEL=Qwen3-0.6B-GGUF` работает и печатает выбранную модель в header

### Impact / change surface

| Файл | Что изменилось |
|---|---|
| `src/agent/__main__.py` | +`--model` argparse-флаг, +`replace(settings, llm_model=...)` |
| `tests/unit/test_cli.py` | +`test_model_flag_override` |
| `Makefile` | +переменная `MODEL ?=`, +`_MODEL_ARG = $(if $(MODEL),--model $(MODEL),)` |
| `README.md` | +пример с MODEL= и --model, пояснение приоритета |

### History

- 2026-04-23 — открыт и реализован, Merged

---

## D-04 — Step timings

### Метадата

| Поле | Значение |
|---|---|
| **Task ID** | `D-04` |
| **Branch** | `main` |
| **Task spec** | [docs/tasks/D-04_STEP_TIMINGS.md](../tasks/D-04_STEP_TIMINGS.md) |
| **Started** | 2026-04-23 |
| **Status** | `Merged` |
| **Owner** | stan |

### Success criteria

- [x] `make test` — 58/58 (+1 юнит `test_step_and_total_timings_are_printed`)
- [x] Live-прогон показывает `(llm X.XXs · tool X.XXs)` в заголовке шага
- [x] Финальный шаг показывает `(llm X.XXs)` и затем `Total: X.XXs, N step(s)`
- [x] Acceptance-лог [docs/dialogs/test5-timings.log](../dialogs/test5-timings.log)

### Impact / change surface

| Файл | Что изменилось |
|---|---|
| `src/agent/agent.py` | +`import time`, замеры `perf_counter` вокруг llm.chat и executor.execute, новый формат заголовков, `Total:` footer |
| `tests/unit/test_agent.py` | +`test_step_and_total_timings_are_printed` |
| `docs/dialogs/test5-timings.log` | demo-лог с таймингами на ТЗ-тесте №1 |

### History

- 2026-04-23 — открыт по запросу пользователя, реализован + юнит + acceptance-лог, Merged

---

## D-05 — Auto-save run logs

### Метадата

| Поле | Значение |
|---|---|
| **Task ID** | `D-05` |
| **Branch** | `main` |
| **Task spec** | [docs/tasks/D-05_AUTO_SAVE_LOGS.md](../tasks/D-05_AUTO_SAVE_LOGS.md) |
| **Started** | 2026-04-23 |
| **Status** | `Merged` |
| **Owner** | stan |

### Success criteria

- [x] `make run TASK='...' SAVE=1` создаёт `docs/dialogs/run-<ts>.log` с полным выводом
- [x] Без `SAVE=1` поведение не меняется
- [x] `git status` не видит `run-*.log` (исключение в `.gitignore`)
- [x] Acceptance-снимки `test*-*.log` продолжают трекаться

### Impact / change surface

| Файл | Что изменилось |
|---|---|
| `Makefile` | +`SAVE ?=`, +`_LOG_FILE`, +`_RUN_CMD`, условная ветка `tee` в `run` |
| `.gitignore` | +`docs/dialogs/run-*.log` |
| `README.md` | +пример `SAVE=1` |

### History

- 2026-04-23 — открыт и реализован, Merged
