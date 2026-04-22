# Roadmap

## Phase A — Sprint 1 (MVP) ✅

- D-01: MVP agent loop + 3 tools + Docker compose wrapper

## Phase B — Memory & history

- B-01: file-backed conversation log (append-only JSONL)
- B-02: простая long-term memory через `MEMORY.md`-подобный индекс + `read_file`/`write_file` tool

## Phase C — Planner

- C-01: `planner` шаг перед executor'ом (LLM предлагает план действий → agent прогоняет по нему)
- C-02: tool selection через embedding + similarity (вместо хардкода в реестре)

## Phase D — Integrations & UX

- D-02: streaming ответов модели с CLI spinner'ом
- D-03: web search tool (DuckDuckGo/Brave) с кэшем
- D-04: native function-calling API lemonade (если уедет на OpenAI-совместимый) вместо JSON-prompting
- D-05: HTTP-обёртка (FastAPI) для агента как сервиса

## Out of scope (никогда)

- Облачные API (OpenAI/Claude/Gemini) — проект принципиально локальный
- Stateful tool sessions (shell с history и т.п.) — по задаче, без persistent state
