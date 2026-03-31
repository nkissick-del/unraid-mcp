"""Shared test helpers to eliminate tool-lookup boilerplate."""

from collections.abc import Callable
from typing import Any

from fastmcp import FastMCP


async def get_tool_fn(register_fn: Callable[..., Any], tool_name: str) -> Any:
    """Register tools and return the named tool's function.

    Args:
        register_fn: The register_*_tools function to call
        tool_name: Name of the tool to look up

    Returns:
        The tool's underlying async function

    Raises:
        AssertionError: If the tool is not found after registration
    """
    mcp = FastMCP("test")
    register_fn(mcp)
    tool = await mcp._get_tool(tool_name)
    if tool is not None:
        return tool.fn
    raise AssertionError(f"Tool '{tool_name}' not found")


async def get_registered_tool_names(register_fn: Callable[..., Any]) -> set[str]:
    """Register tools and return all registered tool names.

    Args:
        register_fn: The register_*_tools function to call

    Returns:
        Set of all registered tool names
    """
    mcp = FastMCP("test")
    register_fn(mcp)
    tools = await mcp._list_tools()
    return {t.name for t in tools}
