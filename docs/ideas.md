# Ideas — raw backlog

Сырые идеи, ещё не превращённые в задачи.

## Tools

- **`web_search`** — DuckDuckGo-HTML парсер как альтернатива закрытым API; кэшировать запросы по hash.
- **`shell`** — выполнение `subprocess` с whitelisted-командами (ls, cat, grep). Опасно без sandboxing, отложить.
- **`rag_lookup`** — интеграция с `local-rag-mcp` соседом по `llm-net`: tool зовёт MCP, получает top-k chunks.
- **`write_file`** — opposite of `read_file`, для сохранения intermediate результатов. Cap размера + `/workspace` only.

## Loop

- **Fallback modes** при `LLMError` — попробовать вторую модель (`Qwen3-0.6B` для быстрого ответа, `Qwen3-8B` для сложной задачи).
- **Tree-of-thoughts** — параллельно N ветвей, self-consistency vote.
- **Reflexion** — после fail-а агент пишет post-mortem и перезапускает с ним в контексте.

## UX

- Цветной CLI-вывод (thought — dim, action — bold, observation — cyan).
- TUI через `textual` с отдельными панелями для history/step/tools.
- Export прогона в markdown-отчёт для PR-артефактов.

## Integration

- Telegram-bot обёртка, reuse `ai-bot`-инфра.
- Prometheus-метрики (steps, tool calls, latency) через `/metrics` endpoint.
