"""Tests for parity check management tools."""

import pytest

from unraid_mcp.core.constants import PARITY_CHECK_ACTIONS
from unraid_mcp.core.exceptions import ValidationError
from unraid_mcp.core.utils import validate_enum
from unraid_mcp.tools.queries.parity import PARITY_CHECK_MUTATIONS, PARITY_STATUS_QUERY


class TestParityMutationStrings:
    def test_all_actions_present_in_mutations_dict(self):
        for action in PARITY_CHECK_ACTIONS:
            assert action in PARITY_CHECK_MUTATIONS

    def test_start_mutation_has_correct_variable(self):
        assert "$correct" in PARITY_CHECK_MUTATIONS["START"]
        assert "Boolean!" in PARITY_CHECK_MUTATIONS["START"]

    def test_pause_mutation_no_variables(self):
        assert "$" not in PARITY_CHECK_MUTATIONS["PAUSE"]

    def test_resume_mutation_no_variables(self):
        assert "$" not in PARITY_CHECK_MUTATIONS["RESUME"]

    def test_cancel_mutation_no_variables(self):
        assert "$" not in PARITY_CHECK_MUTATIONS["CANCEL"]

    def test_all_mutations_are_graphql(self):
        for action, mutation in PARITY_CHECK_MUTATIONS.items():
            assert "mutation" in mutation, f"{action} mutation missing 'mutation' keyword"

    def test_all_mutations_contain_return_fields(self):
        for action, mutation in PARITY_CHECK_MUTATIONS.items():
            assert "state" in mutation, f"{action} mutation missing 'state' field"
            assert "progress" in mutation, f"{action} mutation missing 'progress' field"
            assert "errors" in mutation, f"{action} mutation missing 'errors' field"

    def test_all_mutations_nested_under_parity_check(self):
        for action, mutation in PARITY_CHECK_MUTATIONS.items():
            assert "parityCheck" in mutation, f"{action} mutation missing 'parityCheck' namespace"


class TestParityStatusQuery:
    def test_status_query_is_graphql(self):
        assert "query" in PARITY_STATUS_QUERY

    def test_status_query_has_array_fields(self):
        assert "array" in PARITY_STATUS_QUERY
        assert "state" in PARITY_STATUS_QUERY


class TestParityActionValidation:
    @pytest.mark.parametrize("action", PARITY_CHECK_ACTIONS)
    def test_valid_actions_accepted(self, action: str):
        result = validate_enum(action, PARITY_CHECK_ACTIONS, "action")
        assert result == action

    def test_invalid_action_raises(self):
        with pytest.raises(ValidationError, match="Invalid action"):
            validate_enum("RESTART", PARITY_CHECK_ACTIONS, "action")

    def test_lowercase_action_raises(self):
        with pytest.raises(ValidationError):
            validate_enum("start", PARITY_CHECK_ACTIONS, "action")
