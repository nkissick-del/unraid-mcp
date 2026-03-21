"""Tests for Docker mutation extensions (pause/unpause, remove, update, logs)."""

import pytest

from tests.helpers import get_tool_fn
from unraid_mcp.core.client import is_idempotent_error
from unraid_mcp.core.exceptions import ToolError
from unraid_mcp.tools.docker_admin import register_docker_admin_tools
from unraid_mcp.tools.queries.docker import (
    DOCKER_ACTION_MUTATIONS,
    DOCKER_LOGS_QUERY,
    DOCKER_REMOVE_CONTAINER_MUTATION,
    DOCKER_UPDATE_CONTAINER_MUTATION,
)


class TestPauseUnpauseInActionDict:
    def test_pause_action_exists(self):
        assert "pause" in DOCKER_ACTION_MUTATIONS

    def test_unpause_action_exists(self):
        assert "unpause" in DOCKER_ACTION_MUTATIONS

    def test_all_actions_present(self):
        assert set(DOCKER_ACTION_MUTATIONS.keys()) == {
            "start",
            "stop",
            "pause",
            "unpause",
        }

    def test_pause_mutation_contains_graphql_keyword(self):
        assert "mutation" in DOCKER_ACTION_MUTATIONS["pause"]
        assert "pause" in DOCKER_ACTION_MUTATIONS["pause"]

    def test_unpause_mutation_contains_graphql_keyword(self):
        assert "mutation" in DOCKER_ACTION_MUTATIONS["unpause"]
        assert "unpause" in DOCKER_ACTION_MUTATIONS["unpause"]


class TestIdempotentErrorExtensions:
    def test_pause_already_paused(self):
        assert is_idempotent_error("Container already paused", "pause") is True

    def test_pause_304(self):
        assert is_idempotent_error("HTTP code 304", "pause") is True

    def test_pause_unrelated(self):
        assert is_idempotent_error("Something went wrong", "pause") is False

    def test_unpause_not_paused(self):
        assert is_idempotent_error("Container not paused", "unpause") is True

    def test_unpause_304(self):
        assert is_idempotent_error("HTTP code 304", "unpause") is True

    def test_unpause_unrelated(self):
        assert is_idempotent_error("Something went wrong", "unpause") is False


class TestDockerQueryStrings:
    def test_remove_mutation_has_variables(self):
        assert "$id" in DOCKER_REMOVE_CONTAINER_MUTATION
        assert "$withImage" in DOCKER_REMOVE_CONTAINER_MUTATION
        assert "removeContainer" in DOCKER_REMOVE_CONTAINER_MUTATION

    def test_update_mutation_has_variables(self):
        assert "$id" in DOCKER_UPDATE_CONTAINER_MUTATION
        assert "updateContainer" in DOCKER_UPDATE_CONTAINER_MUTATION

    def test_logs_query_has_variables(self):
        assert "$id" in DOCKER_LOGS_QUERY
        assert "$since" in DOCKER_LOGS_QUERY
        assert "$tail" in DOCKER_LOGS_QUERY
        assert "logs" in DOCKER_LOGS_QUERY


class TestRemoveContainerConfirmGate:
    @pytest.mark.asyncio
    async def test_confirm_false_raises(self):
        """remove_docker_container must raise when confirm is False."""
        tool_fn = get_tool_fn(register_docker_admin_tools, "remove_docker_container")
        with pytest.raises(ToolError, match="confirm must be True"):
            await tool_fn("test-container", with_image=False, confirm=False)
