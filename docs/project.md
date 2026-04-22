# ai-agent

Учебный **autonomous AI-agent** с локальной LLM. Принимает задачу пользователя, думает пошагово (`thought → action → observation → …`), вызывает инструменты, завершается `final_answer`.

## Зачем

Дорожная домашка по AI-инфре: показать базовый ReAct-паттерн с JSON-prompting, tool-use и loop-guard на **локальной** модели без внешних API.

## Что внутри

- **Цикл агента:** `src/agent/agent.py` — thought → action → observation, max 8 шагов.
- **3 инструмента:** `calculator` (safe AST-eval), `read_file` (50 KB cap), `http_get` (httpx, 10 s).
- **Строгий JSON-контракт:** LLM обязан отвечать либо `{action, args}`, либо `{final_answer}`. Parser прощает ```json fences``` и free-form preamble.
- **Loop-guard:** повтор одной и той же `(action, args)` подряд → abort.
- **Локальная LLM:** `Qwen3-4B-Instruct-2507-GGUF` через [lemonade-server](../../lemonade-server/) на общей `llm-net`.

## Stack

Python 3.11 · openai SDK (в OpenAI-compat режиме → lemonade) · httpx · pytest + respx · Docker Compose · Makefile.

## Как запустить

```bash
make build
make run TASK='Посчитай (123 + 456) * 2'
```

Подробности — в [ui-kit.md](ui-kit.md) и [testing.md](testing.md).

## Кому

- Разработчику, который хочет увидеть минимальный рабочий ReAct-loop на Python.
- Будущему себе — как отправная точка перед переходом на function-calling API / planner / долгосрочную память.

## Status

Sprint 1 закрыт, MVP loop + 3 tools — зелёный. См. [sprints/sprint-1-delivery.md](sprints/sprint-1-delivery.md) (будет создан при закрытии спринта).
