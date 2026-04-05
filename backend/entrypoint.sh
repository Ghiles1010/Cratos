#!/bin/bash
set -e

echo "[cratos] Running migrations..."
uv run python manage.py migrate --noinput

echo "[cratos] Bootstrapping..."
uv run python manage.py bootstrap

exec "$@"
