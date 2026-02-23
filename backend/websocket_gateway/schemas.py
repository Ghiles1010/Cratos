"""Pydantic schemas for the WebSocket gateway."""

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class ExecutionStatus(str, Enum):
    """Valid execution status values."""

    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"


class ExecutionResult(BaseModel):
    """Execution result from Celery workers."""

    task_id: str = Field(..., description="Unique task identifier")
    status: ExecutionStatus = Field(..., description="Execution status")
    execution_number: int = Field(..., ge=0, description="Execution sequence number")
    started_at: str = Field(..., description="ISO timestamp when execution started")
    completed_at: str | None = Field(None, description="ISO timestamp when execution completed")
    duration_seconds: float | None = Field(None, ge=0, description="Execution duration in seconds")
    http_status_code: int | None = Field(None, ge=100, le=599, description="HTTP status code if applicable")
    response_body: str | None = Field(None, description="Response body from callback")
    error_type: str | None = Field(None, description="Type of error if execution failed")
    error_message: str | None = Field(None, description="Error message if execution failed")
    retry_count: int = Field(0, ge=0, description="Number of retry attempts")
    is_retry: bool = Field(False, description="Whether this is a retry execution")


class CallbackResponse(BaseModel):
    """Response from callback endpoint."""

    status: Literal["received"] = Field(..., description="Callback processing status")
    task_id: str = Field(..., description="Task identifier")
    delivered_via_websocket: bool = Field(..., description="Whether message was delivered via WebSocket")


class HealthResponse(BaseModel):
    """Health check response."""

    status: Literal["healthy"] = Field(..., description="Service health status")
    connections: int = Field(..., ge=0, description="Total number of active WebSocket connections")


class WebSocketMessageType(str, Enum):
    """Valid WebSocket message types."""

    SUBSCRIBED = "subscribed"
    EXECUTION_RESULT = "execution_result"


class WebSocketMessage(BaseModel):
    """WebSocket message format."""

    type: WebSocketMessageType = Field(..., description="Message type")
    task_id: str | None = Field(None, description="Task identifier")
    status: ExecutionStatus | None = Field(None, description="Execution status")
    execution_number: int | None = Field(None, ge=0, description="Execution sequence number")
    started_at: str | None = Field(None, description="ISO timestamp when execution started")
    completed_at: str | None = Field(None, description="ISO timestamp when execution completed")
    duration_seconds: float | None = Field(None, ge=0, description="Execution duration in seconds")
    http_status_code: int | None = Field(None, ge=100, le=599, description="HTTP status code if applicable")
    error_type: str | None = Field(None, description="Type of error if execution failed")
    error_message: str | None = Field(None, description="Error message if execution failed")
    retry_count: int | None = Field(None, ge=0, description="Number of retry attempts")
    is_retry: bool | None = Field(None, description="Whether this is a retry execution")
    topic: str | None = Field(None, description="Subscription topic")
    message: str | None = Field(None, description="Human-readable message")


