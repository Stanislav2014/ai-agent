# Contract — DuckDuckGo HTML endpoint

Используется только tool'ом `web_search` (`src/agent/tools.py`).

## Endpoint

- `POST https://html.duckduckgo.com/html/`
- Тело: `application/x-www-form-urlencoded`, единственный параметр `q=<query>`.
- Заголовок `User-Agent: Mozilla/5.0 (compatible; ai-agent/0.1; +https://example.invalid)` — без него DDG может отдать пустую страницу или 403.

## Ответ

Статический HTML со списком результатов вида:

```html
<div class="result">
  <h2><a class="result__a" href="URL">TITLE</a></h2>
  <a class="result__snippet">SNIPPET</a>
</div>
```

## Что вытаскиваем

- Селекторы: `div.result` → `a.result__a[@href]` (title + url) + `.result__snippet` (abstract).
- Берём топ-5 (`_SEARCH_MAX = 5`).
- Формат возврата: `N. TITLE\n   URL\n   SNIPPET` для каждого, `\n\n` между результатами.
- Пустая выдача → литерал `"No results."`.

## Ошибки и лимиты

- **Rate-limit:** DDG не документирует, на практике > 10 rps начинает показывать 429 / капчу. Для MVP агента (ручные запуски) запаса хватает.
- **JS-защита:** `html.duckduckgo.com/html/` — spec-endpoint **для** статического HTML, не требует JS. Обычный `duckduckgo.com` — SPA, не подходит.
- **Сетевые сбои:** `httpx.TimeoutException` / `HTTPError` → `ToolError(...)` → Executor превращает в `"Error: …"` observation.

## Аутентификация

Нет. Публичный endpoint.

## Что может сломаться

1. DDG меняет имена классов (`div.result` / `a.result__a` / `.result__snippet`) — тогда получим `"No results."` на явном запросе. Тест `test_web_search_parses_ddg_results` использует inline-фикстуру с текущей разметкой — при изменении DDG юнит зелёный, а live — нет.
2. Блок по UA — добавить/ротировать UA-строки.
3. Региональные ограничения — для ru-запросов DDG обычно возвращает ru-результаты без параметров.
