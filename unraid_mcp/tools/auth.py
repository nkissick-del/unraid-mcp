"""API key and authentication management tools.

This module is gated under the 'auth' module and disabled by default.
It provides tools for managing API keys, roles, and permissions.
"""

from typing import Any

from fastmcp import FastMCP

from ..config.logging import logger
from ..core.client import make_graphql_request
from ..core.decorators import tool_error_handler
from ..core.exceptions import ToolError
from ..core.utils import ensure_dict, ensure_list, require_confirm, validate_input_dict
from .queries.auth import (
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


def register_auth_tools(mcp: FastMCP) -> None:
    """Register auth tools with the FastMCP instance."""

    @mcp.tool()
    @tool_error_handler("list API keys")
    async def list_api_keys() -> dict[str, Any]:
        """Lists all API keys with their names, roles, and usage info."""
        response = await make_graphql_request(LIST_API_KEYS_QUERY)
        keys = ensure_list(response.get("apiKeys", []))
        return {"count": len(keys), "apiKeys": keys}

    @mcp.tool()
    @tool_error_handler("get API key")
    async def get_api_key(key_id: str) -> dict[str, Any]:
        """Gets details of a specific API key including permissions.

        Args:
            key_id: The ID of the API key to retrieve
        """
        if not key_id or not isinstance(key_id, str):
            raise ToolError("key_id must be a non-empty string")

        variables: dict[str, Any] = {"keyId": key_id}
        response = await make_graphql_request(GET_API_KEY_QUERY, variables)
        return ensure_dict(response.get("apiKey", {}))

    @mcp.tool()
    @tool_error_handler("get possible roles")
    async def get_api_key_possible_roles() -> dict[str, Any]:
        """Lists all possible roles that can be assigned to API keys."""
        response = await make_graphql_request(GET_API_KEY_POSSIBLE_ROLES_QUERY)
        roles = ensure_list(response.get("apiKeyPossibleRoles", []))
        return {"count": len(roles), "roles": roles}

    @mcp.tool()
    @tool_error_handler("get possible permissions")
    async def get_api_key_possible_permissions() -> dict[str, Any]:
        """Lists all possible permissions that can be granted to API keys."""
        response = await make_graphql_request(GET_API_KEY_POSSIBLE_PERMISSIONS_QUERY)
        permissions = ensure_list(response.get("apiKeyPossiblePermissions", []))
        return {"count": len(permissions), "permissions": permissions}

    @mcp.tool()
    @tool_error_handler("get permissions for roles")
    async def get_permissions_for_roles(
        roles: list[str],
    ) -> dict[str, Any]:
        """Gets the effective permissions for a given set of roles.

        Args:
            roles: List of role names to get permissions for
        """
        if not roles or not isinstance(roles, list):
            raise ToolError("roles must be a non-empty list of strings")

        variables: dict[str, Any] = {"roles": roles}
        response = await make_graphql_request(GET_PERMISSIONS_FOR_ROLES_QUERY, variables)
        permissions = ensure_list(response.get("permissionsForRoles", []))
        return {"count": len(permissions), "permissions": permissions}

    @mcp.tool()
    @tool_error_handler("preview effective permissions")
    async def preview_effective_permissions(
        input_config: dict[str, Any],
    ) -> dict[str, Any]:
        """Previews the effective permissions that would result from a given configuration.

        Args:
            input_config: Dict describing the roles/permissions to preview
        """
        validate_input_dict(input_config)

        variables: dict[str, Any] = {"input": input_config}
        response = await make_graphql_request(PREVIEW_EFFECTIVE_PERMISSIONS_QUERY, variables)
        permissions = ensure_list(response.get("previewEffectivePermissions", []))
        return {"count": len(permissions), "permissions": permissions}

    @mcp.tool()
    @tool_error_handler("get available auth actions")
    async def get_available_auth_actions() -> dict[str, Any]:
        """Lists all available authentication actions."""
        response = await make_graphql_request(GET_AVAILABLE_AUTH_ACTIONS_QUERY)
        actions = ensure_list(response.get("availableAuthActions", []))
        return {"count": len(actions), "actions": actions}

    @mcp.tool()
    @tool_error_handler("get API key creation schema")
    async def get_api_key_creation_form_schema() -> dict[str, Any]:
        """Gets the form schema for creating a new API key."""
        response = await make_graphql_request(GET_API_KEY_CREATION_FORM_SCHEMA_QUERY)
        return ensure_dict(response.get("apiKeyCreationFormSchema", {}))

    @mcp.tool()
    @tool_error_handler("create API key")
    async def create_api_key(input_config: dict[str, Any], confirm: bool = False) -> dict[str, Any]:
        """Creates a new API key. Requires confirm=True.

        WARNING: The API key value is returned only once and cannot be retrieved later.
        Store it securely immediately after creation.

        Args:
            input_config: Dict with API key configuration (name, roles, etc.)
            confirm: Safety gate - must be True to proceed
        """
        require_confirm(confirm, "create an API key")
        validate_input_dict(input_config)

        variables: dict[str, Any] = {"input": input_config}
        response = await make_graphql_request(CREATE_API_KEY_MUTATION, variables)
        result = response.get("createApiKey")
        if not result:
            raise ToolError("Failed to create API key")
        # Log only redacted key info
        key_value = result.get("key", "")
        if key_value and len(key_value) > 8:
            logger.info(f"API key created: {result.get('name')} (key: {key_value[:8]}...redacted)")
        elif key_value:
            logger.info(f"API key created: {result.get('name')} (key: [redacted])")
        return {
            "success": True,
            "apiKey": result,
            "message": "API key created. Store the key value securely — it cannot be retrieved later.",
        }

    @mcp.tool()
    @tool_error_handler("add role to API key")
    async def add_role_to_api_key(
        input_config: dict[str, Any], confirm: bool = False
    ) -> dict[str, Any]:
        """Adds a role to an existing API key. Requires confirm=True.

        Args:
            input_config: Dict with keyId and role to add
            confirm: Safety gate - must be True to proceed
        """
        require_confirm(confirm, "add a role to an API key")
        validate_input_dict(input_config)

        variables: dict[str, Any] = {"input": input_config}
        response = await make_graphql_request(ADD_ROLE_TO_API_KEY_MUTATION, variables)
        result = response.get("addRoleToApiKey")
        if not result:
            raise ToolError("Failed to add role to API key")
        return {
            "success": True,
            "apiKey": result,
            "message": "Role added to API key",
        }

    @mcp.tool()
    @tool_error_handler("remove role from API key")
    async def remove_role_from_api_key(
        input_config: dict[str, Any], confirm: bool = False
    ) -> dict[str, Any]:
        """Removes a role from an existing API key. Requires confirm=True.

        Args:
            input_config: Dict with keyId and role to remove
            confirm: Safety gate - must be True to proceed
        """
        require_confirm(confirm, "remove a role from an API key")
        validate_input_dict(input_config)

        variables: dict[str, Any] = {"input": input_config}
        response = await make_graphql_request(REMOVE_ROLE_FROM_API_KEY_MUTATION, variables)
        result = response.get("removeRoleFromApiKey")
        if not result:
            raise ToolError("Failed to remove role from API key")
        return {
            "success": True,
            "apiKey": result,
            "message": "Role removed from API key",
        }

    @mcp.tool()
    @tool_error_handler("delete API key")
    async def delete_api_key(key_id: str, confirm: bool = False) -> dict[str, Any]:
        """Deletes an API key permanently. Requires confirm=True.

        Args:
            key_id: ID of the API key to delete
            confirm: Safety gate - must be True to proceed
        """
        require_confirm(confirm, "delete an API key")

        if not key_id or not isinstance(key_id, str):
            raise ToolError("key_id must be a non-empty string")

        variables: dict[str, Any] = {"keyId": key_id}
        response = await make_graphql_request(DELETE_API_KEY_MUTATION, variables)
        result = response.get("deleteApiKey", {})
        success = result.get("success", False)
        if not success:
            raise ToolError(f"Failed to delete API key {key_id}")
        return {
            "success": True,
            "message": f"API key {key_id} deleted",
        }

    @mcp.tool()
    @tool_error_handler("update API key")
    async def update_api_key(input_config: dict[str, Any], confirm: bool = False) -> dict[str, Any]:
        """Updates an existing API key's configuration. Requires confirm=True.

        Args:
            input_config: Dict with API key update fields (id, name, description, etc.)
            confirm: Safety gate - must be True to proceed
        """
        require_confirm(confirm, "update an API key")
        validate_input_dict(input_config)

        variables: dict[str, Any] = {"input": input_config}
        response = await make_graphql_request(UPDATE_API_KEY_MUTATION, variables)
        result = response.get("updateApiKey")
        if not result:
            raise ToolError("Failed to update API key")
        return {
            "success": True,
            "apiKey": result,
            "message": "API key updated",
        }

    logger.info("Auth tools registered successfully")
