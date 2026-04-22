# External links

## Модель

- **Qwen3-4B-Instruct-2507** — https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507
- GGUF-сборка (unsloth) — https://huggingface.co/unsloth/Qwen3-4B-Instruct-2507-GGUF

## LLM-сервер

- **lemonade-sdk** — https://github.com/lemonade-sdk/lemonade
- Каталог доступных моделей — вывод `lemonade-server-dev pull --help`
- Соседний docker-compose проект — [../../lemonade-server/](../../lemonade-server/)

## Стек

- **openai Python SDK** — https://github.com/openai/openai-python (OpenAI-compatible mode)
- **httpx** — https://www.python-httpx.org/
- **pytest** — https://docs.pytest.org/
- **respx** (httpx mocking) — https://lundberg.github.io/respx/

## Соседние проекты

- [../ai-bot/](../../ai-bot/) — референс по структуре docs/ + рабочий клиент lemonade
- [../local-rag-mcp/](../../local-rag-mcp/) — MCP-based RAG, можно подключить как tool в Sprint 2+
- [../lemonade-server/](../../lemonade-server/) — общий LLM-сервер

## Концепция

- ReAct paper — https://arxiv.org/abs/2210.03629 (Yao et al.)
- karpathy о LLM-coding — https://x.com/karpathy/status/2015883857489522876
- manbot repo (источник структуры docs) — https://github.com/larchanka/manbot

## Инструкции

- [../docs-organization.md](../docs-organization.md) — эталонная инструкция по docs/ этого семейства проектов
