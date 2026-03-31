"""Centralized input validation functions for Unraid MCP tools."""

import posixpath
import re
from typing import Any

from ..core.constants import (
    ALLOWED_LOG_PREFIXES,
    ERROR_TRUNCATION_LENGTH,
    RCLONE_REMOTE_NAME_PATTERN,
)
from ..core.exceptions import ToolError, ValidationError


def require_confirm(confirm: bool, action: str, reason: str = "") -> None:
    """Raise ToolError if confirm is not True.

    Args:
        confirm: The confirm flag value
        action: Description of the action (e.g. "remove a container")
        reason: Optional extra context appended to the message
    """
    if not confirm:
        msg = f"confirm must be True to {action}."
        if reason:
            msg += f" {reason}"
        raise ToolError(msg)


def validate_input_dict(value: Any, name: str = "input_config") -> dict[str, Any]:
    """Validate value is a non-empty dict, raise ToolError otherwise."""
    if not value or not isinstance(value, dict):
        raise ToolError(f"{name} must be a non-empty dictionary")
    result: dict[str, Any] = value
    return result


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


def validate_rclone_remote_name(name: str) -> str:
    """Validate an RClone remote name (alphanumeric start, max 64 chars)."""
    validate_string_not_empty(name, "remote name")
    if not re.fullmatch(RCLONE_REMOTE_NAME_PATTERN, name):
        raise ValidationError(
            f"Invalid remote name '{name}'. Must start with alphanumeric, "
            "contain only alphanumeric/hyphen/underscore, max 64 characters."
        )
    return name


def validate_path(path: str, allowed_prefixes: list[str], param_name: str) -> str:
    """Validate a file path against allowed prefixes, rejecting traversal attempts.

    Args:
        path: The path to validate.
        allowed_prefixes: List of allowed path prefixes.
        param_name: Parameter name for error messages.

    Returns:
        The normalized (posixpath.normpath) path on success.

    Raises:
        ValidationError: If the path is empty, contains null bytes, contains '..'
            components after normalization, or does not start with an allowed prefix.
    """
    if not path or not path.strip():
        raise ValidationError(f"{param_name} must not be empty")
    if "\x00" in path:
        raise ValidationError(f"{param_name} must not contain null bytes")
    normalized = posixpath.normpath(path)
    parts = normalized.split("/")
    if ".." in parts:
        raise ValidationError(f"{param_name} contains path traversal components (..)")
    if not any(normalized.startswith(prefix) for prefix in allowed_prefixes):
        raise ValidationError(
            f"{param_name} must start with one of: {', '.join(allowed_prefixes)}"
        )
    return normalized


def validate_log_file_path(path: str) -> str:
    """Validate log file path — delegates to validate_path with log prefixes."""
    return validate_path(path, list(ALLOWED_LOG_PREFIXES), "log_file_path")


def truncate_for_error(text: str, max_length: int = ERROR_TRUNCATION_LENGTH) -> str:
    """Truncate a string for safe inclusion in error messages and logs."""
    if len(text) <= max_length:
        return text
    return text[:max_length] + f"... [truncated, {len(text)} chars total]"
