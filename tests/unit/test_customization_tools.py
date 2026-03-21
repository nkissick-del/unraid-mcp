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
    def test_display_settings_query_is_valid(self):
        assert "query" in DISPLAY_SETTINGS_QUERY
        assert "display" in DISPLAY_SETTINGS_QUERY

    def test_display_settings_has_expected_fields(self):
        assert "locale" in DISPLAY_SETTINGS_QUERY
        assert "theme" in DISPLAY_SETTINGS_QUERY
        assert "dateFormat" in DISPLAY_SETTINGS_QUERY

    def test_current_user_query_is_valid(self):
        assert "query" in CURRENT_USER_QUERY
        assert "me" in CURRENT_USER_QUERY

    def test_current_user_has_expected_fields(self):
        assert "name" in CURRENT_USER_QUERY
        assert "role" in CURRENT_USER_QUERY
        assert "permissions" in CURRENT_USER_QUERY

    def test_owner_info_query_is_valid(self):
        assert "query" in OWNER_INFO_QUERY
        assert "owner" in OWNER_INFO_QUERY

    def test_owner_has_expected_fields(self):
        assert "username" in OWNER_INFO_QUERY
        assert "url" in OWNER_INFO_QUERY
        assert "avatar" in OWNER_INFO_QUERY

    def test_customization_query_is_valid(self):
        assert "query" in CUSTOMIZATION_QUERY
        assert "customization" in CUSTOMIZATION_QUERY

    def test_customization_has_expected_fields(self):
        assert "theme" in CUSTOMIZATION_QUERY
        assert "locale" in CUSTOMIZATION_QUERY
        assert "banner" in CUSTOMIZATION_QUERY

    def test_public_theme_query_is_valid(self):
        assert "query" in PUBLIC_THEME_QUERY
        assert "publicTheme" in PUBLIC_THEME_QUERY

    def test_public_theme_has_expected_fields(self):
        assert "theme" in PUBLIC_THEME_QUERY
        assert "banner" in PUBLIC_THEME_QUERY


class TestCustomizationMutations:
    def test_set_theme_mutation_is_valid(self):
        assert "mutation" in SET_THEME_MUTATION
        assert "setTheme" in SET_THEME_MUTATION
        assert "$input" in SET_THEME_MUTATION

    def test_set_locale_mutation_is_valid(self):
        assert "mutation" in SET_LOCALE_MUTATION
        assert "setLocale" in SET_LOCALE_MUTATION
        assert "$locale" in SET_LOCALE_MUTATION


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
