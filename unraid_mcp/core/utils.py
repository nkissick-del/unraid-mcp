"""Shared utility helpers for Unraid MCP tools."""

from typing import Any


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
