# Cratos

<div align="center">

**Self-hosted webhook scheduler with a built-in web UI**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18.2+-61dafb.svg)](https://reactjs.org/)

</div>

---

Cratos calls your HTTP endpoints on a schedule. Register a URL, pick a schedule, and Cratos fires a signed POST request at the right time — with retries, execution history, and a web UI to manage everything.

## Quick Start

**Prerequisites:** Docker and Docker Compose.

```bash
git clone https://github.com/Ghiles1010/Cratos.git
cd cratos
docker compose up -d --build
```

| Service  | URL                    |
|----------|------------------------|
| Web UI   | http://localhost:3001  |
| REST API | http://localhost:9101  |
| API Docs | http://localhost:9101/api/docs/ |

Default credentials: `admin` / `admin`. Override via environment variables or `.env` file (see `.env.example`):

```env
CRATOS_ADMIN_USERNAME=admin
CRATOS_ADMIN_PASSWORD=yourpassword
```

On a remote host, set `VITE_SCHEDULER_API_URL` to your Cratos instance's public address.

## API Usage

Get your API key from the UI (Secrets page) or via:

```bash
curl -X POST http://localhost:9101/api/auth/get-api-key/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}'
```

### Schedule a one-off task

```bash
curl -X POST http://localhost:9101/api/tasks/ \
  -H "Authorization: Api-Key YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "task_name": "send-report",
    "callback_url": "https://your-service.com/webhook",
    "schedule_type": "one_off",
    "schedule_time": "2026-03-22T18:00:00Z"
  }'
```

### Schedule a cron task

```bash
curl -X POST http://localhost:9101/api/tasks/ \
  -H "Authorization: Api-Key YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "task_name": "daily-digest",
    "callback_url": "https://your-service.com/webhook",
    "schedule_type": "cron",
    "cron_expression": "0 9 * * *",
    "task_timezone": "America/New_York"
  }'
```

### Schedule an interval task

```bash
curl -X POST http://localhost:9101/api/tasks/ \
  -H "Authorization: Api-Key YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "task_name": "health-check",
    "callback_url": "https://your-service.com/webhook",
    "schedule_type": "interval",
    "interval_seconds": 30,
    "retry_policy": "exponential",
    "max_retries": 3,
    "retry_delay_seconds": 10
  }'
```

Cratos POSTs to your `callback_url` with a signed JSON payload. Your endpoint just needs to respond with a 2xx.

## Account Management

Change password or username via API (no CLI needed):

```bash
# Change password
curl -X POST http://localhost:9101/api/auth/change-password/ \
  -H "Authorization: Api-Key YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"current_password": "admin", "new_password": "newpassword"}'

# Change username
curl -X POST http://localhost:9101/api/auth/change-username/ \
  -H "Authorization: Api-Key YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"password": "admin", "new_username": "alice"}'
```

Both are also available in the UI under **Account**.

## Webhook Signing

Every outbound request includes HMAC-SHA256 signature headers:

```
X-Cratos-Timestamp: 1709041234
X-Cratos-Signature: sha256=a3f1...
```

**Verification (Python):**

```python
import hashlib, hmac, time

def verify(payload_bytes, headers, secret, max_age_seconds=300):
    timestamp = headers["X-Cratos-Timestamp"]
    if abs(time.time() - int(timestamp)) > max_age_seconds:
        raise ValueError("Stale request")

    signed_content = f"{timestamp}.".encode() + payload_bytes
    expected = "sha256=" + hmac.new(
        secret.encode(), signed_content, hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected, headers["X-Cratos-Signature"]):
        raise ValueError("Invalid signature")
```

Get your signing secret from the UI (Secrets page) or rotate it via `POST /api/webhooks/signing-key/`.

## Security

- **Outbound allowlist** — callback URLs must come from pre-approved origins. Prevents SSRF.
- **Redirect blocking** — 3xx responses are treated as errors, not followed.
- **Per-user isolation** — users can only access their own tasks, keys, and secrets.
- **API key auth** — `Authorization: Api-Key <key>` for programmatic access.

Add allowed origins (admin only):

```bash
curl -X POST http://localhost:9101/api/webhooks/allowed-origins/ \
  -H "Authorization: Api-Key ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{"scheme": "https", "host": "hooks.example.com", "port": 443}'
```

## License

MIT — see [LICENSE](LICENSE).
