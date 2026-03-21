"""Shared decorators for Unraid MCP tools."""

import functools
import logging
from collections.abc import Callable, Coroutine
from typing import Any

from .exceptions import ToolError

logger = logging.getLogger(__name__)


def tool_error_handler(operation_name: str) -> Callable[..., Any]:
    """Decorator: wraps tool body with standard error logging and ToolError conversion.

    Usage:
        @mcp.tool()
        @tool_error_handler("retrieve Connect info")
        async def get_connect_info() -> dict[str, Any]:
            ...

    Note: @mcp.tool() must be outermost (applied last), @tool_error_handler innermost.

    Args:
        operation_name: Human-readable description for error messages (e.g. "retrieve Connect info")
    """

    def decorator(
        fn: Callable[..., Coroutine[Any, Any, Any]],
    ) -> Callable[..., Coroutine[Any, Any, Any]]:
        @functools.wraps(fn)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                logger.info(f"Executing {fn.__name__}")
                return await fn(*args, **kwargs)
            except ToolError:
                raise
            except Exception as e:
                logger.error(f"Error in {fn.__name__}: {e}", exc_info=True)
                raise ToolError(f"Failed to {operation_name}: {str(e)}") from e

        return wrapper

    return decorator
