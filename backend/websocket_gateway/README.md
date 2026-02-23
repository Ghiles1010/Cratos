# WebSocket Gateway

FastAPI service that routes task execution results to WebSocket subscribers for real-time notifications.

## Architecture

The gateway is part of the Cratos project and receives execution results from Celery workers:
- Receives execution results from Celery workers
- Routes to WebSocket subscribers (if any are connected)
- HTTP callbacks are handled directly by Cratos (this gateway is WebSocket-only)

## Endpoints

- `POST /callback` - Receive execution results from Cratos
- `GET /health` - Health check
- `WS /ws/subscribe/{topic}` - WebSocket subscription endpoint

## Topics

Topics follow the pattern: `task:{task_id}` or `user:{user_id}`

## Usage

### WebSocket Subscription

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/subscribe/task:abc-123');
ws.onmessage = (event) => {
  const result = JSON.parse(event.data);
  console.log('Task completed:', result.status);
};
```

### Configuration

Set `WEBSOCKET_GATEWAY_URL=http://websocket-gateway:8000` in environment variables.
If not set, WebSocket notifications are disabled (HTTP callbacks still work normally).
