FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY pyproject.toml ./
COPY src/ ./src/
RUN pip install -e ".[dev]"

COPY tests/ ./tests/

RUN useradd -m -u 1000 agent && chown -R agent:agent /app
USER agent

ENTRYPOINT ["python", "-m", "agent"]
