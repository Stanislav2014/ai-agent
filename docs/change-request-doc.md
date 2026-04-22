# Change Request — TEMPLATE (один блок задачи)

> 📋 Шаблон блока. Реальные данные — в [change-request.md](change-request.md). При старте новой задачи добавлять блок, а не заменять файл. После merge — оставить блок со статусом `Merged` до закрытия спринта.

---

## Метадата

| Поле | Значение |
|---|---|
| **Task ID** | `{PREFIX}-{NN}` |
| **Branch** | `{type}/{slug}` |
| **Task spec** | `docs/tasks/{PREFIX}-{NN}_*.md` |
| **Started** | YYYY-MM-DD |
| **Status** | `To Do` / `In Progress` / `In Review` / `Merged` |
| **Owner** | handle |

---

## Goal

Одно предложение — что именно должно измениться и почему.

## Success criteria (verifiable)

- [ ] Критерий 1 → verify: {как проверить}
- [ ] Критерий 2 → verify: {как проверить}

---

## Scope

### In scope
### Out of scope

---

## Impact / change surface

### Изменяемые файлы
| Файл | Характер изменений |
|---|---|

### Затронутые потоки (из [context-dump.md](context-dump.md))

---

## Uncertainty list

1. **Вопрос** — текущее понимание / варианты

---

## Pending action items

- [ ] **A1**: описание · verify: {критерий}

---

## TDD phases

### Phase 0 — Research
### Phase 1 — Core
### Phase 2 — UI
### Phase 3 — Gating
### Phase 4 — Testing
### Phase 5 — Review & docs

---

## Regression watch

---

## Checkpoints

### Phase 0 checkpoint
### Phase 1 checkpoint
### Phase 4 checkpoint

---

## History

- YYYY-MM-DD — started
- YYYY-MM-DD — merged (commit …)
