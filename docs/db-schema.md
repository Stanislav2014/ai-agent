# Data persistence

**Stateless** — персистентного хранилища в Sprint 1 нет.

Во время одного `Agent.run(task)`:

| State | Где живёт | TTL |
|---|---|---|
| `messages[]` (system + user + assistant + tool) | `Agent._loop` local var | жизнь процесса |
| `previous_action` (для loop-guard) | `Agent._loop` local var | одна итерация |
| env settings | `Settings` dataclass | жизнь процесса |
| логи шагов | stdout (terminal) + `docs/dialogs/*.log` при ручном redirect | пока юзер не удалит |

## Planned (Sprint 2+)

- **Conversation log** — JSONL `runs/{timestamp}-{task-slug}.jsonl` с полным history, для offline-анализа.
- **Memory store** — `memory/MEMORY.md` индекс + `memory/<cat>_<name>.md` детали (аналог Claude Code auto-memory).

Оба — файловые, никакой БД.
