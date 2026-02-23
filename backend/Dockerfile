FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

WORKDIR /app

# Install system dependencies + uv
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc postgresql-client curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Install Python deps (leverages Docker layer cache)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

# Copy project
COPY . .
RUN uv sync --frozen

EXPOSE 8001

CMD ["uv", "run", "gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8001", "--workers", "3"]
