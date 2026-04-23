.PHONY: help network build run test test-int test-cov shell clean logs venv

TASK ?= "Посчитай (123 + 456) * 2"
MODEL ?=
_MODEL_ARG = $(if $(MODEL),--model $(MODEL),)

help:           ## show this help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

network:        ## create shared llm-net docker network (idempotent)
	@docker network inspect llm-net >/dev/null 2>&1 || docker network create llm-net

build: network  ## build the agent image
	docker compose build

run:            ## run agent with TASK="..." [MODEL=...] (run `make build` first if code changed)
	docker compose --progress=quiet run --rm agent $(_MODEL_ARG) "$(TASK)"

test:           ## unit tests inside container
	docker compose run --rm --entrypoint pytest agent tests/unit -v

test-int:       ## integration tests against live lemonade
	docker compose run --rm --entrypoint pytest agent tests/integration -v -s

test-cov:       ## unit tests with coverage report
	docker compose run --rm --entrypoint pytest agent tests/unit --cov=src/agent --cov-report=term-missing

shell:          ## drop into a bash shell in the container
	docker compose run --rm --entrypoint bash agent

logs:           ## tail container logs
	docker compose logs -f

clean:          ## remove image + volumes
	docker compose down -v --rmi local

venv:           ## set up local venv for host-side dev
	virtualenv .venv && .venv/bin/pip install -e ".[dev]"
