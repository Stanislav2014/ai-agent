# Contract — lemonade-server

OpenAI-compatible локальный LLM-сервер. Единственный внешний зависимый сервис на этапе Sprint 1.

## Эндпоинт

- Из контейнера agent на `llm-net`: `http://lemonade:8000/api/v1`
- С хоста: `http://localhost:8000/api/v1`

## Используемые операции

### `GET /api/v1/models`

Discovery — список моделей (используется только вручную при дебаге).

### `POST /api/v1/chat/completions`

Единственная операция в runtime агента. Совместимый с OpenAI формат.

**Request (наш payload):**
```json
{
  "model": "Qwen3-4B-Instruct-2507-GGUF",
  "messages": [
    {"role": "system",    "content": "..."},
    {"role": "user",      "content": "..."},
    {"role": "assistant", "content": "..."},
    {"role": "tool",      "content": "..."}
  ],
  "temperature": 0.2
}
```

**Response (relevant поля):**
```json
{
  "choices": [
    {"message": {"role": "assistant", "content": "<raw string from LLM>"}}
  ]
}
```

## Наши ожидания

- `choices[0].message.content` — строка с валидным JSON (по нашему system-prompt); parser допускает мусор вокруг/fences.
- Ошибки сети/таймаут маппятся openai SDK в `APIConnectionError`/`APITimeoutError` → наш `LLMError`.

## Лимиты и нагрузка

- Inference **сериализуется** в lemonade (CPU-backend), другие клиенты (ai-bot, rag-mcp) могут встать в очередь → latency может вырасти.
- По умолчанию таймаут клиента 60 s (`LLM_TIMEOUT` env). Для cold-start модели на 4B-параметров 60 s хватает.
- Auth: нет. API-key SDK требует формально (`not-needed`).

## Аутентификация

Нет. Сервер слушает только на `llm-net` (изолированная docker-сеть) и localhost.

## Как запустить сервер

См. [../../../lemonade-server/README.md](../../../lemonade-server/README.md):

```bash
cd ~/Projects/ai-project-grow/lemonade-server
make network     # один раз
make up
make pull-models # если модель ещё не подтянута
docker compose exec lemonade lemonade-server-dev pull Qwen3-4B-Instruct-2507-GGUF
```
