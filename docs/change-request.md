# Change Request — Sprint 2 · 2026-04-22 → 2026-04-23

Зеркало активного спринта. Блоки остаются до sprint close, меняется только статус.

---

## D-02 — web_search tool + HTML→Markdown

### Метадата

| Поле | Значение |
|---|---|
| **Task ID** | `D-02` |
| **Branch** | `main` (post-sprint-1 hotfix, ретроактивно оформлено) |
| **Task spec** | [docs/tasks/D-02_WEB_SEARCH.md](tasks/D-02_WEB_SEARCH.md) |
| **Started** | 2026-04-22 |
| **Status** | `Merged` |
| **Owner** | stan |

### Goal

Расширить арсенал агента: научить искать информацию в интернете (DuckDuckGo HTML endpoint) и получать веб-страницы в Markdown вместо сырого HTML — чтобы не забивать context window разметкой.

### Success criteria (verifiable)

- [x] `make test` — 56 passed (было 47, +9 юнитов на web_search и _html_to_markdown)
- [x] 4-й acceptance-прогон записан в [docs/dialogs/test4-web-search.log](dialogs/test4-web-search.log)
- [x] Live-тест: `"Найди в интернете прогноз погоды в Москве на сегодня"` → агент делает ровно 1 `web_search` и возвращает топ-5 источников с ссылками; общее время ~30 s
- [x] `executor.describe()` содержит описание `web_search` — попадает в system prompt автоматически
- [x] Репозиторий запушен на GitHub (public)

### Scope

**In scope**
- `web_search(query) -> str` через `POST https://html.duckduckgo.com/html/`
- HTML→Markdown конвертация в `http_get` (по Content-Type)
- `beautifulsoup4` + `markdownify` как новые зависимости
- Юниты на оба компонента

**Out of scope**
- Альтернативные search API (Brave, SerpAPI)
- JS-рендеринг (headless Chrome)
- Retry/backoff на 429 от DDG
- CLI-флаг `--model` (вынесен в D-03)

### Impact / change surface

| Файл | Что изменилось |
|---|---|
| `src/agent/tools.py` | +`web_search`, +`_html_to_markdown`, +`_UA`, HTML-ветка в `http_get` |
| `src/agent/executor.py` | +`web_search` в `DEFAULT_TOOLS` и `_TOOL_DOCS`; обновлён doc для `http_get` |
| `pyproject.toml` | +`beautifulsoup4>=4.12`, +`markdownify>=0.13` |
| `tests/unit/test_tools.py` | +9 тестов |
| `docs/dialogs/test4-web-search.log` | новый acceptance-прогон |
| `docker-compose.yml` | env-substitution + `LLM_TIMEOUT=180` |
| `Makefile` | `run` больше не триггерит `build` |
| `.env.example` | добавлен `LLM_TIMEOUT` |

### Uncertainty list

1. ~~DDG может отдавать JS-only страницу~~ — `html.duckduckgo.com/html/` отдаёт чистый HTML. Проверено live.
2. ~~`markdownify` раздувает вывод~~ — стриппер убирает script/style/nav/footer/aside до конвертации; + cap 5 KB.
3. ~~UA-блокировка~~ — проставили стандартный UA; DDG пока отдаёт.

### Pending action items

(пусто — задача закрыта)

### TDD phases

- [x] Phase 0 — Research: DDG HTML endpoint живой, отдаёт `div.result`.
- [x] Phase 1 — Core: `web_search` + `_html_to_markdown` в tools.py, регистрация в executor.
- [x] Phase 2 — Testing: 9 юнитов с respx-моком DDG и inline-HTML фикстурами.
- [x] Phase 3 — Integration: `make build` с новыми deps, live-прогон через lemonade.
- [x] Phase 4 — Docs: task spec D-02, sprint doc, architecture.md, contracts.

### Regression watch

- DDG может поменять разметку результатов — при `"No results."` на явном запросе проверить селекторы `div.result`, `a.result__a`, `.result__snippet`.
- `markdownify` строго зависит от `bs4`; смена parser'а (`html.parser` → `lxml`) может слегка изменить вывод — если добавим `lxml`, нужно прогнать существующие HTML-юниты.
- Если агент станет часто получать `429 Too Many Requests` от DDG — подмешать exponential backoff в `web_search` (сейчас нет).

### Checkpoints

**Phase 2 checkpoint:** 56/56 unit (было 47/47, +9 на web_search/html-md).

**Phase 3 checkpoint:** live-прогон в ~30 s, 2 шага (web_search → final_answer), выдача 5 результатов с заголовками + URL + сниппетами.

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
| **Task spec** | [docs/tasks/D-03_CLI_MODEL_FLAG.md](tasks/D-03_CLI_MODEL_FLAG.md) |
| **Started** | 2026-04-23 |
| **Status** | `Merged` |
| **Owner** | stan |

### Goal

Разрешить смену модели прямо из CLI (`--model`) и Makefile (`MODEL=…`), не обращаясь к env.

### Success criteria (verifiable)

- [x] `make test` — 57/57 (было 56, +1 тест)
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
