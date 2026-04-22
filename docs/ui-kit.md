# UI kit — CLI

Интерфейс единственный — CLI, запускается через `python -m agent` или `make run`.

## Команды

| Команда | Делает |
|---|---|
| `make network` | Создаёт общую docker-сеть `llm-net` (идемпотентно) |
| `make build` | Собирает образ `ai-agent:latest` |
| `make run TASK="<текст>"` | Одноразовый прогон агента с задачей |
| `make test` | `pytest tests/unit -v` внутри контейнера |
| `make test-int` | `pytest tests/integration -v` (требует живой lemonade) |
| `make test-cov` | unit-тесты с coverage-репортом |
| `make shell` | bash внутри контейнера |
| `make clean` | down + remove image |
| `make venv` | локальный `virtualenv .venv` для dev на хосте |

## Формат вывода агента

```
Task: <task text>
Model: Qwen3-4B-Instruct-2507-GGUF @ http://lemonade:8000/api/v1

[Step 1]
Thought: <reasoning from model>
Action: <tool name>
Args: {<k>: <v>, ...}
Observation: <tool result, possibly truncated>

[Step 2]
Final: <final answer>

=== ANSWER ===
<final answer>
```

## Exit codes

| Code | Когда |
|---|---|
| `0` | Агент вернул `final_answer` |
| `1` | Агент упёрся в `MAX_STEPS` либо loop-guard |
| `2` | `LLMError` (сеть/таймаут/пустой ответ модели) |

## Args

```
ai-agent [-h] [--max-steps MAX_STEPS] task
```

| Аргумент | По умолчанию | Описание |
|---|---|---|
| `task` (позиционный) | — | Текст задачи |
| `--max-steps` | `$MAX_STEPS` (8) | override лимита шагов |

## Примеры из ТЗ

```bash
make run TASK='Посчитай (123 + 456) * 2'
make run TASK='Прочитай файл /workspace/test.txt и скажи сколько в нём строк'
make run TASK='Сделай GET запрос к https://api.github.com и верни HTTP статус-код'
```

Готовые логи — в [dialogs/](dialogs/).
