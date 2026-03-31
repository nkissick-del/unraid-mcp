"""Tests for Docker organization tools."""

import pytest

from tests.helpers import get_registered_tool_names, get_tool_fn
from unraid_mcp.core.exceptions import ToolError
from unraid_mcp.tools.docker_organize import register_docker_organize_tools
from unraid_mcp.tools.queries.docker_organize import (
    CREATE_DOCKER_FOLDER_MUTATION,
    CREATE_DOCKER_FOLDER_WITH_ITEMS_MUTATION,
    DELETE_DOCKER_ENTRIES_MUTATION,
    MOVE_DOCKER_ENTRIES_TO_FOLDER_MUTATION,
    MOVE_DOCKER_ITEMS_TO_POSITION_MUTATION,
    REFRESH_DOCKER_DIGESTS_MUTATION,
    RENAME_DOCKER_FOLDER_MUTATION,
    RESET_DOCKER_TEMPLATE_MAPPINGS_MUTATION,
    SET_DOCKER_FOLDER_CHILDREN_MUTATION,
    SYNC_DOCKER_TEMPLATE_PATHS_MUTATION,
    UPDATE_DOCKER_VIEW_PREFERENCES_MUTATION,
)


class TestDockerOrganizeMutations:
    def test_create_folder_mutation(self):
        assert "mutation" in CREATE_DOCKER_FOLDER_MUTATION
        assert "$name" in CREATE_DOCKER_FOLDER_MUTATION
        assert "createDockerFolder" in CREATE_DOCKER_FOLDER_MUTATION

    def test_set_folder_children_mutation(self):
        assert "mutation" in SET_DOCKER_FOLDER_CHILDREN_MUTATION
        assert "$folderId" in SET_DOCKER_FOLDER_CHILDREN_MUTATION
        assert "$children" in SET_DOCKER_FOLDER_CHILDREN_MUTATION

    def test_delete_entries_mutation(self):
        assert "mutation" in DELETE_DOCKER_ENTRIES_MUTATION
        assert "$ids" in DELETE_DOCKER_ENTRIES_MUTATION
        assert "deleteDockerEntries" in DELETE_DOCKER_ENTRIES_MUTATION

    def test_move_entries_to_folder_mutation(self):
        assert "mutation" in MOVE_DOCKER_ENTRIES_TO_FOLDER_MUTATION
        assert "$folderId" in MOVE_DOCKER_ENTRIES_TO_FOLDER_MUTATION
        assert "$entryIds" in MOVE_DOCKER_ENTRIES_TO_FOLDER_MUTATION

    def test_move_items_to_position_mutation(self):
        assert "mutation" in MOVE_DOCKER_ITEMS_TO_POSITION_MUTATION
        assert "$itemIds" in MOVE_DOCKER_ITEMS_TO_POSITION_MUTATION
        assert "$position" in MOVE_DOCKER_ITEMS_TO_POSITION_MUTATION

    def test_rename_folder_mutation(self):
        assert "mutation" in RENAME_DOCKER_FOLDER_MUTATION
        assert "$folderId" in RENAME_DOCKER_FOLDER_MUTATION
        assert "$name" in RENAME_DOCKER_FOLDER_MUTATION

    def test_create_folder_with_items_mutation(self):
        assert "mutation" in CREATE_DOCKER_FOLDER_WITH_ITEMS_MUTATION
        assert "$name" in CREATE_DOCKER_FOLDER_WITH_ITEMS_MUTATION
        assert "$itemIds" in CREATE_DOCKER_FOLDER_WITH_ITEMS_MUTATION

    def test_update_view_preferences_mutation(self):
        assert "mutation" in UPDATE_DOCKER_VIEW_PREFERENCES_MUTATION
        assert "updateDockerViewPreferences" in UPDATE_DOCKER_VIEW_PREFERENCES_MUTATION

    def test_sync_template_paths_mutation(self):
        assert "mutation" in SYNC_DOCKER_TEMPLATE_PATHS_MUTATION
        assert "syncDockerTemplatePaths" in SYNC_DOCKER_TEMPLATE_PATHS_MUTATION

    def test_reset_template_mappings_mutation(self):
        assert "mutation" in RESET_DOCKER_TEMPLATE_MAPPINGS_MUTATION
        assert "resetDockerTemplateMappings" in RESET_DOCKER_TEMPLATE_MAPPINGS_MUTATION

    def test_refresh_digests_mutation(self):
        assert "mutation" in REFRESH_DOCKER_DIGESTS_MUTATION
        assert "refreshDockerDigests" in REFRESH_DOCKER_DIGESTS_MUTATION


class TestDeleteDockerEntriesConfirmGate:
    @pytest.mark.asyncio
    async def test_confirm_false_raises(self):
        tool_fn = await get_tool_fn(register_docker_organize_tools, "delete_docker_entries")
        with pytest.raises(ToolError, match="confirm must be True"):
            await tool_fn(ids=["entry1"], confirm=False)

    @pytest.mark.asyncio
    async def test_confirm_default_raises(self):
        tool_fn = await get_tool_fn(register_docker_organize_tools, "delete_docker_entries")
        with pytest.raises(ToolError, match="confirm must be True"):
            await tool_fn(ids=["entry1"])


class TestResetTemplateMappingsConfirmGate:
    @pytest.mark.asyncio
    async def test_confirm_false_raises(self):
        tool_fn = await get_tool_fn(
            register_docker_organize_tools, "reset_docker_template_mappings"
        )
        with pytest.raises(ToolError, match="confirm must be True"):
            await tool_fn(confirm=False)


class TestDockerOrganizeInputValidation:
    @pytest.mark.asyncio
    async def test_create_folder_empty_name_raises(self):
        tool_fn = await get_tool_fn(register_docker_organize_tools, "create_docker_folder")
        with pytest.raises(ToolError, match="non-empty string"):
            await tool_fn(name="")

    @pytest.mark.asyncio
    async def test_set_folder_children_empty_id_raises(self):
        tool_fn = await get_tool_fn(register_docker_organize_tools, "set_docker_folder_children")
        with pytest.raises(ToolError, match="non-empty string"):
            await tool_fn(folder_id="", children=["a"])

    @pytest.mark.asyncio
    async def test_view_preferences_empty_config_raises(self):
        tool_fn = await get_tool_fn(
            register_docker_organize_tools, "update_docker_view_preferences"
        )
        with pytest.raises(ToolError, match="non-empty dictionary"):
            await tool_fn(input_config={})


class TestDockerOrganizeToolRegistration:
    async def test_all_tools_registered(self):
        tool_names = await get_registered_tool_names(register_docker_organize_tools)
        expected = {
            "create_docker_folder",
            "set_docker_folder_children",
            "delete_docker_entries",
            "move_docker_entries_to_folder",
            "move_docker_items_to_position",
            "rename_docker_folder",
            "create_docker_folder_with_items",
            "update_docker_view_preferences",
            "sync_docker_template_paths",
            "reset_docker_template_mappings",
            "refresh_docker_digests",
        }
        assert expected.issubset(tool_names)
