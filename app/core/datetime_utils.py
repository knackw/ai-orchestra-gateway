"""
SEC-014: Unified Date/Time Handling

Provides consistent ISO 8601 UTC date/time handling across the application.
All timestamps should be stored and transmitted in UTC with ISO 8601 format.

Format: YYYY-MM-DDTHH:MM:SS.sssZ (e.g., 2025-12-09T14:30:00.000Z)

Key Principles:
1. Always store in UTC
2. Always transmit in ISO 8601 format
3. Convert to local timezone only for display in frontend
4. Use timezone-aware datetime objects
"""

from datetime import datetime, timezone, timedelta
from typing import Optional, Union
import re


# ISO 8601 format with milliseconds and Z suffix
ISO_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
ISO_FORMAT_NO_MS = "%Y-%m-%dT%H:%M:%SZ"

# Regex for ISO 8601 validation
ISO_8601_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"
    r"(?:\.\d{1,6})?"  # Optional milliseconds
    r"(?:Z|[+-]\d{2}:?\d{2})$"  # Z or timezone offset
)


def utc_now() -> datetime:
    """
    Get current UTC datetime with timezone info.

    Returns:
        Timezone-aware datetime in UTC
    """
    return datetime.now(timezone.utc)


def utc_now_iso() -> str:
    """
    Get current UTC datetime as ISO 8601 string.

    Returns:
        ISO 8601 formatted string with Z suffix (e.g., '2025-12-09T14:30:00.000000Z')
    """
    return utc_now().strftime(ISO_FORMAT)


def to_iso(dt: Optional[datetime]) -> Optional[str]:
    """
    Convert datetime to ISO 8601 string in UTC.

    Args:
        dt: Datetime object (timezone-aware or naive)

    Returns:
        ISO 8601 string in UTC, or None if input is None
    """
    if dt is None:
        return None

    # If naive datetime, assume UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        # Convert to UTC
        dt = dt.astimezone(timezone.utc)

    return dt.strftime(ISO_FORMAT)


def from_iso(iso_string: Optional[str]) -> Optional[datetime]:
    """
    Parse ISO 8601 string to datetime in UTC.

    Handles various ISO 8601 formats:
    - 2025-12-09T14:30:00Z
    - 2025-12-09T14:30:00.000Z
    - 2025-12-09T14:30:00+00:00
    - 2025-12-09T14:30:00.000000+00:00

    Args:
        iso_string: ISO 8601 formatted string

    Returns:
        Timezone-aware datetime in UTC, or None if input is None

    Raises:
        ValueError: If string is not a valid ISO 8601 format
    """
    if iso_string is None:
        return None

    if not isinstance(iso_string, str):
        raise ValueError(f"Expected string, got {type(iso_string)}")

    # Handle Z suffix
    if iso_string.endswith("Z"):
        iso_string = iso_string[:-1] + "+00:00"

    try:
        dt = datetime.fromisoformat(iso_string)
        # Ensure UTC
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
        return dt
    except ValueError as e:
        raise ValueError(f"Invalid ISO 8601 format: {iso_string}") from e


def is_valid_iso(iso_string: str) -> bool:
    """
    Check if string is a valid ISO 8601 datetime.

    Args:
        iso_string: String to validate

    Returns:
        True if valid ISO 8601 datetime string
    """
    if not iso_string or not isinstance(iso_string, str):
        return False
    return bool(ISO_8601_PATTERN.match(iso_string))


def add_days(dt: Optional[datetime], days: int) -> Optional[datetime]:
    """
    Add days to a datetime.

    Args:
        dt: Base datetime
        days: Number of days to add (can be negative)

    Returns:
        New datetime, or None if input is None
    """
    if dt is None:
        return None
    return dt + timedelta(days=days)


def add_hours(dt: Optional[datetime], hours: int) -> Optional[datetime]:
    """
    Add hours to a datetime.

    Args:
        dt: Base datetime
        hours: Number of hours to add (can be negative)

    Returns:
        New datetime, or None if input is None
    """
    if dt is None:
        return None
    return dt + timedelta(hours=hours)


def start_of_day(dt: Optional[datetime] = None) -> datetime:
    """
    Get start of day (00:00:00.000000) in UTC.

    Args:
        dt: Datetime (defaults to now)

    Returns:
        Start of day in UTC
    """
    if dt is None:
        dt = utc_now()
    elif dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)

    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def end_of_day(dt: Optional[datetime] = None) -> datetime:
    """
    Get end of day (23:59:59.999999) in UTC.

    Args:
        dt: Datetime (defaults to now)

    Returns:
        End of day in UTC
    """
    if dt is None:
        dt = utc_now()
    elif dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)

    return dt.replace(hour=23, minute=59, second=59, microsecond=999999)


def start_of_month(dt: Optional[datetime] = None) -> datetime:
    """
    Get start of month in UTC.

    Args:
        dt: Datetime (defaults to now)

    Returns:
        First day of month at 00:00:00 in UTC
    """
    if dt is None:
        dt = utc_now()
    elif dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)

    return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def days_between(dt1: datetime, dt2: datetime) -> int:
    """
    Calculate number of days between two datetimes.

    Args:
        dt1: First datetime
        dt2: Second datetime

    Returns:
        Number of days (positive if dt2 > dt1)
    """
    # Ensure both are UTC
    if dt1.tzinfo is None:
        dt1 = dt1.replace(tzinfo=timezone.utc)
    if dt2.tzinfo is None:
        dt2 = dt2.replace(tzinfo=timezone.utc)

    return (dt2 - dt1).days


def is_expired(dt: Optional[datetime]) -> bool:
    """
    Check if a datetime is in the past (expired).

    Args:
        dt: Datetime to check

    Returns:
        True if dt is in the past, False if None or in future
    """
    if dt is None:
        return False

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return dt < utc_now()


def format_relative(dt: datetime) -> str:
    """
    Format datetime as relative time string (for logs/debug).

    Args:
        dt: Datetime to format

    Returns:
        Relative time string (e.g., "2 hours ago", "in 3 days")
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    now = utc_now()
    diff = now - dt

    seconds = diff.total_seconds()

    if seconds < 0:
        # Future
        seconds = abs(seconds)
        prefix = "in "
        suffix = ""
    else:
        # Past
        prefix = ""
        suffix = " ago"

    if seconds < 60:
        return f"{prefix}{int(seconds)} seconds{suffix}"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{prefix}{minutes} minute{'s' if minutes != 1 else ''}{suffix}"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{prefix}{hours} hour{'s' if hours != 1 else ''}{suffix}"
    else:
        days = int(seconds / 86400)
        return f"{prefix}{days} day{'s' if days != 1 else ''}{suffix}"


# Export all functions
__all__ = [
    "utc_now",
    "utc_now_iso",
    "to_iso",
    "from_iso",
    "is_valid_iso",
    "add_days",
    "add_hours",
    "start_of_day",
    "end_of_day",
    "start_of_month",
    "days_between",
    "is_expired",
    "format_relative",
    "ISO_FORMAT",
    "ISO_FORMAT_NO_MS",
]
