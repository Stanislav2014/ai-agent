# Sprint 2 — delivery · 2026-04-22 → 2026-04-23

**Goal:** расширить агента поиском в интернете и оптимизацией HTML-ответов; оформить post-sprint-1 правки как полноценные задачи.
**Outcome:** ✅ Closed on 2026-04-23.

---

## Что доехало

| Task | Артефакты | Acceptance |
|---|---|---|
| D-02 | `web_search` (DuckDuckGo HTML), `_html_to_markdown` в `http_get`, `+9` юнитов, deps `bs4`/`markdownify` | [test4-web-search.log](../dialogs/test4-web-search.log) — 1 search, 5 источников, 29.6 s |
| D-03 | CLI `--model` + Makefile `MODEL=`, `+1` юнит | в header live-прогона печатается `Model: <выбранная>` |
| D-04 | Замеры `perf_counter` вокруг llm/tool, новый формат заголовка шага и `Total:` футер, `+1` юнит | [test5-timings.log](../dialogs/test5-timings.log) — Step1=15.06s vs Step2=1.28s (KV-cache хит) |
| D-05 | Makefile `SAVE=1` → `tee` в `docs/dialogs/run-<ts>.log`; файлы вне git | smoke `make run TASK='9*9' SAVE=1` создал лог, `git status` его не видит |

**Итог:** 58 unit + 3 integration зелёных. Репозиторий public: https://github.com/Stanislav2014/ai-agent.

---

## Архитектурные изменения

- **4-й инструмент** (`web_search`) встал в существующую архитектуру `Executor` + `_TOOL_DOCS` без правок `agent.py`/`parser.py` — подтверждена изоляция, заложенная в Sprint 1.
- **Pipeline для HTML:** в `http_get` теперь по `Content-Type` ветвится — HTML стрипается (`script/style/nav/header/footer/aside/svg/form`) → берётся `<main>`/`<article>`/`<body>` → `markdownify` → cap 5 KB. JSON / plaintext проходят без изменений.
- **Settings overlay через `dataclasses.replace()`** — CLI-флаги `--model` / `--max-steps` создают immutable копию `Settings` с подменёнными полями. Без env-мутаций.
- **Тайминги через `time.perf_counter()`** — замеры вокруг `llm.chat()` и `executor.execute()` отдельно, чтобы видеть, где провисает.
- **Run logs out-of-git** — acceptance-снимки `test*-*.log` остаются в репо; ad-hoc прогоны через `SAVE=1` идут в `run-*.log` и игнорируются.

---

## Acceptance артефакты

- [docs/dialogs/test4-web-search.log](../dialogs/test4-web-search.log) — D-02
- [docs/dialogs/test5-timings.log](../dialogs/test5-timings.log) — D-04

(D-03 и D-05 без отдельного acceptance-снимка; верифицированы smoke-прогоном.)

---

## Что улучшили в процессе

- Параллельные `make run` с разными `MODEL=` устроили шторм перезагрузок весов в lemonade (`Loading llm: 4B → 8B → 4B`) — сериализатор инференса не любит такого. Теперь правило: один прогон за раз. Вынесено в Sprint 3 backlog как кандидат на `bench.sh` (D-08).
- HTML→MD pipeline хорош для веб-страниц, но лишний для JSON-API. Текущая эвристика по `Content-Type` пока справляется — если проявится контр-пример, оформим флаг.
- 8B-модель таймаутила на 60 s из-за prefill длинного системного промпта. Подняли `LLM_TIMEOUT=180`. Обнажилась идея D-06 — токены показать; реализовано в Sprint 3.

---

## Уехало в Sprint 3+

- Native function calling API вместо JSON-prompting (D-04 старого backlog'а, переименовать).
- Долгосрочная память агента (B-01 / B-02 в roadmap).
- Streaming inference (раньше D-02, переименовать).
- Двойная обёртка `final_answer` у 0.6B — задокументировано в `legacy-warning.md`, fix отложен до Sprint 3 (D-09).

---

## Sprint close checklist

- [x] history из блоков `change-request.md` уже в `tasks/D-XX_*.md` → `## History` каждой спеки.
- [x] `sprints/sprint-2-archive.md` создан (frozen snapshot).
- [x] `sprints/sprint-2-delivery.md` (этот файл).
- [x] `sprints/current-sprint.md` обновлён под Sprint 3.
- [x] `change-request.md` обнулён до Sprint 3.
- [x] `prompts/prompts-sprint-2.md` создан с аннотированной хроникой.
- [x] `tasks.md` пополнен D-02..D-05.
- [x] `legacy-warning.md` обновлён.
