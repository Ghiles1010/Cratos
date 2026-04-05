"""
Cron expression utilities powered by ``croniter``.

Thin wrapper that provides:
  - ``next_cron_occurrence()`` — next fire time in UTC
  - ``validate_cron()``       — check syntax, raise ValueError on bad input
  - ``describe_cron()``       — human-readable description (optional)
"""

from __future__ import annotations

import zoneinfo
from datetime import datetime
from typing import Optional

from croniter import croniter, CroniterBadCronError, CroniterBadDateError
from django.utils import timezone

try:
    from cron_descriptor import get_description as _describe
except ImportError:  # cron-descriptor is optional
    _describe = None


# ── Public API ───────────────────────────────────────────────────────────────

def next_cron_occurrence(
    expression: str,
    after: Optional[datetime] = None,
    tz_name: str = "UTC",
) -> datetime:
    """
    Return the next datetime (UTC) matching *expression* strictly after *after*.

    Raises ``ValueError`` on invalid expressions or timezones.
    """
    validate_cron(expression)

    if after is None:
        after = timezone.now()

    try:
        tz = zoneinfo.ZoneInfo(tz_name)
    except (KeyError, Exception) as exc:
        raise ValueError(f"Invalid timezone: {tz_name!r}") from exc

    # croniter works in the task's local timezone so DST is handled correctly
    local_after = after.astimezone(tz)

    try:
        cron = croniter(expression, local_after)
        next_local: datetime = cron.get_next(datetime)
    except CroniterBadDateError as exc:
        raise ValueError(f"Cannot compute next occurrence: {exc}") from exc

    # Convert back to UTC for storage
    return next_local.astimezone(timezone.utc)


def validate_cron(expression: str) -> None:
    """
    Validate a cron expression.

    Raises ``ValueError`` with a descriptive message on invalid input.
    """
    if not expression or not expression.strip():
        raise ValueError("Cron expression cannot be empty.")

    if not croniter.is_valid(expression):
        raise ValueError(f"Invalid cron expression: {expression!r}")


def describe_cron(expression: str) -> str:
    """
    Return a human-readable description of a cron expression.

    Falls back to the raw expression if ``cron-descriptor`` is not installed.

    Examples:
        "*/5 * * * *"   → "Every 5 minutes"
        "0 9 * * 1-5"  → "At 09:00 AM, Monday through Friday"
        "0 0 1 * *"    → "At 12:00 AM, on day 1 of the month"
    """
    if _describe is None:
        return expression

    try:
        return _describe(expression)
    except Exception:
        return expression
