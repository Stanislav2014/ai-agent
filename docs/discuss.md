# Open questions

Вопросы, которые пока не закрыты — требуют решения перед соответствующей задачей.

## JSON-prompting vs native function calling

**Контекст:** сейчас мы просим модель отвечать строго в JSON-схеме через system prompt. Lemonade/llama.cpp поддерживает OpenAI-compatible function calling (tools param), который парсит сам сервер.

**Tradeoff:**
- JSON-prompting — работает везде, одна логика на все бэкенды, но хрупкий (модель может нарушить).
- Function calling — серверная валидация, меньше retry, но завязка на конкретную реализацию.

**Решение:** оставляем JSON-prompting в Sprint 1. Переход — D-04 (Sprint 2+).

## Размер контекста при долгих сессиях

**Контекст:** observation's обрезаются до 4 KB, но после 5-7 шагов контекст всё равно растёт до 10-20 KB — близко к лимиту prompt'а для 4B-модели.

**Варианты:**
- A. Summarize старые шаги (extra LLM call).
- B. Drop-oldest — выкидывать самый старый `tool` observation когда превышаем N шагов.
- C. Ничего не делать, положиться на MAX_STEPS=8.

**Текущее:** C. Возвращаться к A/B, когда появятся задачи, требующие > 8 шагов.

## Tool-selection через embeddings

**Контекст:** когда tool'ов станет 10+, их полный список в system prompt начнёт отъедать контекст.

**Варианты:**
- Ретривер по task → top-k tool-descriptions → только их в prompt.
- MCP-подход — tools describe себя через `/list_tools`, агент опрашивает динамически.

**Решение:** отложить до C-02.

## Где запускать: хост vs Docker

**Контекст:** `python3-venv` недоступен на хосте, venv делается через `virtualenv`. Docker — официальный способ деплоя, но его dev-loop медленнее (перестройка слоёв).

**Решение:** dev через `virtualenv + .venv/bin/pytest`, production/acceptance — через Docker compose. `make venv` + `make test` в контейнере покрывают оба.
