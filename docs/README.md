# ai-agent · docs index

MVP автономного AI-агента на локальной LLM (Qwen3-4B через lemonade), JSON-prompting loop с tool-use.

## Корневые файлы

| Файл | Назначение |
|---|---|
| [project.md](project.md) | Что это, зачем, stack — обзор на один экран |
| [instructions.md](instructions.md) | Workflow (TDD, task lifecycle, branch naming, karpathy guidelines) |
| [plan.md](plan.md) | Roadmap по фазам A/B/C/D |
| [ideas.md](ideas.md) | Копилка сырых идей |
| [discuss.md](discuss.md) | Открытые архитектурные/продуктовые вопросы |
| [tasks.md](tasks.md) | Master-каталог задач |
| [change-request.md](change-request.md) | Зеркало текущего спринта (все активные блоки) |
| [change-request-doc.md](change-request-doc.md) | Шаблон блока задачи |
| [architecture.md](architecture.md) | Архитектура + edge cases |
| [context-dump.md](context-dump.md) | Карта кода file:line |
| [tech-stack.md](tech-stack.md) | Зависимости, env, версии |
| [db-schema.md](db-schema.md) | Хранение данных (пока stateless) |
| [ui-kit.md](ui-kit.md) | CLI-интерфейс, формат вывода |
| [testing.md](testing.md) | Тестовый стек + команды |
| [legacy-warning.md](legacy-warning.md) | Тех-долг, known issues, костыли |
| [links.md](links.md) | Внешние ссылки (lemonade, модель, OpenAI SDK) |

## Поддиректории

| Путь | Назначение |
|---|---|
| [tasks/](tasks/) | Детальные спеки задач (один файл = одна задача) |
| [contracts/](contracts/) | Внешние интерфейсы (только lemonade на этом этапе) |
| [sprints/](sprints/) | Текущий + закрытые спринты |
| [prompts/](prompts/) | Архив промтов к AI-агенту-разработчику |
| [dialogs/](dialogs/) | Логи живых прогонов (acceptance-артефакты) |
| [superpowers/](superpowers/) | Архив MVP-дизайна (не расширяется) |

## Навигация по ролям

| Вопрос | Файл |
|---|---|
| «Что это за проект?» | [project.md](project.md) |
| «Как запустить?» | [../README.md](../README.md) + [ui-kit.md](ui-kit.md) |
| «Как устроен loop?» | [architecture.md](architecture.md) |
| «Где код?» | [context-dump.md](context-dump.md) |
| «Что в работе?» | [sprints/current-sprint.md](sprints/current-sprint.md) |
| «Как прогнать тесты?» | [testing.md](testing.md) |
| «К какой модели ходим?» | [contracts/external/lemonade.md](contracts/external/lemonade.md) |
