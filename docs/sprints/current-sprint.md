# Sprint 2 · 2026-04-22 → 2026-04-23

**Goal:** расширить агента поиском в интернете и оптимизацией HTML-ответов; оформить post-sprint-1 правки как полноценные задачи.
**Status:** ✅ Closed on 2026-04-23.

## Kanban

### To Do
(пусто)

### In Progress
(пусто)

### Done

- **D-02** — web_search tool (DuckDuckGo) + HTML→Markdown в http_get ([spec](../tasks/D-02_WEB_SEARCH.md)) · 2026-04-23

## Definition of Done (sprint-level)

- [x] 56 unit-тестов зелёных (было 47, добавлено 9)
- [x] 4-й acceptance-лог для web_search в `docs/dialogs/`
- [x] Зависимости `beautifulsoup4`, `markdownify` в `pyproject.toml`, образ пересобран
- [x] `architecture.md` обновлён (новый tool, HTML→MD этап)
- [x] `contracts/` — новый внешний контракт DDG
- [x] Репозиторий запушен на GitHub: https://github.com/Stanislav2014/ai-agent

## Retrospective

**Что пошло хорошо:**
- 4-й tool встал в существующую архитектуру (`Executor` + `_TOOL_DOCS` + юниты) без правок `agent.py`/`parser.py` — подтверждает изоляцию, заложенную в Sprint 1.
- Парсинг DDG через BeautifulSoup + селекторы (`div.result` / `a.result__a` / `.result__snippet`) работает стабильно, 5 результатов за ~0.4 s.
- `markdownify` + вырезание `nav`/`script`/`footer` до конвертации режет вес HTML-страницы до разумной пачки MD — агент теперь не захлёбывается при первом же GET.

**Что можно улучшить:**
- Параллельно запускал несколько контейнеров агента — lemonade сериализует инференс и устроил шторм перезагрузок модели (`Loading llm: Qwen3-4B → 8B → 4B`). В `instructions.md` добавить «один прогон за раз, не переключать модель без необходимости».
- HTML→MD внутри `http_get` полезен для read-pages, но не для API-ответов. Текущая эвристика по `Content-Type` работает, но не отличает «HTML-error page от JSON-API» — пока достаточно, если проявится — оформить флаг в D-06+.

**Что уехало в Sprint 3+:**
- CLI-флаг `--model` (открывается как D-03).
- Native function calling API (D-04).
- Долгосрочная память (B-01/B-02).
- Streaming (D-02 старый, переименовать).

---

## Архив

- Sprint 1 (2026-04-19 → 2026-04-21) — D-01 MVP agent loop. См. git history.
