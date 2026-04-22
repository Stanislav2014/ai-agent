# Инструкция по организации docs/ для нового проекта

Скопировать/адаптировать в любой новый проект в `ai-project-grow/`. Основано на структуре ai-bot (Sprint 1, 2026-04-17). Вдохновлено [manbot](https://github.com/larchanka/manbot) + TDD + karpathy-guidelines.

**Философия**: one-stop docs директория с чёткими ролями файлов. Каждый тип информации имеет **единственное место**. Ничего не дублируется (кроме change-request.md, который зеркалит sprint).

---

## 1. Структура директории

```
docs/
├── README.md                  # Индекс всех docs-файлов (таблица файл → назначение)
│
├── project.md                 # Обзор проекта на 1 экран (что, зачем, кому, stack)
├── instructions.md            # Workflow: task lifecycle, branch naming, TDD, commit rules
├── plan.md                    # Roadmap по фазам (A/B/C/D)
├── ideas.md                   # Копилка идей (ещё не задачи)
├── discuss.md                 # Открытые архитектурные/продуктовые вопросы
│
├── tasks.md                   # Master-каталог всех задач по фазам
├── tasks/                     # Детальные спеки задач, один файл = одна задача
│   └── {PREFIX}-{NN}_{TICKET}_{SLUG}.md
│
├── change-request.md          # Зеркало текущего спринта (все активные задачи блоками)
├── change-request-doc.md      # Шаблон одного блока для change-request.md
│
├── architecture.md            # Архитектурные паттерны + раздел "Edge cases" (обязательно)
├── context-dump.md            # Карта всех flows с file:line ссылками
├── tech-stack.md              # Зависимости/версии/env переменные
├── db-schema.md               # Состояние хранения данных
├── ui-kit.md                  # UI-интерфейс (команды / страницы / компоненты)
├── testing.md                 # Фреймворки, fixtures, команды прогона
├── legacy-warning.md          # Тех-долг / костыли / known issues (с приоритетами 🔥⚠🧟)
├── links.md                   # Внешние ссылки (доки стека, репо, соседние проекты)
│
├── contracts/                 # Внешние интерфейсы
│   ├── README.md              # Индекс контрактов
│   └── external/
│       └── {system}.md        # По одному файлу на внешний сервис
│
├── sprints/                   # Закрытые и текущий спринты
│   ├── current-sprint.md      # Kanban текущей итерации (To Do / In Progress / Done)
│   ├── sprint-N-delivery.md   # Финальный delivery-документ спринта N
│   ├── sprint-N-archive.md    # Замороженный change-request на момент закрытия
│   └── sprint-N-summary.md    # Человеческим языком, TL;DR по спринту (опционально)
│
├── prompts/                   # История промптов к AI-агенту
│   ├── prompts.md             # Пред-спринтовые / MVP-промты
│   └── prompts-sprint-N.md    # Промты за спринт N (хронологически)
│
├── dialogs/                   # Скриншоты живых диалогов/UI — acceptance artifacts
│   └── README.md              # Объяснение что на каждом скриншоте
│
└── superpowers/               # Архив MVP-дизайна (не расширяется новыми задачами)
    └── specs/
```

---

## 2. Роли файлов — что куда писать

| Вопрос | Куда |
|--------|------|
| «Что это за проект на 1 экран?» | `project.md` |
| «Как работать над задачей?» | `instructions.md` |
| «Что планируем в следующих фазах?» | `plan.md` |
| «Какие есть сырые идеи?» | `ideas.md` |
| «Какой архитектурный вопрос открыт?» | `discuss.md` |
| «Список всех задач?» | `tasks.md` (обзорная таблица) |
| «Детали конкретной задачи?» | `tasks/{PREFIX}-{NN}_*.md` |
| «Что в работе сейчас?» | `sprints/current-sprint.md` + `change-request.md` |
| «Как устроена архитектура?» | `architecture.md` |
| «Где в коде какая логика?» | `context-dump.md` |
| «Какие env-переменные?» | `tech-stack.md` |
| «Какие известные проблемы?» | `legacy-warning.md` |
| «Что в SQL/YAML хранится?» | `db-schema.md` |
| «Какие команды/страницы у юзера?» | `ui-kit.md` |
| «Как запустить тесты?» | `testing.md` |
| «Внешние API, которые дёргаем?» | `contracts/external/{system}.md` |
| «История промптов к AI-агенту?» | `prompts/prompts-sprint-N.md` |
| «Итог закрытого спринта?» | `sprints/sprint-N-delivery.md` + `-summary.md` |

---

## 3. Жизненный цикл задачи (из instructions.md)

### Task prefixes
- **A-** — критичные дефекты (P0/P1)
- **B-** — исправленные баги (история)
- **C-** — технический долг
- **D-** — фичи / enhancements

### Branch naming
- `bugfix/{ticket}` — дефекты
- `feature/BAU/{ticket}` — фичи < 20 раб. дней
- `feature/CR/{ticket}` — фичи > 20 раб. дней
- `feature/TD/{ticket}` — тех-долг

### 7 шагов жизни задачи

1. **Создание** — блок в `change-request.md` (по шаблону `change-request-doc.md`) + строка в `tasks.md` + в `current-sprint.md` «To Do» + спека в `tasks/{PREFIX}-{NN}_*.md`.
2. **Research** — grep кодбейза, git log, собрать Uncertainty и Action items.
3. **Implementation (TDD phases)** — Phase 0 Research, 1 Core, 2 UI, 3 Gating, 4 Testing, 5 Docs. В конце каждой фазы — checkpoint в спеке.
4. **TDD-цикл** — RED (падающий тест) → GREEN (минимум кода) → REFACTOR (SOLID/DRY без расширения scope). **НЕ батчить** тесты в конец.
5. **Commit & merge** — один коммит = одна логическая единица, осмысленное сообщение. Merge только при зелёных тестах + линте.
6. **Post-merge** — history в спеку, ✅ в `tasks.md`, `Done` в `current-sprint.md`, обновить статус блока в `change-request.md` на **Merged** (не удалять!), обновить `legacy-warning.md` если тех-долг изменился.
7. **Sprint close** — history из change-request переезжает в `## History` секции task-спек, change-request обнуляется под следующий спринт. Создаётся `sprints/sprint-N-delivery.md` + опц. `sprint-N-summary.md`.

---

## 4. Ключевые конвенции

- **change-request.md — зеркало спринта**, не single-task tracker. Блок каждой задачи сохраняется до закрытия спринта, только статус меняется. Не очищать после merge одной задачи.
- **Одна задача — один файл** в `tasks/`. Design + план + история — всё в одном спек-файле.
- **Архив `superpowers/specs/`** — только оригинальный MVP-дизайн. Новые задачи сюда не пишутся.
- **Комментарии в коде** — дефолт не писать. Только когда WHY неочевидно (hidden constraint, workaround, subtle invariant). НЕ писать ticket-id, «used by X», описания задач — живёт в git log / task spec.
- **Success criteria — verifiable**. Каждый критерий должен иметь тест или чёткий способ ручной верификации.
- **Legacy-warning приоритеты** — 🔥 критично, ⚠ архитектурное, 🧟 стилистическое. Отмечать ✅ РЕШЕНО при закрытии, не удалять — как история решений.
- **TDD mandatory** — тест до кода. Исключения: скрипты деплоя, Makefile, CI, trivial DTO.

---

## 5. Recipe — развернуть структуру в новом проекте

```bash
# 1. Создать скелет
cd <new-project>
mkdir -p docs/{tasks,contracts/external,sprints,prompts,dialogs,superpowers/specs}

# 2. Скопировать шаблонные/рекомендованные файлы из ai-bot
AI_BOT=~/Projects/ai-project-grow/ai-bot
cp $AI_BOT/docs/instructions.md docs/          # Workflow (адаптировать под стек)
cp $AI_BOT/docs/change-request-doc.md docs/    # Шаблон блока задачи
cp $AI_BOT/docs/README.md docs/README.md       # Индекс — переписать под проект

# 3. Создать пустые каркасы для остальных файлов
touch docs/{project,plan,ideas,discuss,tasks,change-request,architecture,context-dump,tech-stack,db-schema,ui-kit,testing,legacy-warning,links}.md
touch docs/sprints/current-sprint.md
touch docs/contracts/README.md
touch docs/dialogs/README.md

# 4. Первое заполнение
# - docs/project.md      → обзор проекта на 1 экран
# - docs/tech-stack.md   → зависимости, env
# - docs/architecture.md → высокоуровневая диаграмма + раздел "Edge cases"
# - docs/README.md       → актуализировать индекс
# - docs/instructions.md → адаптировать workflow (branch naming, TDD исключения)
```

---

## 6. Как писать архитектуру (самое важное)

`architecture.md` — не только «схема и паттерны», но и **обязательный раздел Edge cases** с нумерацией. Пример из ai-bot:

> ### 9. Startup race: polling начинается раньше чем Lemonade готов
> Lemonade теперь в отдельном docker-проекте, `depends_on` не применим. Если ai-bot поднят, а Lemonade-контейнер ещё грузит модель — первый запрос вернёт ошибку. Бот переживёт через graceful error, повтор сработает. Порядок запуска: сначала lemonade-server, потом ai-bot.

Это пишется **по мере обнаружения** — при работе над каждой задачей думать «а что может сломаться на стыке» и добавлять edge case. Через 10 задач — 10+ edge cases, которые реально помогут новичку.

---

## 7. Sprint close checklist

При закрытии спринта сделать **в указанном порядке**:

1. Переместить `history` из блоков `change-request.md` в соответствующие `tasks/{PREFIX}-*.md` → раздел `## History`.
2. Создать `sprints/sprint-N-archive.md` — копия `change-request.md` на момент закрытия (frozen snapshot).
3. Создать `sprints/sprint-N-delivery.md` — live-документ с архитектурой, примерами, deliverables, acceptance-артефактами.
4. (Опционально) Создать `sprints/sprint-N-summary.md` — TL;DR человеческим языком.
5. Обновить `sprints/current-sprint.md`: либо закрыть (заголовок «Sprint N закрыт YYYY-MM-DD» + пустые секции под следующий), либо пересоздать под новый спринт.
6. Обнулить `change-request.md`: оставить только шапку «Sprint (N+1) · TBD» и пустые секции.
7. Добавить `prompts/prompts-sprint-N.md` — хронологический архив промтов за спринт. Короткие ответы (`да`/`A`/`B`/`приступай`) **аннотировать**: что предлагал агент в варианте A/B, что было выбрано, ссылка на task-спеку. Без этого архив бесполезен через месяц.
8. Сделать screenshot-артефакты в `dialogs/` — с `dialogs/README.md`, где описано, что демонстрирует каждый.

---

## 8. Что НЕ делать

- Не дублировать информацию в нескольких файлах — одна вещь живёт в одном месте.
- Не писать timelog/changelog отдельно от `tasks/` и git log.
- Не складывать документы по датам — складывать по предмету (tasks, sprints, architecture…).
- Не очищать `change-request.md` после merge одной задачи — чистится только на sprint close.
- Не писать в коде то, что должно жить в git log или task spec (даты, ticket-id, описания задач).
- Не расширять `superpowers/specs/` новыми задачами — это архив MVP-дизайна.

---

## 9. Где взять эталон

Живой референс — [../ai-bot/docs/](../ai-bot/docs). Всё, что описано в этой инструкции, там реально работает. При возникновении вопроса «а как это должно выглядеть?» — смотреть туда.

Конкретные файлы-эталоны:
- [ai-bot/docs/README.md](../ai-bot/docs/README.md) — пример индекса
- [ai-bot/docs/instructions.md](../ai-bot/docs/instructions.md) — workflow
- [ai-bot/docs/change-request-doc.md](../ai-bot/docs/change-request-doc.md) — шаблон блока задачи
- [ai-bot/docs/architecture.md](../ai-bot/docs/architecture.md) — структура паттерны + edge cases
- [ai-bot/docs/tasks/D-04_DIALOG_HISTORY_YAML.md](../ai-bot/docs/tasks/D-04_DIALOG_HISTORY_YAML.md) — эталонная task-спека
- [ai-bot/docs/sprints/sprint-1-delivery.md](../ai-bot/docs/sprints/sprint-1-delivery.md) — эталонный delivery-документ
- [ai-bot/docs/prompts/prompts-sprint-1.md](../ai-bot/docs/prompts/prompts-sprint-1.md) — эталонный prompts-архив с аннотациями
