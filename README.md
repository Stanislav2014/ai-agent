# ai-agent

Минимальный autonomous AI-агент на локальной LLM (Qwen3-4B через [lemonade-server](../lemonade-server/)).

- JSON-prompting loop (`thought → action → observation → …`)
- Три инструмента: `calculator`, `read_file`, `http_get`
- `MAX_STEPS=8` + loop-guard
- Docker compose на общей `llm-net`
- 47 unit + 3 integration tests, coverage 85 %

## Быстрый старт

```bash
# однажды
make network

# собрать и прогнать
make build
make run TASK='Посчитай (123 + 456) * 2'
```

(Lemonade-server должен быть поднят: `cd ../lemonade-server && make up`.)

## Примеры

```bash
make run TASK='Посчитай (123 + 456) * 2'
make run TASK='Прочитай файл /workspace/test.txt и скажи сколько в нём строк'
make run TASK='Сделай GET запрос к https://api.github.com и верни HTTP статус-код'
```

Логи трёх прогонов — в [docs/dialogs/](docs/dialogs/).

## Тесты

```bash
make test        # 47 unit в контейнере
make test-cov    # с coverage
make test-int    # 3 integration против live lemonade
```

## Структура

- **`src/agent/`** — код агента (8 модулей: llm, tools, executor, parser, agent, prompts, config, __main__).
- **`tests/unit/`** и **`tests/integration/`** — pytest.
- **`docs/`** — полная док-структура по [docs-organization.md](docs-organization.md).
- **`workspace/`** — тестовые файлы для tool `read_file`.
- **`Dockerfile` / `docker-compose.yml` / `Makefile`** — обёртка.

## Документация

Всё в [docs/](docs/). Точка входа: [docs/README.md](docs/README.md).

- [docs/project.md](docs/project.md) — обзор
- [docs/architecture.md](docs/architecture.md) — loop + edge cases
- [docs/tasks/D-01_MVP_AGENT_LOOP.md](docs/tasks/D-01_MVP_AGENT_LOOP.md) — спека задачи
- [docs/superpowers/specs/2026-04-21-mvp-agent-loop-design.md](docs/superpowers/specs/2026-04-21-mvp-agent-loop-design.md) — утверждённый дизайн

## Модель

- `Qwen3-4B-Instruct-2507-GGUF` (Q4_K_M) через lemonade-server
- Переключить можно через env: `LLM_MODEL=<другая_из_каталога_lemonade>`

## Дерево

```
ai-agent/
├── src/agent/           # ядро
├── tests/               # 47 unit + 3 integration
├── workspace/test.txt   # fixture для read_file
├── docs/                # full spec/docs per docs-organization.md
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── pyproject.toml
└── README.md
```
