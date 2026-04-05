#!/bin/bash
set -e

# Generate a stable SECRET_KEY if not provided, persisted to a file so all
# Gunicorn workers share the same key across restarts.
if [ -z "$DJANGO_SECRET_KEY" ]; then
  KEY_FILE="/tmp/cratos_secret_key"
  if [ ! -f "$KEY_FILE" ]; then
    python -c "import secrets; print(secrets.token_urlsafe(50))" > "$KEY_FILE"
  fi
  export DJANGO_SECRET_KEY=$(cat "$KEY_FILE")
fi

echo "[cratos] Running migrations..."
uv run python manage.py migrate --noinput

echo "[cratos] Bootstrapping..."
uv run python manage.py bootstrap

exec "$@"
