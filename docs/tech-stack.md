# Tech stack

## Runtime

| Слой | Версия | Назначение |
|---|---|---|
| Python | 3.11 (Docker image `python:3.11-slim`) | язык агента |
| openai | ≥ 1.40 | SDK в OpenAI-compatible режиме → lemonade |
| httpx | ≥ 0.27 | http_get-tool, sync client с таймаутом |
| lemonade-server | latest (соседний docker-compose проект) | локальный LLM-сервер |
| Qwen3-4B-Instruct-2507-GGUF | Q4_K_M | основная модель |

## Тесты

| Пакет | Версия | Для чего |
|---|---|---|
| pytest | ≥ 8 | runner |
| pytest-mock | ≥ 3 | mocking фикстуры |
| pytest-cov | ≥ 5 | coverage |
| respx | ≥ 0.21 | httpx-mock для http_get |

## Инфра

- Docker Engine + Docker Compose v2
- Общая сеть `llm-net` (external) — агент ↔ lemonade
- Local dev venv через `virtualenv` (у `python3-venv` debian-пакет отсутствует на хосте)

## Environment variables

Файл `.env.example`:

| Переменная | Default | Назначение |
|---|---|---|
| `LLM_BASE_URL` | `http://localhost:8000/api/v1` (host) / `http://lemonade:8000/api/v1` (compose) | OpenAI-compat endpoint |
| `LLM_MODEL` | `Qwen3-4B-Instruct-2507-GGUF` | id модели в lemonade |
| `LLM_API_KEY` | `not-needed` | обязательный параметр SDK, lemonade его игнорирует |
| `LLM_TIMEOUT` | `60` | секунд на один chat.completions запрос |
| `MAX_STEPS` | `8` | верхний предел итераций агента |

## Volumes

| Host path | Container path | Mode | Назначение |
|---|---|---|---|
| `./src` | `/app/src` | ro | hot-reload кода без пересборки |
| `./tests` | `/app/tests` | ro | прогон тестов |
| `./workspace` | `/workspace` | ro | тестовые файлы для tool `read_file` |
| `./docs/dialogs` | `/app/dialogs` | rw | сохранение логов прогонов |
