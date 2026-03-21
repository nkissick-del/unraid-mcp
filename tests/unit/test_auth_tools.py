"""Tests for auth and API key management tools."""

import pytest

from tests.helpers import get_registered_tool_names, get_tool_fn
from unraid_mcp.core.exceptions import ToolError
from unraid_mcp.tools.auth import register_auth_tools
from unraid_mcp.tools.queries.auth import (
    ADD_ROLE_TO_API_KEY_MUTATION,
    CREATE_API_KEY_MUTATION,
    DELETE_API_KEY_MUTATION,
    GET_API_KEY_CREATION_FORM_SCHEMA_QUERY,
    GET_API_KEY_POSSIBLE_PERMISSIONS_QUERY,
    GET_API_KEY_POSSIBLE_ROLES_QUERY,
    GET_API_KEY_QUERY,
    GET_AVAILABLE_AUTH_ACTIONS_QUERY,
    GET_PERMISSIONS_FOR_ROLES_QUERY,
    LIST_API_KEYS_QUERY,
    PREVIEW_EFFECTIVE_PERMISSIONS_QUERY,
    REMOVE_ROLE_FROM_API_KEY_MUTATION,
    UPDATE_API_KEY_MUTATION,
)


class TestAuthQueries:
    def test_list_api_keys_query(self):
        assert "query" in LIST_API_KEYS_QUERY
        assert "apiKeys" in LIST_API_KEYS_QUERY

    def test_list_api_keys_has_expected_fields(self):
        assert "name" in LIST_API_KEYS_QUERY
        assert "roles" in LIST_API_KEYS_QUERY
        assert "createdAt" in LIST_API_KEYS_QUERY

    def test_get_api_key_query(self):
        assert "query" in GET_API_KEY_QUERY
        assert "$keyId" in GET_API_KEY_QUERY
        assert "apiKey" in GET_API_KEY_QUERY

    def test_get_api_key_has_expected_fields(self):
        assert "permissions" in GET_API_KEY_QUERY
        assert "lastUsedAt" in GET_API_KEY_QUERY

    def test_get_possible_roles_query(self):
        assert "query" in GET_API_KEY_POSSIBLE_ROLES_QUERY
        assert "apiKeyPossibleRoles" in GET_API_KEY_POSSIBLE_ROLES_QUERY

    def test_get_possible_permissions_query(self):
        assert "query" in GET_API_KEY_POSSIBLE_PERMISSIONS_QUERY
        assert "apiKeyPossiblePermissions" in GET_API_KEY_POSSIBLE_PERMISSIONS_QUERY

    def test_get_permissions_for_roles_query(self):
        assert "query" in GET_PERMISSIONS_FOR_ROLES_QUERY
        assert "$roles" in GET_PERMISSIONS_FOR_ROLES_QUERY
        assert "permissionsForRoles" in GET_PERMISSIONS_FOR_ROLES_QUERY

    def test_preview_effective_permissions_query(self):
        assert "query" in PREVIEW_EFFECTIVE_PERMISSIONS_QUERY
        assert "$input" in PREVIEW_EFFECTIVE_PERMISSIONS_QUERY
        assert "previewEffectivePermissions" in PREVIEW_EFFECTIVE_PERMISSIONS_QUERY

    def test_get_available_auth_actions_query(self):
        assert "query" in GET_AVAILABLE_AUTH_ACTIONS_QUERY
        assert "availableAuthActions" in GET_AVAILABLE_AUTH_ACTIONS_QUERY

    def test_get_api_key_creation_form_schema_query(self):
        assert "query" in GET_API_KEY_CREATION_FORM_SCHEMA_QUERY
        assert "apiKeyCreationFormSchema" in GET_API_KEY_CREATION_FORM_SCHEMA_QUERY


class TestAuthMutations:
    def test_create_api_key_mutation(self):
        assert "mutation" in CREATE_API_KEY_MUTATION
        assert "$input" in CREATE_API_KEY_MUTATION
        assert "createApiKey" in CREATE_API_KEY_MUTATION
        assert "key" in CREATE_API_KEY_MUTATION

    def test_add_role_mutation(self):
        assert "mutation" in ADD_ROLE_TO_API_KEY_MUTATION
        assert "$input" in ADD_ROLE_TO_API_KEY_MUTATION
        assert "addRoleToApiKey" in ADD_ROLE_TO_API_KEY_MUTATION

    def test_remove_role_mutation(self):
        assert "mutation" in REMOVE_ROLE_FROM_API_KEY_MUTATION
        assert "$input" in REMOVE_ROLE_FROM_API_KEY_MUTATION
        assert "removeRoleFromApiKey" in REMOVE_ROLE_FROM_API_KEY_MUTATION

    def test_delete_api_key_mutation(self):
        assert "mutation" in DELETE_API_KEY_MUTATION
        assert "$keyId" in DELETE_API_KEY_MUTATION
        assert "deleteApiKey" in DELETE_API_KEY_MUTATION

    def test_update_api_key_mutation(self):
        assert "mutation" in UPDATE_API_KEY_MUTATION
        assert "$input" in UPDATE_API_KEY_MUTATION
        assert "updateApiKey" in UPDATE_API_KEY_MUTATION


class TestAuthConfirmGates:
    @pytest.mark.parametrize(
        "tool_name",
        [
            "create_api_key",
            "add_role_to_api_key",
            "remove_role_from_api_key",
            "delete_api_key",
            "update_api_key",
        ],
    )
    @pytest.mark.asyncio
    async def test_confirm_false_raises(self, tool_name):
        tool_fn = get_tool_fn(register_auth_tools, tool_name)

        if tool_name == "delete_api_key":
            with pytest.raises(ToolError, match="confirm must be True"):
                await tool_fn(key_id="test-key-id", confirm=False)
        else:
            with pytest.raises(ToolError, match="confirm must be True"):
                await tool_fn(input_config={"key": "value"}, confirm=False)


class TestAuthInputValidation:
    @pytest.mark.asyncio
    async def test_get_api_key_empty_id_raises(self):
        tool_fn = get_tool_fn(register_auth_tools, "get_api_key")
        with pytest.raises(ToolError, match="non-empty string"):
            await tool_fn(key_id="")

    @pytest.mark.asyncio
    async def test_get_permissions_for_roles_empty_raises(self):
        tool_fn = get_tool_fn(register_auth_tools, "get_permissions_for_roles")
        with pytest.raises(ToolError, match="non-empty list"):
            await tool_fn(roles=[])

    @pytest.mark.asyncio
    async def test_preview_permissions_empty_config_raises(self):
        tool_fn = get_tool_fn(register_auth_tools, "preview_effective_permissions")
        with pytest.raises(ToolError, match="non-empty dictionary"):
            await tool_fn(input_config={})

    @pytest.mark.asyncio
    async def test_delete_api_key_empty_id_raises(self):
        tool_fn = get_tool_fn(register_auth_tools, "delete_api_key")
        with pytest.raises(ToolError, match="non-empty string"):
            await tool_fn(key_id="", confirm=True)


class TestAuthToolRegistration:
    def test_all_tools_registered(self):
        tool_names = get_registered_tool_names(register_auth_tools)
        expected = {
            "list_api_keys",
            "get_api_key",
            "get_api_key_possible_roles",
            "get_api_key_possible_permissions",
            "get_permissions_for_roles",
            "preview_effective_permissions",
            "get_available_auth_actions",
            "get_api_key_creation_form_schema",
            "create_api_key",
            "add_role_to_api_key",
            "remove_role_from_api_key",
            "delete_api_key",
            "update_api_key",
        }
        assert expected.issubset(tool_names)
