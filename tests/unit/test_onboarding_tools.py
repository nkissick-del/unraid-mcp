"""Tests for onboarding tools."""

import pytest

from tests.helpers import get_registered_tool_names, get_tool_fn
from unraid_mcp.core.exceptions import ToolError
from unraid_mcp.tools.onboarding import register_onboarding_tools
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
        assert "isFreshInstall" in IS_FRESH_INSTALL_QUERY


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
        assert "status" in mutation_str

    @pytest.mark.parametrize(
        "mutation,keywords",
        [
            (SET_ONBOARDING_OVERRIDE_MUTATION, ["mutation", "$input", "setOnboardingOverride"]),
            (CLEAR_ONBOARDING_OVERRIDE_MUTATION, ["mutation", "clearOnboardingOverride"]),
            (CREATE_INTERNAL_BOOT_POOL_MUTATION, ["mutation", "createInternalBootPool"]),
            (REFRESH_INTERNAL_BOOT_CONTEXT_MUTATION, ["mutation", "refreshInternalBootContext"]),
        ],
    )
    def test_other_mutation_structure(self, mutation, keywords):
        for kw in keywords:
            assert kw in mutation


class TestCreateBootPoolConfirmGate:
    @pytest.mark.asyncio
    async def test_confirm_false_raises(self):
        tool_fn = await get_tool_fn(register_onboarding_tools, "create_internal_boot_pool")
        with pytest.raises(ToolError, match="confirm must be True"):
            await tool_fn(confirm=False)

    @pytest.mark.asyncio
    async def test_confirm_default_raises(self):
        tool_fn = await get_tool_fn(register_onboarding_tools, "create_internal_boot_pool")
        with pytest.raises(ToolError, match="confirm must be True"):
            await tool_fn()


class TestSetOverrideValidation:
    @pytest.mark.asyncio
    async def test_empty_config_raises(self):
        tool_fn = await get_tool_fn(register_onboarding_tools, "set_onboarding_override")
        with pytest.raises(ToolError, match="non-empty dictionary"):
            await tool_fn({})


class TestOnboardingToolRegistration:
    async def test_all_tools_registered(self):
        tool_names = await get_registered_tool_names(register_onboarding_tools)
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
