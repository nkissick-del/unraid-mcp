"""Customization tools for display settings, themes, and locale.

This module is gated under the 'customization' module and disabled by default.
"""

from typing import Any

from fastmcp import FastMCP

from ..core.client import make_graphql_request
from ..core.decorators import tool_error_handler
from ..core.exceptions import ToolError
from ..core.utils import ensure_dict, validate_input_dict
from .queries.customization import (
    CURRENT_USER_QUERY,
    CUSTOMIZATION_QUERY,
    DISPLAY_SETTINGS_QUERY,
    OWNER_INFO_QUERY,
    PUBLIC_THEME_QUERY,
    SET_LOCALE_MUTATION,
    SET_THEME_MUTATION,
)


def register_customization_tools(mcp: FastMCP) -> None:
    """Register customization tools with the FastMCP instance."""

    @mcp.tool()
    @tool_error_handler("retrieve display settings")
    async def get_display_settings() -> dict[str, Any]:
        """Retrieves current display settings including locale, theme, date/time format, and start page."""
        response = await make_graphql_request(DISPLAY_SETTINGS_QUERY)
        return ensure_dict(response.get("display", {}))

    @mcp.tool()
    @tool_error_handler("retrieve current user")
    async def get_current_user() -> dict[str, Any]:
        """Retrieves information about the currently authenticated user (name, role, permissions)."""
        response = await make_graphql_request(CURRENT_USER_QUERY)
        return ensure_dict(response.get("me", {}))

    @mcp.tool()
    @tool_error_handler("retrieve owner info")
    async def get_owner_info() -> dict[str, Any]:
        """Retrieves owner information including username, URL, and avatar."""
        response = await make_graphql_request(OWNER_INFO_QUERY)
        return ensure_dict(response.get("owner", {}))

    @mcp.tool()
    @tool_error_handler("retrieve customization")
    async def get_customization() -> dict[str, Any]:
        """Retrieves the full customization configuration including theme, locale, date/time format, banner, and usage."""
        response = await make_graphql_request(CUSTOMIZATION_QUERY)
        return ensure_dict(response.get("customization", {}))

    @mcp.tool()
    @tool_error_handler("retrieve public theme")
    async def get_public_theme() -> dict[str, Any]:
        """Retrieves the public theme settings (available without authentication)."""
        response = await make_graphql_request(PUBLIC_THEME_QUERY)
        return ensure_dict(response.get("publicTheme", {}))

    @mcp.tool()
    @tool_error_handler("set theme")
    async def set_theme(input_config: dict[str, Any]) -> dict[str, Any]:
        """Sets the UI theme configuration. This is a cosmetic change only.

        Args:
            input_config: Dict of theme fields to set (e.g. theme, banner)
        """
        validate_input_dict(input_config)

        variables: dict[str, Any] = {"theme": input_config.get("theme", input_config.get("name"))}
        response = await make_graphql_request(SET_THEME_MUTATION, variables)
        result = (response.get("customization") or {}).get("setTheme")
        if result is None:
            raise ToolError("Failed to set theme")
        return {
            "success": True,
            "theme": result,
            "message": "Theme updated successfully",
        }

    @mcp.tool()
    @tool_error_handler("set locale")
    async def set_locale(locale: str) -> dict[str, Any]:
        """Sets the UI locale/language. This is a cosmetic change only.

        Args:
            locale: The locale string to set (e.g. 'en-US', 'de-DE')
        """
        if not isinstance(locale, str) or not locale.strip():
            raise ToolError("locale must be a non-empty string")
        locale = locale.strip()

        variables: dict[str, Any] = {"locale": locale}
        response = await make_graphql_request(SET_LOCALE_MUTATION, variables)
        result = (response.get("customization") or {}).get("setLocale")
        if result is None:
            raise ToolError("Failed to set locale")
        return {
            "success": True,
            "locale": result,
            "message": f"Locale set to {locale}",
        }
