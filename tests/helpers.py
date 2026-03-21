"""Shared test helpers to eliminate tool-lookup boilerplate."""

from collections.abc import Callable

from fastmcp import FastMCP


def get_tool_fn(register_fn: Callable, tool_name: str):
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
    for tool in mcp._tool_manager._tools.values():
        if tool.name == tool_name:
            return tool.fn
    raise AssertionError(f"Tool '{tool_name}' not found")


def get_registered_tool_names(register_fn: Callable) -> set[str]:
    """Register tools and return all registered tool names.

    Args:
        register_fn: The register_*_tools function to call

    Returns:
        Set of all registered tool names
    """
    mcp = FastMCP("test")
    register_fn(mcp)
    return set(mcp._tool_manager._tools.keys())
