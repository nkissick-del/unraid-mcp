"""Logging configuration for Unraid MCP Server.

This module sets up structured logging with Rich console and overwrite file handlers
that cap at 10MB and start over (no rotation) for consistent use across all modules.
"""

import logging
import sys

try:
    from fastmcp.utilities.logging import get_logger as get_fastmcp_logger

    FASTMCP_AVAILABLE = True
except ImportError:
    FASTMCP_AVAILABLE = False

from rich.console import Console

from ..core.constants import LOG_FILE_MAX_BYTES
from .logging_handlers import JsonFormatter, OverwriteFileHandler, RedactingFilter
from .settings import LOG_FILE_PATH, LOG_FORMAT, LOG_LEVEL_STR

__all__ = [
    "logger",
    "setup_logger",
    "configure_fastmcp_logger_with_rich",
    "JsonFormatter",
    "OverwriteFileHandler",
    "RedactingFilter",
]

# Shared Rich console for consistent formatting
console = Console(stderr=True, force_terminal=True)


def setup_logger(name: str = "UnraidMCPServer") -> logging.Logger:
    """Set up and configure the logger with console and file handlers.

    Args:
        name: Logger name (defaults to UnraidMCPServer)

    Returns:
        Configured logger instance
    """
    # Get numeric log level
    numeric_log_level = getattr(logging, LOG_LEVEL_STR, logging.INFO)

    # Define the logger
    logger = logging.getLogger(name)
    logger.setLevel(numeric_log_level)
    logger.propagate = False  # Prevent root logger from duplicating handlers

    # Clear any existing handlers
    logger.handlers.clear()

    redacting_filter = RedactingFilter()

    if LOG_FORMAT == "json":
        json_handler = logging.StreamHandler(sys.stderr)
        json_handler.setLevel(numeric_log_level)
        json_handler.setFormatter(JsonFormatter())
        json_handler.addFilter(redacting_filter)
        logger.addHandler(json_handler)
    else:
        # Rich Console Handler for beautiful output
        from rich.logging import RichHandler

        console_handler = RichHandler(
            console=console,
            show_time=True,
            show_level=True,
            show_path=False,
            rich_tracebacks=True,
            tracebacks_show_locals=True,
        )
        console_handler.setLevel(numeric_log_level)
        console_handler.addFilter(redacting_filter)
        logger.addHandler(console_handler)

    # File Handler with 10MB cap (overwrites instead of rotating)
    file_handler = OverwriteFileHandler(
        LOG_FILE_PATH, max_bytes=LOG_FILE_MAX_BYTES, encoding="utf-8"
    )
    file_handler.setLevel(numeric_log_level)
    if LOG_FORMAT == "json":
        file_handler.setFormatter(JsonFormatter())
    else:
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
    file_handler.addFilter(redacting_filter)
    logger.addHandler(file_handler)

    return logger


def configure_fastmcp_logger_with_rich() -> logging.Logger | None:
    """Configure FastMCP logger to use Rich formatting with Nordic colors."""
    if not FASTMCP_AVAILABLE:
        return None

    # Get numeric log level
    numeric_log_level = getattr(logging, LOG_LEVEL_STR, logging.INFO)

    # Get the FastMCP logger
    fastmcp_logger = get_fastmcp_logger("UnraidMCPServer")

    # Clear existing handlers
    fastmcp_logger.handlers.clear()
    fastmcp_logger.propagate = False

    redacting_filter = RedactingFilter()

    if LOG_FORMAT == "json":
        json_formatter = JsonFormatter()

        fmcp_json_handler = logging.StreamHandler(sys.stderr)
        fmcp_json_handler.setLevel(numeric_log_level)
        fmcp_json_handler.setFormatter(json_formatter)
        fmcp_json_handler.addFilter(redacting_filter)
        fastmcp_logger.addHandler(fmcp_json_handler)
    else:
        from rich.logging import RichHandler

        # Rich Console Handler
        fmcp_rich_handler = RichHandler(
            console=console,
            show_time=True,
            show_level=True,
            show_path=False,
            rich_tracebacks=True,
            tracebacks_show_locals=True,
            markup=True,
        )
        fmcp_rich_handler.setLevel(numeric_log_level)
        fmcp_rich_handler.addFilter(redacting_filter)
        fastmcp_logger.addHandler(fmcp_rich_handler)

    # Shared file handler — one instance for both loggers to avoid duplicate
    # writes and uncoordinated file-size resets
    shared_file_handler = OverwriteFileHandler(
        LOG_FILE_PATH, max_bytes=LOG_FILE_MAX_BYTES, encoding="utf-8"
    )
    shared_file_handler.setLevel(numeric_log_level)
    if LOG_FORMAT == "json":
        shared_file_handler.setFormatter(JsonFormatter())
    else:
        shared_file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s"
            )
        )
    shared_file_handler.addFilter(redacting_filter)
    fastmcp_logger.addHandler(shared_file_handler)

    fastmcp_logger.setLevel(numeric_log_level)

    # Also configure the root logger to catch any other logs
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.propagate = False

    if LOG_FORMAT == "json":
        root_json_handler = logging.StreamHandler(sys.stderr)
        root_json_handler.setLevel(numeric_log_level)
        root_json_handler.setFormatter(JsonFormatter())
        root_json_handler.addFilter(redacting_filter)
        root_logger.addHandler(root_json_handler)
    else:
        from rich.logging import RichHandler

        # Rich Console Handler for root logger
        root_rich_handler = RichHandler(
            console=console,
            show_time=True,
            show_level=True,
            show_path=False,
            rich_tracebacks=True,
            tracebacks_show_locals=True,
            markup=True,
        )
        root_rich_handler.setLevel(numeric_log_level)
        root_rich_handler.addFilter(redacting_filter)
        root_logger.addHandler(root_rich_handler)

    # Reuse the same file handler for root logger
    root_logger.addHandler(shared_file_handler)
    root_logger.setLevel(numeric_log_level)

    return fastmcp_logger


# Global logger instance - modules can import this directly
if FASTMCP_AVAILABLE:
    # Use FastMCP logger with Rich formatting
    _fastmcp_logger = configure_fastmcp_logger_with_rich()
    if _fastmcp_logger is not None:
        logger = _fastmcp_logger
    else:
        # Fallback to our custom logger if FastMCP configuration fails
        logger = setup_logger()
else:
    # Fallback to our custom logger if FastMCP is not available
    logger = setup_logger()
