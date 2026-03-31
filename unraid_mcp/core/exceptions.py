"""Custom exceptions for Unraid MCP Server.

This module defines custom exception classes for consistent error handling
throughout the application, with proper integration to FastMCP's error system.
"""

from collections.abc import Generator
from contextlib import contextmanager
from logging import Logger

from fastmcp.exceptions import ToolError as FastMCPToolError


class ToolError(FastMCPToolError):
    """User-facing error that MCP clients can handle.

    This is the main exception type used throughout the application for
    errors that should be presented to the user/LLM in a friendly way.

    Inherits from FastMCP's ToolError to ensure proper MCP protocol handling.
    """

    pass


class ValidationError(ToolError):
    """Raised when input validation fails."""

    pass


@contextmanager
def tool_error_handler(tool_name: str, action: str, logger: Logger) -> Generator[None, None, None]:
    """Context manager that normalises exceptions into ToolError.

    - ToolError passes through unchanged.
    - TimeoutError becomes a descriptive ToolError (no internal details).
    - All other exceptions are logged with full traceback then re-raised as a
      sanitised ToolError so internal details do not leak to the caller.
    """
    try:
        yield
    except ToolError:
        raise
    except TimeoutError:
        raise ToolError(
            f"{tool_name}: {action} timed out — the Unraid server may be under heavy load"
        ) from None
    except Exception as e:
        logger.error(f"{tool_name}: {action} failed: {e}", exc_info=True)
        raise ToolError(
            f"{tool_name}: {action} failed — check server logs for details"
        ) from e
