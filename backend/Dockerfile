FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Install uv from its official image – no curl, no apt
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Install dependencies first (cached layer – only re-runs when lock file changes)
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project

# Copy project and finalize
COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

EXPOSE 8001

CMD ["uv", "run", "gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8001", "--workers", "3"]
