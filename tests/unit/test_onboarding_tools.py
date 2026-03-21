"""Tests for onboarding tools."""

import pytest

from unraid_mcp.core.exceptions import ToolError
from unraid_mcp.tools.queries.onboarding import (
    BYPASS_ONBOARDING_MUTATION,
    CLEAR_ONBOARDING_OVERRIDE_MUTATION,
    CLOSE_ONBOARDING_MUTATION,
    COMPLETE_ONBOARDING_MUTATION,
    CREATE_INTERNAL_BOOT_POOL_MUTATION,
    IS_FRESH_INSTALL_QUERY,
    OPEN_ONBOARDING_MUTATION,
    REFRESH_INTERNAL_BOOT_CONTEXT_MUTATION,
    RESET_ONBOARDING_MUTATION,
    RESUME_ONBOARDING_MUTATION,
    SET_ONBOARDING_OVERRIDE_MUTATION,
)


class TestOnboardingQueries:
    def test_is_fresh_install_query(self):
        assert "query" in IS_FRESH_INSTALL_QUERY
        assert "freshInstall" in IS_FRESH_INSTALL_QUERY


class TestOnboardingMutations:
    @pytest.mark.parametrize(
        "mutation_name,mutation_str,keyword",
        [
            ("complete", COMPLETE_ONBOARDING_MUTATION, "complete"),
            ("reset", RESET_ONBOARDING_MUTATION, "reset"),
            ("open", OPEN_ONBOARDING_MUTATION, "open"),
            ("close", CLOSE_ONBOARDING_MUTATION, "close"),
            ("bypass", BYPASS_ONBOARDING_MUTATION, "bypass"),
            ("resume", RESUME_ONBOARDING_MUTATION, "resume"),
        ],
    )
    def test_idempotent_mutation_is_valid(self, mutation_name, mutation_str, keyword):
        assert "mutation" in mutation_str
        assert keyword in mutation_str.lower()
        assert "success" in mutation_str

    def test_set_override_mutation_is_valid(self):
        assert "mutation" in SET_ONBOARDING_OVERRIDE_MUTATION
        assert "$input" in SET_ONBOARDING_OVERRIDE_MUTATION
        assert "setOverride" in SET_ONBOARDING_OVERRIDE_MUTATION

    def test_clear_override_mutation_is_valid(self):
        assert "mutation" in CLEAR_ONBOARDING_OVERRIDE_MUTATION
        assert "clearOverride" in CLEAR_ONBOARDING_OVERRIDE_MUTATION

    def test_create_boot_pool_mutation_is_valid(self):
        assert "mutation" in CREATE_INTERNAL_BOOT_POOL_MUTATION
        assert "createInternalBootPool" in CREATE_INTERNAL_BOOT_POOL_MUTATION

    def test_refresh_boot_context_mutation_is_valid(self):
        assert "mutation" in REFRESH_INTERNAL_BOOT_CONTEXT_MUTATION
        assert "refreshInternalBootContext" in REFRESH_INTERNAL_BOOT_CONTEXT_MUTATION


class TestCreateBootPoolConfirmGate:
    @pytest.mark.asyncio
    async def test_confirm_false_raises(self):
        from fastmcp import FastMCP

        from unraid_mcp.tools.onboarding import register_onboarding_tools

        test_mcp = FastMCP("test")
        register_onboarding_tools(test_mcp)

        tool_fn = None
        for tool in test_mcp._tool_manager._tools.values():
            if tool.name == "create_internal_boot_pool":
                tool_fn = tool.fn
                break

        assert tool_fn is not None, "create_internal_boot_pool tool not registered"
        with pytest.raises(ToolError, match="confirm must be True"):
            await tool_fn(confirm=False)

    @pytest.mark.asyncio
    async def test_confirm_default_raises(self):
        from fastmcp import FastMCP

        from unraid_mcp.tools.onboarding import register_onboarding_tools

        test_mcp = FastMCP("test")
        register_onboarding_tools(test_mcp)

        tool_fn = None
        for tool in test_mcp._tool_manager._tools.values():
            if tool.name == "create_internal_boot_pool":
                tool_fn = tool.fn
                break

        assert tool_fn is not None
        with pytest.raises(ToolError, match="confirm must be True"):
            await tool_fn()


class TestSetOverrideValidation:
    @pytest.mark.asyncio
    async def test_empty_config_raises(self):
        from fastmcp import FastMCP

        from unraid_mcp.tools.onboarding import register_onboarding_tools

        test_mcp = FastMCP("test")
        register_onboarding_tools(test_mcp)

        tool_fn = None
        for tool in test_mcp._tool_manager._tools.values():
            if tool.name == "set_onboarding_override":
                tool_fn = tool.fn
                break

        assert tool_fn is not None
        with pytest.raises(ToolError, match="non-empty dictionary"):
            await tool_fn({})


class TestOnboardingToolRegistration:
    def test_all_tools_registered(self):
        from fastmcp import FastMCP

        from unraid_mcp.tools.onboarding import register_onboarding_tools

        test_mcp = FastMCP("test")
        register_onboarding_tools(test_mcp)

        tool_names = set(test_mcp._tool_manager._tools.keys())
        expected = {
            "is_fresh_install",
            "complete_onboarding",
            "reset_onboarding",
            "open_onboarding",
            "close_onboarding",
            "bypass_onboarding",
            "resume_onboarding",
            "set_onboarding_override",
            "clear_onboarding_override",
            "create_internal_boot_pool",
            "refresh_internal_boot_context",
        }
        assert expected.issubset(tool_names)
