# Cratos

<div align="center">

**Self-hosted task scheduler with a built-in web UI**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18.2+-61dafb.svg)](https://reactjs.org/)

</div>

---

Schedule webhook callbacks — one-off, cron, or interval — with retry policies, execution history, and real-time updates. Everything runs in a single `docker compose up`.

## Screenshots

### Tasks Dashboard
![Tasks Dashboard](docs/images/tasks.png)

### Task Details
![Task Details](docs/images/task_details.png)

### Metrics Dashboard
![Metrics Dashboard](docs/images/metrics.png)

## Features

- **Flexible Scheduling** — one-off, cron expressions, and interval-based tasks with timezone support
- **Retry Policies** — fixed, linear, and exponential backoff
- **Execution History** — full audit trail with HTTP response details, timings, and error traces
- **Real-time Updates** — WebSocket gateway for live task execution events
- **Web UI** — manage tasks, view metrics, and handle API keys from the browser
- **REST API** — full programmatic access; use directly or via the [Python SDK](https://github.com/Ghiles1010/Cratos-SDK)

## Repository Structure

```
cratos/
├── backend/          # Django API, Celery workers, WebSocket gateway
├── ui/               # React + TypeScript frontend
├── docker-compose.yml
├── .env.example
└── Taskfile.yml
```

## Quick Start

### Prerequisites

- Docker and Docker Compose

### Setup

```bash
git clone https://github.com/Ghiles1010/Cratos.git
cd Cratos
cp .env.example .env
task init
```

`task init` builds images, starts services, runs migrations, creates an admin user (`admin` / `admin`), and registers the dispatcher.

> No `task` CLI? Run the steps manually:
> ```bash
> docker compose up -d --build
> docker compose exec cratos-web python manage.py migrate
> docker compose exec cratos-web python manage.py createsuperuser
> docker compose exec cratos-web python manage.py ensure_dispatcher_periodic_task
> ```

### Access

| Service | URL |
|---------|-----|
| Web UI  | http://localhost:3001 |
| REST API | http://localhost:9101 |
| WebSocket Gateway | ws://localhost:9100 |

## Configuration

Copy `.env.example` to `.env` to customize ports:

```bash
CRATOS_API_PORT=9101
CRATOS_WS_PORT=9100
CRATOS_POSTGRES_PORT=9433
CRATOS_REDIS_PORT=9638
CRATOS_UI_PORT=3001

# URL the browser uses to reach the API (must be host-accessible)
VITE_SCHEDULER_API_URL=http://localhost:9101
```

> **Note:** `VITE_SCHEDULER_API_URL` is baked into the frontend at build time. If you change it, rebuild the UI container: `docker compose build cratos-ui`.

## API Usage

### Get your API key

```bash
docker compose exec cratos-web python manage.py get_api_key \
  --username admin --password admin
```

### Schedule a task

```bash
curl -X POST http://localhost:9101/api/tasks/ \
  -H "Authorization: Api-Key YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "task_name": "daily_report",
    "callback_url": "https://example.com/webhook",
    "schedule_type": "cron",
    "cron_expression": "0 9 * * *"
  }'
```

### List tasks

```bash
curl http://localhost:9101/api/tasks/ \
  -H "Authorization: Api-Key YOUR_API_KEY"
```

## Development

### Backend

```bash
docker compose up cratos-postgres cratos-redis -d
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend

```bash
cd ui
npm install
npm run dev   # http://localhost:3001
```

## Common Commands

```bash
task up              # Start all services
task down            # Stop all services
task logs            # Tail all logs
task migrate         # Run DB migrations
task shell           # Django shell
task ui:dev          # Start frontend dev server
```

## Related Projects

- **[Cratos SDK](https://github.com/Ghiles1010/Cratos-SDK)** — Python SDK for programmatic access

## License

MIT License — see [LICENSE](LICENSE) file for details.
