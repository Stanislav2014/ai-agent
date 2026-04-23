# D-05 · Auto-save run logs

**Status:** ✅ Done (Sprint 2 add-on)
**Branch:** `main`

## Problem

После D-04 в stdout пишутся тайминги и итог, но всё равно исчезает при закрытии терминала. Для анализа прогонов (сравнить модели, промпты, найти закономерности) нужно сохранять логи. Делать это руками через `tee` — трение.

## Scope

### In scope
- Makefile-флаг `SAVE=1`: `make run TASK='...' SAVE=1` дублирует вывод в `docs/dialogs/run-<timestamp>.log` (формат `YYYYMMDD-HHMMSS`).
- Пишет одновременно и в терминал, и в файл (`tee`), а не только в файл — чтобы пользователь видел прогресс.
- `.gitignore`: `docs/dialogs/run-*.log` — вне git. Acceptance-снимки (`test*-*.log`) остаются в репо.

### Out of scope
- Авто-пуш логов куда-то (S3, elastic).
- Ротация / очистка старых логов (делается вручную `rm docs/dialogs/run-*.log`).
- JSON-формат логов (D-06+, если понадобится парсить).

## Design

```make
SAVE ?=
_LOG_FILE = docs/dialogs/run-$(shell date +%Y%m%d-%H%M%S).log
_RUN_CMD = docker compose --progress=quiet run --rm agent $(_MODEL_ARG) "$(TASK)"

run:
ifeq ($(SAVE),1)
	@echo "(saving to $(_LOG_FILE))"
	@$(_RUN_CMD) 2>&1 | tee $(_LOG_FILE)
else
	@$(_RUN_CMD)
endif
```

- `_LOG_FILE` разрешается один раз при каждом вызове `make run` (через `$(shell date ...)`) — гарантированно уникальное имя.
- `2>&1 | tee` сохраняет и stdout, и stderr (важно, т.к. `MAX_STEPS_MESSAGE` и `LOOP_ABORT_MESSAGE` идут в stderr).
- При `SAVE=` или отсутствии — поведение **полностью** неизменно (no-op на `make run`).

## Success criteria

- [x] `make run TASK='...' SAVE=1` создаёт файл `docs/dialogs/run-<ts>.log` с полным выводом агента.
- [x] `git status` после такого запуска не показывает файл (благодаря правилу в .gitignore).
- [x] `make run TASK='...'` без `SAVE=1` ведёт себя как раньше (регрессия покрыта existing-smoke-запуском).
- [x] Acceptance-логи в репо (`test*-*.log`) продолжают трекаться.

## Files touched

- `Makefile` — +`SAVE ?=`, +`_LOG_FILE`, +`_RUN_CMD`, условная ветка с `tee`.
- `.gitignore` — +строка `docs/dialogs/run-*.log`.

## Regression watch

- `tee` есть везде (Linux / macOS / WSL). Windows-native без git-bash — поломается, но у нас только Linux-dev.
- Если `docs/dialogs/` вдруг станет read-only (chmod) — `tee` упадёт, но видно сразу из ошибки. Маловероятно.
- При очень большом выводе (не наш случай — agent compact) tee может тормозить; для MVP не критично.

## History

- 2026-04-23 — открыт по запросу пользователя (`лог сохраняется?` → «да, но в git не добавляй»), Merged
