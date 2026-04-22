# Workflow

Процесс ведения задач в `ai-agent`. Основан на `ai-bot/docs/instructions.md` (TDD + manbot-style kanban + karpathy-guidelines).

## 1. Task prefixes

| Префикс | Когда |
|---|---|
| **A-** | Критичные дефекты (P0/P1) |
| **B-** | Исправленные баги (история) |
| **C-** | Технический долг |
| **D-** | Фичи / enhancements |

Имя файла: `{PREFIX}-{NN}_{SLUG}.md` (без ticket-id — в учебном проекте внешнего трекера нет). Пример: `D-01_MVP_AGENT_LOOP.md`.

## 2. Branch naming

| Префикс | Когда |
|---|---|
| `feature/BAU/{slug}` | фичи < 20 раб. дней |
| `feature/CR/{slug}` | фичи > 20 раб. дней |
| `feature/TD/{slug}` | тех-долг |
| `bugfix/{slug}` | дефекты |

## 3. Жизненный цикл задачи

1. **Создание**
   - Блок в [change-request.md](change-request.md) по шаблону [change-request-doc.md](change-request-doc.md).
   - Строка в [tasks.md](tasks.md).
   - Перенести в [sprints/current-sprint.md](sprints/current-sprint.md) → `To Do`.
   - Спека `docs/tasks/{PREFIX}-{NN}_*.md` — единая точка истины.
   - ⚠ Не использовать `docs/superpowers/specs/` для новых задач — там архив MVP-дизайна.

2. **Research** — grep кодбейза, git log затрагиваемых файлов, смежные задачи.

3. **Implementation (TDD phases)**
   - Phase 0: Research
   - Phase 1: Core changes
   - Phase 2: UI (если применимо)
   - Phase 3: Gating / error handling
   - Phase 4: Testing (unit + integration smoke)
   - Phase 5: Review & docs
   - Checkpoint в конце каждой фазы.

4. **TDD на каждое изменение**
   - RED → падающий тест
   - GREEN → минимальный код
   - REFACTOR → SOLID/DRY/KISS, без расширения scope
   - НЕ батчить тесты в конец задачи.

5. **Commit & merge** — один коммит = одна логическая единица. Merge после `make test` + `make test-int`.

6. **Post-merge**
   - История в спеку.
   - ✅ в [tasks.md](tasks.md), `Done` в `current-sprint.md`.
   - Обновить статус блока в `change-request.md` на Merged (не удалять).
   - Обновить [legacy-warning.md](legacy-warning.md), если изменился тех-долг.

7. **Sprint close** — history из блоков → в `tasks/*.md` §History; создать `sprints/sprint-N-delivery.md` + `-archive.md`; очистить `change-request.md`; добавить `prompts/prompts-sprint-N.md`.

## 4. TDD — mandatory

Каждая строка production-кода покрыта тестом, написанным **до** неё.

Исключения: Dockerfile / Makefile / CI, trivial dataclass без логики, тест-фикстуры.

## 5. Karpathy guidelines

Активная skill: `~/.claude/plugins/cache/andrej-karpathy-skills/andrej-karpathy-skills/1.0.0/skills/karpathy-guidelines/SKILL.md`.

1. **Think before coding** — surface assumptions, ask when unclear.
2. **Simplicity first** — ноль speculative features.
3. **Surgical changes** — менять только необходимое.
4. **Goal-driven execution** — verifiable success criteria, loop до зелёного.

## 6. Комментарии в коде

- **Дефолт — не писать**. Имена объясняют WHAT.
- Пишем только когда WHY не-очевидно (hidden constraint, workaround, subtle invariant).
- **НЕ** писать в коде: ticket-id, «used by X», даты, описания задач — гниёт.

## 7. Verification before claiming done

1. `make test` — все unit зелёные.
2. `make test-cov` — coverage ≥ 85 %.
3. `make test-int` (если lemonade локально поднят) — три интеграционных теста проходят.
4. `make build` — образ собирается.
5. Checkpoint в task spec.

## 8. Memory between sessions

Файл `~/.claude/projects/-home-stan-Projects-ai-project-grow-ai-agent/memory/MEMORY.md` + `<category>_<name>.md`.

После задачи с любым non-obvious инсайтом — добавить memory (например, root cause бага, решение, fact о внешней системе).
