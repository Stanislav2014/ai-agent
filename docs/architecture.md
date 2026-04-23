# Architecture

## 1. Top-level flow

```
user task
   │
   ▼
CLI (__main__.py) ──┐
                    ▼
           ┌──────────────┐      messages[]     ┌──────────────┐
           │    Agent     │◀────────────────────│ LLMProvider  │
           │  (agent.py)  │     raw JSON        │   (llm.py)   │
           └──┬────────▲──┘                     └──────┬───────┘
              │        │ observation                   │
              ▼        │                               │ openai SDK
      ┌───────────┐    │                               ▼
      │  parser   │────┘                         lemonade-server
      │ JSON+fix  │                              Qwen3-4B-Instruct
      └───────────┘
              │ dict(action, args)
              ▼
      ┌──────────────┐       ┌────────────────────┐
      │   Executor   │──────▶│   tools.py         │
      │ executor.py  │       │  calculator        │
      └──────────────┘       │  read_file         │
                             │  http_get ─┐       │
                             │  web_search│       │
                             └────────────┼───────┘
                                          │
                                          ▼ (если Content-Type=html)
                                   _html_to_markdown
                                   (bs4 → markdownify)
```

## 2. Цикл агента

```
init: messages = [system-prompt(tools_desc), user(task)]
for step in 1..MAX_STEPS:
    raw = llm.chat(messages)
    try: data = parser.parse_llm_response(raw)
    except ParseError: append retry-hint tool msg, continue
    messages += assistant(raw)
    if final_answer: return it
    if action == previous_action: return "Loop detected, abort."
    observation = executor.execute(action, args)
    messages += tool(observation)
return "Не удалось решить за отведённое количество шагов"
```

## 3. Компоненты и их границы

| Модуль | Входы | Выходы | Изолирован от |
|---|---|---|---|
| `llm.py` | `messages[]` | `raw content (str)` или `LLMError` | парсера, executor'а, tools |
| `parser.py` | `raw (str)` | `dict` с `final_answer` или `action`+`args` | LLM, executor'а |
| `tools.py` | prim args | `str` или `ToolError` | всех остальных |
| `executor.py` | `(name, args)` | `observation (str)` — ошибки превращает в `"Error: …"` | LLM, парсера |
| `agent.py` | `task (str)` | `answer (str)` | CLI |
| `__main__.py` | `argv` | exit code + stdout | всего остального |

Unit-тесты каждого модуля не трогают соседей (LLM везде замокан).

## 4. JSON-контракт с моделью

**Input (system + user + optional tool observations):**

Модель видит системный промпт с жёстко описанным форматом (см. `prompts.py`). Описание инструментов генерится `Executor.describe()` и подставляется в `{{TOOLS_DESCRIPTION}}`.

**Output (обязательно один из двух):**

```json
{"thought": "…", "action": "calculator", "args": {"expression": "1+2"}}
{"final_answer": "3"}
```

Парсер допускает:
- мусор до/после JSON
- обёртку в ` ```json … ``` `
- отсутствие `thought` / `args` (подставляется пустая строка / `{}`)

Если LLM вернул оба ключа — приоритет у `final_answer` (agent стопает рано).

## 5. Edge cases

1. **LLM вернул текст с ```json fences```** → parser снимает fences и всё равно парсит.
2. **LLM вернул не-JSON (объяснение словами)** → `ParseError` → в history добавляется `tool`-сообщение с подсказкой «respond STRICTLY in JSON», агент получает следующую попытку. Retry учитывается в MAX_STEPS.
3. **LLM зациклился: одинаковая `(action, args)` два раза подряд** → `LOOP_ABORT_MESSAGE`, exit 1. Сравнение через `json.dumps(args, sort_keys=True)` — устойчиво к перестановке ключей.
4. **LLM галлюцинирует имя tool'а** → Executor возвращает `"Error: unknown tool 'X'. Available: [...]"` — агент видит и может исправиться на следующем шаге.
5. **`args` отсутствуют / `null`** → передаём `{}` в tool, если у функции нет обязательных kwargs — вернёт `TypeError` → Executor отдаст `"Error: invalid args …"`.
6. **Observation > 4 KB** → обрезаем до `4000` + суффикс `...[truncated]` перед добавлением в history (защита от раздувания контекста).
7. **`read_file` получил > 50 KB** → обрезаем до 50 KB + `...[truncated]`.
8. **`http_get` получил > 5 KB body** → обрезаем до 5 KB; статус-строка + body.
9. **`http_get` получил не-http(s) URL (file://, ftp://)** → `ToolError`, не ходим.
10. **`http_get` timeout (>10s)** → `ToolError` → Executor возвращает observation `"Error: request timed out…"`.
11. **Lemonade вернул пустой `content`** → `LLMError` на уровне `LLMProvider`, CLI печатает stderr и возвращает exit 2.
12. **Lemonade недоступен (порт не отвечает)** → `LLMError` (APIConnectionError). Integration-тест через `socket.create_connection` превентивно `skip`-ает.
13. **Calculator получил `__import__('os')`** → AST-walk белого списка (Constant/BinOp/UnaryOp/Num) отклоняет → `ToolError`.
14. **Calculator: деление на ноль** → `ToolError` с понятным сообщением (не крашит процесс).
15. **Запуск без `llm-net` network** → Docker compose падает на старте. `make network` идемпотентно создаёт её. Запуск lemonade и ai-agent в любом порядке.
16. **`web_search`: DDG вернул 0 результатов** → возвращаем литерал `"No results."`, агент видит это как observation и может переформулировать запрос.
17. **`web_search`: DDG timeout / блокировка UA** → `ToolError("search timed out …")` / `"search HTTP error: …"` → Executor превратит в `"Error: …"` observation, агент выбирает другой путь или сдаётся.
18. **`http_get`: Content-Type HTML** → пайплайн `bs4` удаляет `script/style/nav/header/footer/aside/svg/form`, берёт `<main>`→`<article>`→`<body>`, `markdownify` переводит в MD, коллапс пустых строк. Экономит до 80 % токенов по сравнению с сырым HTML.
19. **Несколько инстансов агента подряд с разной моделью** → lemonade сериализует инференс и перезагружает GGUF при смене модели (десятки секунд). Рекомендация: фиксировать `LLM_MODEL` для серии прогонов.

## 6. Почему такое разбиение

- **Parser и Executor полностью изолированы от LLM и друг от друга** — можно поменять модель, тулы, транспорт независимо.
- **Agent ничего не знает про конкретные tool-имена** — описание идёт в системный промпт через `Executor.describe()`, а возврат ошибки позволяет модели исправиться без хардкода.
- **Tools — чистые функции** — легко тестировать, стабильный контракт `(**kwargs) → str`.
- **Ошибки tool'ов становятся observation'ами**, а не падениями — это и есть основной способ, которым агент учится на прошлых шагах.
