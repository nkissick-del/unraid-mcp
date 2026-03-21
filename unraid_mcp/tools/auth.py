"""API key and authentication management tools.

This module is gated under the 'auth' module and disabled by default.
It provides tools for managing API keys, roles, and permissions.
"""

from typing import Any

from fastmcp import FastMCP

from ..config.logging import logger
from ..core.client import make_graphql_request
from ..core.exceptions import ToolError
from ..core.utils import ensure_dict, ensure_list
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
    async def list_api_keys() -> dict[str, Any]:
        """Lists all API keys with their names, roles, and usage info."""
        try:
            logger.info("Executing list_api_keys")
            response = await make_graphql_request(LIST_API_KEYS_QUERY)
            keys = ensure_list(response.get("apiKeys", []))
            return {"count": len(keys), "apiKeys": keys}
        except Exception as e:
            logger.error(f"Error in list_api_keys: {e}", exc_info=True)
            raise ToolError(f"Failed to list API keys: {str(e)}") from e

    @mcp.tool()
    async def get_api_key(key_id: str) -> dict[str, Any]:
        """Gets details of a specific API key including permissions.

        Args:
            key_id: The ID of the API key to retrieve
        """
        if not key_id or not isinstance(key_id, str):
            raise ToolError("key_id must be a non-empty string")

        try:
            logger.info(f"Executing get_api_key: {key_id}")
            variables: dict[str, Any] = {"keyId": key_id}
            response = await make_graphql_request(GET_API_KEY_QUERY, variables)
            return ensure_dict(response.get("apiKey", {}))
        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in get_api_key: {e}", exc_info=True)
            raise ToolError(f"Failed to get API key: {str(e)}") from e

    @mcp.tool()
    async def get_api_key_possible_roles() -> dict[str, Any]:
        """Lists all possible roles that can be assigned to API keys."""
        try:
            logger.info("Executing get_api_key_possible_roles")
            response = await make_graphql_request(GET_API_KEY_POSSIBLE_ROLES_QUERY)
            roles = ensure_list(response.get("apiKeyPossibleRoles", []))
            return {"count": len(roles), "roles": roles}
        except Exception as e:
            logger.error(f"Error in get_api_key_possible_roles: {e}", exc_info=True)
            raise ToolError(f"Failed to get possible roles: {str(e)}") from e

    @mcp.tool()
    async def get_api_key_possible_permissions() -> dict[str, Any]:
        """Lists all possible permissions that can be granted to API keys."""
        try:
            logger.info("Executing get_api_key_possible_permissions")
            response = await make_graphql_request(GET_API_KEY_POSSIBLE_PERMISSIONS_QUERY)
            permissions = ensure_list(response.get("apiKeyPossiblePermissions", []))
            return {"count": len(permissions), "permissions": permissions}
        except Exception as e:
            logger.error(
                f"Error in get_api_key_possible_permissions: {e}",
                exc_info=True,
            )
            raise ToolError(f"Failed to get possible permissions: {str(e)}") from e

    @mcp.tool()
    async def get_permissions_for_roles(
        roles: list[str],
    ) -> dict[str, Any]:
        """Gets the effective permissions for a given set of roles.

        Args:
            roles: List of role names to get permissions for
        """
        if not roles or not isinstance(roles, list):
            raise ToolError("roles must be a non-empty list of strings")

        try:
            logger.info(f"Executing get_permissions_for_roles: {roles}")
            variables: dict[str, Any] = {"roles": roles}
            response = await make_graphql_request(GET_PERMISSIONS_FOR_ROLES_QUERY, variables)
            permissions = ensure_list(response.get("permissionsForRoles", []))
            return {"count": len(permissions), "permissions": permissions}
        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in get_permissions_for_roles: {e}", exc_info=True)
            raise ToolError(f"Failed to get permissions for roles: {str(e)}") from e

    @mcp.tool()
    async def preview_effective_permissions(
        input_config: dict[str, Any],
    ) -> dict[str, Any]:
        """Previews the effective permissions that would result from a given configuration.

        Args:
            input_config: Dict describing the roles/permissions to preview
        """
        if not input_config or not isinstance(input_config, dict):
            raise ToolError("input_config must be a non-empty dictionary")

        try:
            logger.info("Executing preview_effective_permissions")
            variables: dict[str, Any] = {"input": input_config}
            response = await make_graphql_request(PREVIEW_EFFECTIVE_PERMISSIONS_QUERY, variables)
            permissions = ensure_list(response.get("previewEffectivePermissions", []))
            return {"count": len(permissions), "permissions": permissions}
        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in preview_effective_permissions: {e}", exc_info=True)
            raise ToolError(f"Failed to preview effective permissions: {str(e)}") from e

    @mcp.tool()
    async def get_available_auth_actions() -> dict[str, Any]:
        """Lists all available authentication actions."""
        try:
            logger.info("Executing get_available_auth_actions")
            response = await make_graphql_request(GET_AVAILABLE_AUTH_ACTIONS_QUERY)
            actions = ensure_list(response.get("availableAuthActions", []))
            return {"count": len(actions), "actions": actions}
        except Exception as e:
            logger.error(f"Error in get_available_auth_actions: {e}", exc_info=True)
            raise ToolError(f"Failed to get available auth actions: {str(e)}") from e

    @mcp.tool()
    async def get_api_key_creation_form_schema() -> dict[str, Any]:
        """Gets the form schema for creating a new API key."""
        try:
            logger.info("Executing get_api_key_creation_form_schema")
            response = await make_graphql_request(GET_API_KEY_CREATION_FORM_SCHEMA_QUERY)
            return ensure_dict(response.get("apiKeyCreationFormSchema", {}))
        except Exception as e:
            logger.error(
                f"Error in get_api_key_creation_form_schema: {e}",
                exc_info=True,
            )
            raise ToolError(f"Failed to get API key creation schema: {str(e)}") from e

    @mcp.tool()
    async def create_api_key(input_config: dict[str, Any], confirm: bool = False) -> dict[str, Any]:
        """Creates a new API key. Requires confirm=True.

        WARNING: The API key value is returned only once and cannot be retrieved later.
        Store it securely immediately after creation.

        Args:
            input_config: Dict with API key configuration (name, roles, etc.)
            confirm: Safety gate - must be True to proceed
        """
        if not confirm:
            raise ToolError(
                "confirm must be True to create an API key. "
                "API keys grant access to the server — handle with care."
            )

        if not input_config or not isinstance(input_config, dict):
            raise ToolError("input_config must be a non-empty dictionary")

        try:
            logger.info("Executing create_api_key")
            variables: dict[str, Any] = {"input": input_config}
            response = await make_graphql_request(CREATE_API_KEY_MUTATION, variables)
            result = response.get("createApiKey")
            if not result:
                raise ToolError("Failed to create API key")
            # Log only redacted key info
            key_value = result.get("key", "")
            if key_value and len(key_value) > 8:
                logger.info(
                    f"API key created: {result.get('name')} (key: {key_value[:8]}...redacted)"
                )
            elif key_value:
                logger.info(f"API key created: {result.get('name')} (key: [redacted])")
            return {
                "success": True,
                "apiKey": result,
                "message": "API key created. Store the key value securely — it cannot be retrieved later.",
            }
        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in create_api_key: {e}", exc_info=True)
            raise ToolError(f"Failed to create API key: {str(e)}") from e

    @mcp.tool()
    async def add_role_to_api_key(
        input_config: dict[str, Any], confirm: bool = False
    ) -> dict[str, Any]:
        """Adds a role to an existing API key. Requires confirm=True.

        Args:
            input_config: Dict with keyId and role to add
            confirm: Safety gate - must be True to proceed
        """
        if not confirm:
            raise ToolError(
                "confirm must be True to add a role to an API key. "
                "This expands the key's permissions."
            )

        if not input_config or not isinstance(input_config, dict):
            raise ToolError("input_config must be a non-empty dictionary")

        try:
            logger.info("Executing add_role_to_api_key")
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
        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in add_role_to_api_key: {e}", exc_info=True)
            raise ToolError(f"Failed to add role to API key: {str(e)}") from e

    @mcp.tool()
    async def remove_role_from_api_key(
        input_config: dict[str, Any], confirm: bool = False
    ) -> dict[str, Any]:
        """Removes a role from an existing API key. Requires confirm=True.

        Args:
            input_config: Dict with keyId and role to remove
            confirm: Safety gate - must be True to proceed
        """
        if not confirm:
            raise ToolError(
                "confirm must be True to remove a role from an API key. "
                "This reduces the key's permissions."
            )

        if not input_config or not isinstance(input_config, dict):
            raise ToolError("input_config must be a non-empty dictionary")

        try:
            logger.info("Executing remove_role_from_api_key")
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
        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in remove_role_from_api_key: {e}", exc_info=True)
            raise ToolError(f"Failed to remove role from API key: {str(e)}") from e

    @mcp.tool()
    async def delete_api_key(key_id: str, confirm: bool = False) -> dict[str, Any]:
        """Deletes an API key permanently. Requires confirm=True.

        Args:
            key_id: ID of the API key to delete
            confirm: Safety gate - must be True to proceed
        """
        if not confirm:
            raise ToolError(
                "confirm must be True to delete an API key. "
                "This permanently revokes the key and cannot be undone."
            )

        if not key_id or not isinstance(key_id, str):
            raise ToolError("key_id must be a non-empty string")

        try:
            logger.info(f"Executing delete_api_key: {key_id}")
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
        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in delete_api_key: {e}", exc_info=True)
            raise ToolError(f"Failed to delete API key: {str(e)}") from e

    @mcp.tool()
    async def update_api_key(input_config: dict[str, Any], confirm: bool = False) -> dict[str, Any]:
        """Updates an existing API key's configuration. Requires confirm=True.

        Args:
            input_config: Dict with API key update fields (id, name, description, etc.)
            confirm: Safety gate - must be True to proceed
        """
        if not confirm:
            raise ToolError(
                "confirm must be True to update an API key. "
                "This modifies the key's configuration."
            )

        if not input_config or not isinstance(input_config, dict):
            raise ToolError("input_config must be a non-empty dictionary")

        try:
            logger.info("Executing update_api_key")
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
        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in update_api_key: {e}", exc_info=True)
            raise ToolError(f"Failed to update API key: {str(e)}") from e

    logger.info("Auth tools registered successfully")
