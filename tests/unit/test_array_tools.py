"""Tests for array management tools."""

import pytest

from unraid_mcp.core.exceptions import ValidationError
from unraid_mcp.core.utils import validate_enum
from unraid_mcp.tools.queries.array import ARRAY_SET_STATE_MUTATION, ARRAY_STATUS_QUERY


class TestArrayQueryStrings:
    def test_set_state_mutation_has_input_variable(self):
        assert "$input" in ARRAY_SET_STATE_MUTATION
        assert "setState" in ARRAY_SET_STATE_MUTATION

    def test_set_state_mutation_returns_state(self):
        assert "state" in ARRAY_SET_STATE_MUTATION
        assert "capacity" in ARRAY_SET_STATE_MUTATION

    def test_status_query_has_status_field(self):
        assert "status" in ARRAY_STATUS_QUERY
        assert "state" in ARRAY_STATUS_QUERY

    def test_mutations_are_graphql(self):
        assert "mutation" in ARRAY_SET_STATE_MUTATION
        assert "query" in ARRAY_STATUS_QUERY


class TestArrayStateValidation:
    def test_start_is_valid(self):
        result = validate_enum("START", ["START", "STOP"], "desired_state")
        assert result == "START"

    def test_stop_is_valid(self):
        result = validate_enum("STOP", ["START", "STOP"], "desired_state")
        assert result == "STOP"

    def test_invalid_state_raises(self):
        with pytest.raises(ValidationError, match="Invalid desired_state"):
            validate_enum("RESTART", ["START", "STOP"], "desired_state")

    def test_lowercase_invalid(self):
        with pytest.raises(ValidationError):
            validate_enum("start", ["START", "STOP"], "desired_state")
