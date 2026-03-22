"""Tests for custom exception classes."""

import pytest
from fastmcp.exceptions import ToolError as FastMCPToolError

from unraid_mcp.core.exceptions import (
    ToolError,
    ValidationError,
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
