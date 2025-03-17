ARG PYTHON_VERSION=3.12
ARG UV_VERSION=0.6.6

FROM ghcr.io/astral-sh/uv:${UV_VERSION}-python${PYTHON_VERSION}-bookworm-slim

WORKDIR /usr/src/app

COPY uv.lock pyproject.toml ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

COPY bot ./bot
COPY alembic ./alembic
COPY alembic.ini ./alembic.ini
COPY ./bin/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

ENV PATH="/usr/src/app/.venv/bin:$PATH"
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
