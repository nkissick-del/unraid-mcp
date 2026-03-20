"""Tests for custom exception classes."""

import pytest
from fastmcp.exceptions import ToolError as FastMCPToolError

from unraid_mcp.core.exceptions import (
    ConfigurationError,
    SubscriptionError,
    ToolError,
    UnraidAPIError,
    ValidationError,
)


class TestExceptionInstantiation:
    @pytest.mark.parametrize(
        "exc_cls",
        [ToolError, ConfigurationError, UnraidAPIError, SubscriptionError, ValidationError],
    )
    def test_instantiable_with_message(self, exc_cls):
        exc = exc_cls("test message")
        assert str(exc) == "test message"

    @pytest.mark.parametrize(
        "exc_cls",
        [ConfigurationError, UnraidAPIError, SubscriptionError, ValidationError],
    )
    def test_inherits_from_tool_error(self, exc_cls):
        assert issubclass(exc_cls, ToolError)

    def test_tool_error_inherits_from_fastmcp(self):
        assert issubclass(ToolError, FastMCPToolError)

    def test_can_be_caught_as_tool_error(self):
        with pytest.raises(ToolError):
            raise ValidationError("bad input")

    def test_str_preserves_message(self):
        msg = "something went wrong with the API"
        assert str(UnraidAPIError(msg)) == msg
