"""Centralized input validation functions for Unraid MCP tools."""

import re

from ..core.constants import (
    ALLOWED_LOG_PREFIXES,
    ERROR_TRUNCATION_LENGTH,
    RCLONE_REMOTE_NAME_PATTERN,
)
from ..core.exceptions import ValidationError


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
    if not any(path.startswith(prefix) for prefix in ALLOWED_LOG_PREFIXES):
        raise ValidationError(
            f"log_file_path must start with one of: {', '.join(ALLOWED_LOG_PREFIXES)}"
        )
    return path


def truncate_for_error(text: str, max_length: int = ERROR_TRUNCATION_LENGTH) -> str:
    """Truncate a string for safe inclusion in error messages and logs."""
    if len(text) <= max_length:
        return text
    return text[:max_length] + f"... [truncated, {len(text)} chars total]"
