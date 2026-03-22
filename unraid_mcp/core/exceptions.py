"""Custom exceptions for Unraid MCP Server.

This module defines custom exception classes for consistent error handling
throughout the application, with proper integration to FastMCP's error system.
"""

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
