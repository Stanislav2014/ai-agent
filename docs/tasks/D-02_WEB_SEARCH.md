# D-02 · web_search tool + HTML→Markdown

**Status:** ✅ Done (Sprint 2)
**Branch:** `main` (post-sprint hotfix → retroactive task)

## Problem

Агент из D-01 умел только `calculator` / `read_file` / `http_get`. На задачах вида «найди погоду/новости/статью» он:
- не имел способа искать (только fetch по известному URL),
- при получении HTML страниц забивал context window сырой разметкой (скрипты, nav, футеры).

## Scope

### In scope
- 4-й tool `web_search` через **DuckDuckGo HTML endpoint** (`https://html.duckduckgo.com/html/`).
- Автоматическое HTML→Markdown преобразование внутри `http_get` (по `Content-Type`).
- Юниты на оба компонента (парсинг DDG-HTML через фикстуру, стрип script/style/nav/footer, колапс пустых строк).
- Обновление `executor.py` `_TOOL_DOCS`.
- Acceptance-лог: `docs/dialogs/test4-web-search.log`.

### Out of scope
- Альтернативные search-провайдеры (Brave/SerpAPI) — если DDG капризничает, взять один из них в D-04+.
- JS-рендеринг страниц (agent видит только статический HTML).

## Design

### `web_search(query)`
- `POST https://html.duckduckgo.com/html/` с `data={"q": query}`, UA-заголовок.
- Парсинг `div.result` через BeautifulSoup → топ-5 результатов вида `N. <title>\n   <link>\n   <snippet>`.
- Timeout 10 s, ToolError на таймаут/сетевую ошибку.
- Пустой запрос → `ToolError("empty query")`.
- Пустая выдача → `"No results."`.

### `_html_to_markdown(html)`
- Удаляет `script`, `style`, `noscript`, `nav`, `header`, `footer`, `aside`, `svg`, `form`.
- Предпочитает содержимое `<main>` → `<article>` → `<body>`.
- `markdownify(..., heading_style="ATX", strip=["a"])`.
- Коллапс >=3 переводов строки в `\n\n`.

### Интеграция в `http_get`
- Если `Content-Type` содержит `html` — конвертируем; иначе возвращаем как раньше.
- Cap 5 KB остаётся.

## Success criteria

- [x] `make test` — 56/56 (было 47, добавлено 9 тестов)
- [x] web_search отдаёт пять результатов на реальный DDG — подтверждено live-прогоном
- [x] http_get на HTML страницу возвращает MD (без script/nav/footer)
- [x] acceptance-лог в `docs/dialogs/test4-web-search.log`
- [x] `executor.describe()` включает `web_search` в system prompt

## Uncertainty list → resolved

1. ~~DDG блокирует агентов без UA~~ — проставили `User-Agent: Mozilla/...`, отдаёт HTML.
2. ~~`markdownify` резко раздувает вывод~~ — ограничили: вырезаем nav/footer/aside до конвертации, плюс cap 5 KB после.
3. ~~Страница без `<main>`/`<article>`~~ — фолбэк на `<body>`, иначе на весь документ.

## Files touched

- `src/agent/tools.py` — новые `web_search`, `_html_to_markdown`, `_UA`, `_SEARCH_URL`, `_SEARCH_MAX`
- `src/agent/executor.py` — регистрация `web_search` в `DEFAULT_TOOLS` и `_TOOL_DOCS`
- `pyproject.toml` — deps `beautifulsoup4>=4.12`, `markdownify>=0.13`
- `tests/unit/test_tools.py` — 9 новых тестов
- `docs/dialogs/test4-web-search.log` — acceptance-прогон

## Regression watch

- DDG может поменять HTML-разметку (`div.result`, `a.result__a`, `.result__snippet`). Если получим `"No results."` на явном запросе — проверить селекторы.
- `markdownify` зависит от `bs4`; при смене parser'а (`html.parser` → `lxml`) поведение может чуть отличаться.
- UA-строка может попасть в чёрный список — тогда подстроить или рандомизировать.
