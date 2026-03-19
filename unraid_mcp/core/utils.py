"""Shared utility helpers for Unraid MCP tools."""

from typing import Any

from ..core.exceptions import ValidationError


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


def validate_positive_int(value: int, name: str, max_value: int | None = None) -> int:
    """Validate that a value is a non-negative integer, optionally with an upper bound."""
    if value < 0:
        raise ValidationError(f"{name} must be non-negative, got {value}")
    if max_value is not None and value > max_value:
        raise ValidationError(f"{name} must be at most {max_value}, got {value}")
    return value


def validate_enum(value: str, allowed: list[str], name: str) -> str:
    """Validate that a value is one of the allowed options."""
    if value not in allowed:
        raise ValidationError(f"Invalid {name}. Must be one of {allowed}, got '{value}'.")
    return value


def validate_string_not_empty(value: str, name: str) -> str:
    """Validate that a string is not empty or whitespace-only."""
    if not value or not value.strip():
        raise ValidationError(f"{name} must not be empty")
    return value


def validate_log_file_path(path: str) -> str:
    """Validate a log file path for obvious traversal or injection attempts."""
    if not path or not path.strip():
        raise ValidationError("log_file_path must not be empty")
    if "\x00" in path:
        raise ValidationError("log_file_path must not contain null bytes")
    if ".." in path:
        raise ValidationError("log_file_path must not contain '..'")
    if not path.startswith("/"):
        raise ValidationError("log_file_path must be an absolute path")
    return path


def truncate_for_error(text: str, max_length: int = 500) -> str:
    """Truncate a string for safe inclusion in error messages and logs."""
    if len(text) <= max_length:
        return text
    return text[:max_length] + f"... [truncated, {len(text)} chars total]"
