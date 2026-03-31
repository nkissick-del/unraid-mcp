"""Tests for custom exception classes."""

import logging

import pytest
from fastmcp.exceptions import ToolError as FastMCPToolError

from unraid_mcp.core.exceptions import (
    ToolError,
    ValidationError,
    tool_error_handler,
)


class TestExceptionInstantiation:
    @pytest.mark.parametrize(
        "exc_cls",
        [ToolError, ValidationError],
    )
    def test_instantiable_with_message(self, exc_cls):
        exc = exc_cls("test message")
        assert str(exc) == "test message"

    def test_validation_error_inherits_from_tool_error(self):
        assert issubclass(ValidationError, ToolError)

    def test_tool_error_inherits_from_fastmcp(self):
        assert issubclass(ToolError, FastMCPToolError)

    def test_can_be_caught_as_tool_error(self):
        with pytest.raises(ToolError):
            raise ValidationError("bad input")

    def test_str_preserves_message(self):
        msg = "something went wrong with the API"
        assert str(ValidationError(msg)) == msg


class TestToolErrorHandler:
    def test_tool_error_passes_through(self):
        with pytest.raises(ToolError, match="custom error"):
            with tool_error_handler("test_tool", "test_action", logging.getLogger()):
                raise ToolError("custom error")

    def test_timeout_gets_descriptive_message(self):
        with pytest.raises(ToolError, match="timed out"):
            with tool_error_handler("my_tool", "fetch_data", logging.getLogger()):
                raise TimeoutError("connection timed out")

    def test_generic_exception_is_sanitized(self):
        with pytest.raises(ToolError, match="failed.*check server logs"):
            with tool_error_handler("my_tool", "query", logging.getLogger()):
                raise RuntimeError("internal details that should not leak")

    def test_generic_exception_logs_full_traceback(self, caplog):
        with caplog.at_level(logging.ERROR):
            with pytest.raises(ToolError):
                with tool_error_handler("my_tool", "query", logging.getLogger()):
                    raise RuntimeError("secret internal error")
        assert "secret internal error" in caplog.text

    def test_no_exception_passes_through(self):
        with tool_error_handler("test_tool", "test_action", logging.getLogger()):
            pass
