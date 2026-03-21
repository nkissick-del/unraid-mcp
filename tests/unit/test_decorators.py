"""Tests for tool_error_handler decorator."""

import logging

import pytest

from unraid_mcp.core.decorators import tool_error_handler
from unraid_mcp.core.exceptions import ToolError


class TestToolErrorHandler:
    @pytest.mark.asyncio
    async def test_successful_execution(self):
        @tool_error_handler("do something")
        async def my_tool():
            return {"result": "ok"}

        result = await my_tool()
        assert result == {"result": "ok"}

    @pytest.mark.asyncio
    async def test_tool_error_passthrough(self):
        @tool_error_handler("do something")
        async def my_tool():
            raise ToolError("specific tool error")

        with pytest.raises(ToolError, match="specific tool error"):
            await my_tool()

    @pytest.mark.asyncio
    async def test_generic_exception_wrapped(self):
        @tool_error_handler("fetch data")
        async def my_tool():
            raise ValueError("bad value")

        with pytest.raises(ToolError, match="Failed to fetch data: bad value"):
            await my_tool()

    @pytest.mark.asyncio
    async def test_exception_chaining(self):
        @tool_error_handler("fetch data")
        async def my_tool():
            raise RuntimeError("root cause")

        with pytest.raises(ToolError) as exc_info:
            await my_tool()
        assert isinstance(exc_info.value.__cause__, RuntimeError)

    @pytest.mark.asyncio
    async def test_preserves_function_name(self):
        @tool_error_handler("do something")
        async def my_special_tool():
            return {}

        assert my_special_tool.__name__ == "my_special_tool"

    @pytest.mark.asyncio
    async def test_preserves_docstring(self):
        @tool_error_handler("do something")
        async def my_tool():
            """My docstring."""
            return {}

        assert my_tool.__doc__ == "My docstring."

    @pytest.mark.asyncio
    async def test_logs_execution(self, caplog):
        @tool_error_handler("do something")
        async def my_tool():
            return {}

        with caplog.at_level(logging.INFO, logger="unraid_mcp.core.decorators"):
            await my_tool()
        assert "Executing my_tool" in caplog.text

    @pytest.mark.asyncio
    async def test_logs_error(self, caplog):
        @tool_error_handler("do something")
        async def my_tool():
            raise RuntimeError("boom")

        with caplog.at_level(logging.ERROR, logger="unraid_mcp.core.decorators"):
            with pytest.raises(ToolError):
                await my_tool()
        assert "Error in my_tool: boom" in caplog.text

    @pytest.mark.asyncio
    async def test_passes_args_and_kwargs(self):
        @tool_error_handler("do something")
        async def my_tool(a, b, c=None):
            return {"a": a, "b": b, "c": c}

        result = await my_tool(1, 2, c=3)
        assert result == {"a": 1, "b": 2, "c": 3}
