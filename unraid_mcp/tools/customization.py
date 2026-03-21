"""Customization tools for display settings, themes, and locale.

This module is gated under the 'customization' module and disabled by default.
"""

from typing import Any

from fastmcp import FastMCP

from ..config.logging import logger
from ..core.client import make_graphql_request
from ..core.exceptions import ToolError
from ..core.utils import ensure_dict
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
    async def get_display_settings() -> dict[str, Any]:
        """Retrieves current display settings including locale, theme, date/time format, and start page."""
        try:
            logger.info("Executing get_display_settings")
            response = await make_graphql_request(DISPLAY_SETTINGS_QUERY)
            return ensure_dict(response.get("display", {}))
        except Exception as e:
            logger.error(f"Error in get_display_settings: {e}", exc_info=True)
            raise ToolError(f"Failed to retrieve display settings: {str(e)}") from e

    @mcp.tool()
    async def get_current_user() -> dict[str, Any]:
        """Retrieves information about the currently authenticated user (name, role, permissions)."""
        try:
            logger.info("Executing get_current_user")
            response = await make_graphql_request(CURRENT_USER_QUERY)
            return ensure_dict(response.get("me", {}))
        except Exception as e:
            logger.error(f"Error in get_current_user: {e}", exc_info=True)
            raise ToolError(f"Failed to retrieve current user: {str(e)}") from e

    @mcp.tool()
    async def get_owner_info() -> dict[str, Any]:
        """Retrieves owner information including username, URL, and avatar."""
        try:
            logger.info("Executing get_owner_info")
            response = await make_graphql_request(OWNER_INFO_QUERY)
            return ensure_dict(response.get("owner", {}))
        except Exception as e:
            logger.error(f"Error in get_owner_info: {e}", exc_info=True)
            raise ToolError(f"Failed to retrieve owner info: {str(e)}") from e

    @mcp.tool()
    async def get_customization() -> dict[str, Any]:
        """Retrieves the full customization configuration including theme, locale, date/time format, banner, and usage."""
        try:
            logger.info("Executing get_customization")
            response = await make_graphql_request(CUSTOMIZATION_QUERY)
            return ensure_dict(response.get("customization", {}))
        except Exception as e:
            logger.error(f"Error in get_customization: {e}", exc_info=True)
            raise ToolError(f"Failed to retrieve customization: {str(e)}") from e

    @mcp.tool()
    async def get_public_theme() -> dict[str, Any]:
        """Retrieves the public theme settings (available without authentication)."""
        try:
            logger.info("Executing get_public_theme")
            response = await make_graphql_request(PUBLIC_THEME_QUERY)
            return ensure_dict(response.get("publicTheme", {}))
        except Exception as e:
            logger.error(f"Error in get_public_theme: {e}", exc_info=True)
            raise ToolError(f"Failed to retrieve public theme: {str(e)}") from e

    @mcp.tool()
    async def set_theme(input_config: dict[str, Any]) -> dict[str, Any]:
        """Sets the UI theme configuration. This is a cosmetic change only.

        Args:
            input_config: Dict of theme fields to set (e.g. theme, banner)
        """
        if not input_config or not isinstance(input_config, dict):
            raise ToolError("input_config must be a non-empty dictionary")

        try:
            logger.info("Executing set_theme")
            variables: dict[str, Any] = {"input": input_config}
            response = await make_graphql_request(SET_THEME_MUTATION, variables)
            result = response.get("setTheme")
            if result is None:
                raise ToolError("Failed to set theme")
            return {
                "success": True,
                "theme": result,
                "message": "Theme updated successfully",
            }
        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in set_theme: {e}", exc_info=True)
            raise ToolError(f"Failed to set theme: {str(e)}") from e

    @mcp.tool()
    async def set_locale(locale: str) -> dict[str, Any]:
        """Sets the UI locale/language. This is a cosmetic change only.

        Args:
            locale: The locale string to set (e.g. 'en-US', 'de-DE')
        """
        if not isinstance(locale, str) or not locale.strip():
            raise ToolError("locale must be a non-empty string")
        locale = locale.strip()

        try:
            logger.info(f"Executing set_locale: {locale}")
            variables: dict[str, Any] = {"locale": locale}
            response = await make_graphql_request(SET_LOCALE_MUTATION, variables)
            result = response.get("setLocale")
            if result is None:
                raise ToolError("Failed to set locale")
            return {
                "success": True,
                "locale": result,
                "message": f"Locale set to {locale}",
            }
        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in set_locale: {e}", exc_info=True)
            raise ToolError(f"Failed to set locale: {str(e)}") from e

    logger.info("Customization tools registered successfully")
