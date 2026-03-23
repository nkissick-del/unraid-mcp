"""Tests for customization tools."""

import pytest

from tests.helpers import get_registered_tool_names, get_tool_fn
from unraid_mcp.core.exceptions import ToolError
from unraid_mcp.tools.customization import register_customization_tools
from unraid_mcp.tools.queries.customization import (
    CURRENT_USER_QUERY,
    CUSTOMIZATION_QUERY,
    DISPLAY_SETTINGS_QUERY,
    OWNER_INFO_QUERY,
    PUBLIC_THEME_QUERY,
    SET_LOCALE_MUTATION,
    SET_THEME_MUTATION,
)


class TestCustomizationQueries:
    @pytest.mark.parametrize(
        "query,keywords",
        [
            (DISPLAY_SETTINGS_QUERY, ["query", "display", "locale", "theme", "unit", "scale"]),
            (CURRENT_USER_QUERY, ["query", "me", "name", "roles", "permissions"]),
            (OWNER_INFO_QUERY, ["query", "owner", "username", "url", "avatar"]),
            (CUSTOMIZATION_QUERY, ["query", "customization", "activationCode", "onboarding"]),
            (
                PUBLIC_THEME_QUERY,
                ["query", "publicTheme", "showBannerImage", "headerBackgroundColor"],
            ),
        ],
    )
    def test_query_structure(self, query, keywords):
        for kw in keywords:
            assert kw in query


class TestCustomizationMutations:
    @pytest.mark.parametrize(
        "mutation,keywords",
        [
            (SET_THEME_MUTATION, ["mutation", "setTheme", "$theme", "customization"]),
            (SET_LOCALE_MUTATION, ["mutation", "setLocale", "$locale", "customization"]),
        ],
    )
    def test_mutation_structure(self, mutation, keywords):
        for kw in keywords:
            assert kw in mutation


class TestSetThemeValidation:
    @pytest.mark.asyncio
    async def test_empty_config_raises(self):
        tool_fn = get_tool_fn(register_customization_tools, "set_theme")
        with pytest.raises(ToolError, match="non-empty dictionary"):
            await tool_fn({})

    @pytest.mark.asyncio
    async def test_non_dict_config_raises(self):
        tool_fn = get_tool_fn(register_customization_tools, "set_theme")
        with pytest.raises(ToolError, match="non-empty dictionary"):
            await tool_fn("not-a-dict")


class TestSetLocaleValidation:
    @pytest.mark.asyncio
    async def test_empty_locale_raises(self):
        tool_fn = get_tool_fn(register_customization_tools, "set_locale")
        with pytest.raises(ToolError, match="non-empty string"):
            await tool_fn("")


class TestCustomizationToolRegistration:
    def test_all_tools_registered(self):
        tool_names = get_registered_tool_names(register_customization_tools)
        expected = {
            "get_display_settings",
            "get_current_user",
            "get_owner_info",
            "get_customization",
            "get_public_theme",
            "set_theme",
            "set_locale",
        }
        assert expected.issubset(tool_names)
