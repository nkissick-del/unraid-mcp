"""Shared utility helpers for Unraid MCP tools."""

import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

# Re-export validation functions for backward compatibility
from .validation import (
    require_confirm,
    truncate_for_error,
    validate_enum,
    validate_input_dict,
    validate_log_file_path,
    validate_positive_int,
    validate_rclone_remote_name,
    validate_string_not_empty,
)

T = TypeVar("T")

_logger = logging.getLogger(__name__)

__all__ = [
    "ensure_dict",
    "ensure_list",
    "format_bytes",
    "format_kb",
    "poll_with_backoff",
    "require_confirm",
    "truncate_for_error",
    "validate_enum",
    "validate_input_dict",
    "validate_log_file_path",
    "validate_positive_int",
    "validate_rclone_remote_name",
    "validate_string_not_empty",
]


def ensure_dict(value: Any) -> dict[str, Any]:
    """Return value if it's a dict, otherwise return an empty dict."""
    return value if isinstance(value, dict) else {}


def ensure_list(value: Any) -> list[Any]:
    """Return value if it's a list, otherwise return an empty list."""
    return value if isinstance(value, list) else []


def format_bytes(value: int | None) -> str:
    """Format a byte count into a human-readable string (B/KB/MB/GB/TB/PB/EB)."""
    if value is None:
        return "N/A"
    try:
        num = float(int(value))
    except (ValueError, TypeError):
        return "N/A"

    for unit in ["B", "KB", "MB", "GB", "TB", "PB"]:
        if num < 1024.0:
            return f"{num:.2f} {unit}"
        num /= 1024.0
    return f"{num:.2f} EB"


def format_kb(k: Any) -> str:
    """Format a kilobyte count into a human-readable string (KB/MB/GB/TB).

    Handles edge cases: None -> "N/A", float("inf") -> "inf", non-numeric -> str(value).
    """
    if k is None:
        return "N/A"
    try:
        k = int(float(k))
    except (ValueError, TypeError, OverflowError):
        return str(k)

    if k >= 1024 * 1024 * 1024:
        return f"{k / (1024 * 1024 * 1024):.2f} TB"
    if k >= 1024 * 1024:
        return f"{k / (1024 * 1024):.2f} GB"
    if k >= 1024:
        return f"{k / 1024:.2f} MB"
    return f"{k} KB"


async def poll_with_backoff(
    query_fn: Callable[[], Awaitable[T | None]],
    max_retries: int,
    initial_delay: float,
    backoff_factor: float,
    operation_name: str = "operation",
) -> T | None:
    """Poll an async function with exponential backoff until it returns a non-None result.

    Args:
        query_fn: Async callable that returns a result or None
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay between retries in seconds
        backoff_factor: Multiplier applied to delay after each retry
        operation_name: Human-readable name for logging

    Returns:
        The first non-None result from query_fn, or None if all retries exhausted
    """
    delay = initial_delay

    for attempt in range(max_retries):
        try:
            result = await query_fn()
            if result is not None:
                return result
        except Exception as e:
            _logger.warning(
                f"Error during {operation_name} poll (attempt {attempt + 1}/{max_retries}): {e}"
            )
            if attempt == max_retries - 1:
                return None

        if attempt < max_retries - 1:
            _logger.debug(f"{operation_name}: retry {attempt + 1}/{max_retries} in {delay:.1f}s")
            await asyncio.sleep(delay)
            delay *= backoff_factor

    return None
