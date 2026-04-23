# D-03 · CLI `--model` flag

**Status:** ✅ Done (Sprint 2 add-on)
**Branch:** `main`

## Problem

Чтобы сменить модель приходилось:
```bash
LLM_MODEL=Qwen3-8B-GGUF make run TASK='...'
```

Это работает, но:
- не очевидно из `--help` агента,
- не видно в выводе `ai-agent --help`,
- неудобно для повторных запусков с разными моделями в одной сессии.

## Scope

### In scope
- Новый аргумент `--model <name>` в `argparse` агента.
- Если флаг задан — переопределяет `settings.llm_model` (env-переменная/дефолт).
- Если флаг не задан — всё как раньше (env → config → default).
- Проброс в `Makefile` через `MODEL=...`.
- Юнит-тест `test_model_flag_override`.

### Out of scope
- Валидация имени модели против каталога lemonade (лишняя сложность — lemonade сам скажет 404).
- Переключение модели в середине сессии (перезапуск контейнера — единственный путь).

## Design

```
priority: CLI --model   >   env LLM_MODEL   >   config default ("Qwen3-4B-Instruct-2507-GGUF")
```

Реализовано через `dataclasses.replace(settings, llm_model=args.model)` — тот же паттерн, что уже был для `--max-steps`.

В `Makefile`:

```make
MODEL ?=
_MODEL_ARG = $(if $(MODEL),--model $(MODEL),)

run:
	docker compose ... agent $(_MODEL_ARG) "$(TASK)"
```

`MODEL=` не задан → `_MODEL_ARG` пустой → аргумент не передаётся → работает env-дефолт.

## Success criteria

- [x] `make test` — 57/57 (было 56, +1 тест на `--model`)
- [x] `python -m agent --help` показывает `--model` с описанием
- [x] `make run TASK='…' MODEL=Qwen3-0.6B-GGUF` печатает правильную модель в header-строке
- [x] Без `MODEL=` поведение неизменно

## Files touched

- `src/agent/__main__.py` — +argparse `--model`, +`replace(settings, llm_model=...)`
- `tests/unit/test_cli.py` — +`test_model_flag_override`
- `Makefile` — +`MODEL ?=`, +условный `_MODEL_ARG`

## Usage

```bash
# из Makefile
make run TASK='что-то' MODEL=Qwen3-8B-GGUF
make run TASK='что-то' MODEL=Qwen3-0.6B-GGUF

# напрямую
python -m agent --model Qwen3-8B-GGUF "что-то"

# с переопределением обоих параметров
python -m agent --model Qwen3-0.6B-GGUF --max-steps 4 "что-то"
```

## History

- 2026-04-23 — открыт по запросу пользователя (отдельно от D-02)
- 2026-04-23 — реализован + юнит + Makefile-проброс, Merged
