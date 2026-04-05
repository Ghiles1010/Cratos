from dataclasses import dataclass


@dataclass(frozen=True)
class FailureOutcome:
    retried: bool
    retry_delay_seconds: int | None = None


@dataclass(frozen=True)
class SuccessResult:
    status_code: int
    response_text: str
    recurring_advanced: bool = False


@dataclass(frozen=True)
class FailureResult:
    error: str
    retry_count: int
    max_retries: int
    retry_policy: str
    retry_scheduled: bool
    retry_delay_seconds: int | None
