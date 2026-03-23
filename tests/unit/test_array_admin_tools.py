"""Tests for array disk administration tools."""

import pytest

from tests.helpers import get_registered_tool_names, get_tool_fn
from unraid_mcp.core.exceptions import ToolError
from unraid_mcp.tools.array_admin import register_array_admin_tools
from unraid_mcp.tools.queries.array_admin import (
    ADD_DISK_TO_ARRAY_MUTATION,
    CLEAR_ARRAY_DISK_STATISTICS_MUTATION,
    LIST_ASSIGNABLE_DISKS_QUERY,
    MOUNT_ARRAY_DISK_MUTATION,
    REMOVE_DISK_FROM_ARRAY_MUTATION,
    UNMOUNT_ARRAY_DISK_MUTATION,
)


class TestArrayAdminQueries:
    def test_list_assignable_disks_query(self):
        assert "query" in LIST_ASSIGNABLE_DISKS_QUERY
        assert "assignableDisks" in LIST_ASSIGNABLE_DISKS_QUERY

    def test_list_assignable_disks_has_expected_fields(self):
        assert "name" in LIST_ASSIGNABLE_DISKS_QUERY
        assert "device" in LIST_ASSIGNABLE_DISKS_QUERY
        assert "size" in LIST_ASSIGNABLE_DISKS_QUERY
        assert "serialNum" in LIST_ASSIGNABLE_DISKS_QUERY


class TestArrayAdminMutations:
    def test_add_disk_mutation(self):
        assert "mutation" in ADD_DISK_TO_ARRAY_MUTATION
        assert "$input" in ADD_DISK_TO_ARRAY_MUTATION
        assert "array" in ADD_DISK_TO_ARRAY_MUTATION
        assert "addDiskToArray" in ADD_DISK_TO_ARRAY_MUTATION

    def test_remove_disk_mutation(self):
        assert "mutation" in REMOVE_DISK_FROM_ARRAY_MUTATION
        assert "$input" in REMOVE_DISK_FROM_ARRAY_MUTATION
        assert "array" in REMOVE_DISK_FROM_ARRAY_MUTATION
        assert "removeDiskFromArray" in REMOVE_DISK_FROM_ARRAY_MUTATION

    def test_mount_disk_mutation(self):
        assert "mutation" in MOUNT_ARRAY_DISK_MUTATION
        assert "$id" in MOUNT_ARRAY_DISK_MUTATION
        assert "PrefixedID" in MOUNT_ARRAY_DISK_MUTATION
        assert "array" in MOUNT_ARRAY_DISK_MUTATION
        assert "mountArrayDisk" in MOUNT_ARRAY_DISK_MUTATION

    def test_unmount_disk_mutation(self):
        assert "mutation" in UNMOUNT_ARRAY_DISK_MUTATION
        assert "$id" in UNMOUNT_ARRAY_DISK_MUTATION
        assert "PrefixedID" in UNMOUNT_ARRAY_DISK_MUTATION
        assert "array" in UNMOUNT_ARRAY_DISK_MUTATION
        assert "unmountArrayDisk" in UNMOUNT_ARRAY_DISK_MUTATION

    def test_clear_statistics_mutation(self):
        assert "mutation" in CLEAR_ARRAY_DISK_STATISTICS_MUTATION
        assert "$id" in CLEAR_ARRAY_DISK_STATISTICS_MUTATION
        assert "PrefixedID" in CLEAR_ARRAY_DISK_STATISTICS_MUTATION
        assert "array" in CLEAR_ARRAY_DISK_STATISTICS_MUTATION
        assert "clearArrayDiskStatistics" in CLEAR_ARRAY_DISK_STATISTICS_MUTATION


class TestArrayAdminConfirmGates:
    @pytest.mark.parametrize(
        "tool_name",
        [
            "add_disk_to_array",
            "remove_disk_from_array",
            "mount_array_disk",
            "unmount_array_disk",
            "clear_array_disk_statistics",
        ],
    )
    @pytest.mark.asyncio
    async def test_confirm_false_raises(self, tool_name):
        tool_fn = get_tool_fn(register_array_admin_tools, tool_name)
        with pytest.raises(ToolError, match="confirm must be True"):
            await tool_fn(input_config={"id": "test-disk"}, confirm=False)


class TestArrayAdminExtraStrongWarnings:
    @pytest.mark.asyncio
    async def test_add_disk_warns_extremely_destructive(self):
        tool_fn = get_tool_fn(register_array_admin_tools, "add_disk_to_array")
        with pytest.raises(ToolError, match="EXTREMELY DESTRUCTIVE"):
            await tool_fn(input_config={"id": "test-disk"}, confirm=False)

    @pytest.mark.asyncio
    async def test_remove_disk_warns_extremely_destructive(self):
        tool_fn = get_tool_fn(register_array_admin_tools, "remove_disk_from_array")
        with pytest.raises(ToolError, match="EXTREMELY DESTRUCTIVE"):
            await tool_fn(input_config={"id": "test-disk"}, confirm=False)


class TestArrayAdminInputValidation:
    @pytest.mark.parametrize(
        "tool_name",
        [
            "add_disk_to_array",
            "remove_disk_from_array",
            "mount_array_disk",
            "unmount_array_disk",
            "clear_array_disk_statistics",
        ],
    )
    @pytest.mark.asyncio
    async def test_empty_config_raises(self, tool_name):
        tool_fn = get_tool_fn(register_array_admin_tools, tool_name)
        with pytest.raises(ToolError, match="non-empty dictionary"):
            await tool_fn(input_config={}, confirm=True)


class TestArrayAdminToolRegistration:
    def test_all_tools_registered(self):
        tool_names = get_registered_tool_names(register_array_admin_tools)
        expected = {
            "list_assignable_disks",
            "add_disk_to_array",
            "remove_disk_from_array",
            "mount_array_disk",
            "unmount_array_disk",
            "clear_array_disk_statistics",
        }
        assert expected.issubset(tool_names)
