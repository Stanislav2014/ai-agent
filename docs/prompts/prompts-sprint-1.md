# Prompts archive — Sprint 1 · 2026-04-19 → 2026-04-21

Хронологический архив ключевых обменов с Claude Code (AI-разработчиком). Короткие ответы аннотированы — что стояло в выборе A/B/C, что было выбрано и почему.

---

## 1. ТЗ и первичная постановка (2026-04-19)

Пользователь прислал домашнее задание + детальную спецификацию агента (16 секций) + точный текст системного промпта. Формулировки:

- Входы/выходы: задача на вход → `final_answer` на выход
- JSON-контракт из двух форматов
- 3 примера тестов для проверки
- Просьба оформить `/docs` по `docs-organization.md`

**Никакого clarify не было — юзер задал всё сразу.** Агент-разработчик перешёл к brainstorm-этапу.

---

## 2. Brainstorm — 4 уточняющих вопроса (2026-04-21)

### Q1/4 — LLM-бэкенд

Агент предложил:
- **A.** Lemonade (рекомендация: уже в ecosystem, `Qwen3-4B-Instruct-2507-GGUF`)
- B. Ollama строго по букве ТЗ
- C. Абстракция для обоих

**Ответ:** `A`.
**Rationale:** Ollama не установлена; lemonade уже обслуживает `ai-bot` и `local-rag-mcp`; ТЗ явно разрешает.

### Q2/4 — набор инструментов

- **A.** Все три из спека (calculator/read_file/http_get) — покрывает все 3 теста ТЗ
- B. Только calculator — минимум
- C. Четвёртый бонусный

**Ответ:** `A`.
**Rationale:** 3 теста ТЗ требуют 3 инструмента.

### Q3/4 — объём docs

- **A.** Полная структура по `docs-organization.md §1` (все файлы, всё заполнено)
- B. Полная структура, но пустые каркасы в части файлов
- C. Минимум под задачу

**Ответ:** `A`.
**Rationale:** юзер явно выбрал максимально соответствовать букве инструкции.

### Q4/4 — TDD

- **A.** Строгий TDD по фазам (RED→GREEN→REFACTOR для каждого модуля)
- B. TDD ядра + smoke интеграция
- C. Без тестов

**Ответ:** `A`.
**Rationale:** юзер требует максимального соответствия процессу.

---

## 3. Дизайн, 6 секций (2026-04-21)

Агент показал по секциям (stack / components / data flow / docker / TDD plan / docs structure). Все 6 подтверждены «ок/да/ok».

На секции 4 пользователь добавил: **«сделай обертку через docker compose»** → добавлен Docker+compose+Makefile в дизайн.

---

## 4. Переход к реализации (2026-04-21)

Пользователь: «https://github.com/forrestchang/andrej-karpathy-skills поставь этот скилл и начинай реализацию. Вернсь ко мне с рабочим агентом».

Дополнительно попросил сохранить skill "Замечания к релизу" (чек-лист Yandex Games requirements) — сохранён как reference-memory в `~/.claude/projects/.../memory/reference_release_remarks.md`.

Plugin `andrej-karpathy-skills` был уже установлен (`~/.claude/plugins/cache/andrej-karpathy-skills/.../SKILL.md`). Агент прочитал SKILL.md и придерживался 4 принципов: think before coding, simplicity first, surgical changes, goal-driven execution.

---

## 5. Реализация — TDD по фазам

Последовательность:

1. Design-док → `docs/superpowers/specs/2026-04-21-mvp-agent-loop-design.md`
2. Scaffold: `pyproject.toml`, `.venv` (через `virtualenv`, т.к. `python3-venv` системно отсутствует), dir layout.
3. `parser.py` — 10 тестов → зелёные с первого прогона
4. `tools.py` — 17 тестов (calc parametrized, read_file, http_get+respx) → зелёные
5. `executor.py` — 7 тестов → зелёные
6. `config.py` + `prompts.py` + `llm.py` (без юнитов — тестируем через integration)
7. `agent.py` — 8 тестов (happy / max-steps / loop-guard / parse-retry / log-format) → зелёные
8. `__main__.py` CLI — 5 тестов → зелёные
9. `Dockerfile` + `docker-compose.yml` + `Makefile`
10. `docker compose build` → OK
11. Live прогон 3 тестов ТЗ:
    - `"Посчитай (123 + 456) * 2"` → **1158** за 2 шага
    - `"Прочитай /workspace/test.txt и сколько строк"` → **5** за 2 шага
    - `"GET https://api.github.com"` → **200 OK** за 2 шага
12. Логи сохранены в `docs/dialogs/test{1,2,3}-*.log`
13. Заполнение docs (этот файл — последний шаг)

Всё — в одной непрерывной сессии, без отката и ревью регрессий.

---

## 6. Key takeaways для будущих спринтов

- **Парсер с balanced-brace scanner** оказался overkill для Qwen3-4B (модель возвращает чистый JSON), но был полезен как страховка и не потребовал правок.
- **`temperature=0.2`** дала стабильный JSON-вывод без нарушений схемы за все 3 прогона.
- **Docker compose на внешней `llm-net`** — zero-config подключение к lemonade, скопировано 1-в-1 из `ai-bot`.
- **Ollama была лишней** — как только выяснилось, что lemonade живой, переход на него сэкономил установку/скачивание модели.
