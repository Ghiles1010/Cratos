FROM python:3.11-slim

WORKDIR /app

COPY websocket_gateway/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY websocket_gateway/ ./websocket_gateway/

EXPOSE 8000

CMD ["uvicorn", "websocket_gateway.main:app", "--host", "0.0.0.0", "--port", "8000"]
