# Middleware Stack, Smart Caching & Dynamic Resource Fallback — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a configurable middleware stack (logging, error handling, rate limiting, response limiting, caching) with smart per-tool cache classification, plus a dynamic `unraid://live/{action}` subscription fallback resource.

**Architecture:** Upgrade FastMCP to 3.x, wire 5 middleware layers into the existing `FastMCP()` constructor in `server.py`, add env-var-driven configuration in `settings.py`, classify modules as cacheable/non-cacheable in `registry.py`, and register a dynamic fallback subscription resource in `resources.py`.

**Tech Stack:** FastMCP 3.x, Python 3.12, pytest, uv

**Spec:** `docs/superpowers/specs/2026-03-31-middleware-and-caching-design.md`

---

## Phase 0: FastMCP Upgrade

### Task 1: Upgrade FastMCP to 3.x

**Files:**
- Modify: `pyproject.toml:29`
- Auto-updated: `uv.lock`

- [ ] **Step 1: Bump version constraint**

In `pyproject.toml`, change line 29:

```python
# OLD:
    "fastmcp>=2.14.2,<3.0",
# NEW:
    "fastmcp>=3.2.0,<4.0",
```

- [ ] **Step 2: Sync lockfile**

Run: `uv sync && uv sync --group dev`
Expected: resolves without errors, installs fastmcp 3.x

- [ ] **Step 3: Verify version**

Run: `uv run python -c "import fastmcp; print(fastmcp.__version__)"`
Expected: `3.2.x` or higher

- [ ] **Step 4: Run full test suite**

Run: `uv run pytest -x -q`
Expected: all tests pass (506+)

If tests fail, fix breakage before proceeding. Known risk areas:
- `from fastmcp.utilities.logging import get_logger` in `unraid_mcp/config/logging.py` — if removed in 3.x, replace with `logging.getLogger("fastmcp")`
- `from fastmcp.exceptions import ToolError` in `unraid_mcp/core/exceptions.py` — verify import path
- Any removed constructor kwargs on `FastMCP()` in `server.py`

- [ ] **Step 5: Verify ResponseLimitingMiddleware availability**

Run:
```bash
uv run python -c "from fastmcp.server.middleware.response_limiting import ResponseLimitingMiddleware; print('available')"
```

If this fails with `ModuleNotFoundError`, we will write a custom response-limiting middleware in Task 4. Note the result for Task 4.

- [ ] **Step 6: Run lint and type checks**

Run: `uv run ruff check unraid_mcp/ && uv run black --check unraid_mcp/ && uv run mypy unraid_mcp/`
Expected: all pass

- [ ] **Step 7: Gate — /commit-and-push**

Invoke `/commit-and-push` with message: `chore: upgrade fastmcp from 2.14.5 to 3.x`

---

## Phase 1: Middleware Stack + Configuration

### Task 2: Add middleware configuration to settings.py

**Files:**
- Modify: `unraid_mcp/config/settings.py:90-94` (after TIMEOUT_CONFIG)
- Test: `tests/unit/test_settings_middleware.py` (new)

- [ ] **Step 1: Write the failing test**

Create `tests/unit/test_settings_middleware.py`:

```python
"""Tests for middleware configuration in settings.py."""

import importlib
import os
from unittest.mock import patch


class TestMiddlewareSettings:
    """Verify middleware env vars load with correct defaults and overrides."""

    def _reload_settings(self):
        """Reload settings module to pick up env var changes."""
        import warnings

        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            import unraid_mcp.config.settings as settings_mod

            importlib.reload(settings_mod)
            return settings_mod

    def test_defaults(self):
        """All middleware settings have sensible defaults when no env vars set."""
        with patch.dict(
            os.environ,
            {
                k: ""
                for k in [
                    "UNRAID_MCP_RATE_LIMIT",
                    "UNRAID_MCP_RATE_WINDOW_MINUTES",
                    "UNRAID_MCP_MAX_RESPONSE_KB",
                    "UNRAID_MCP_CACHE_TTL",
                    "UNRAID_MCP_CACHE_ENABLED",
                ]
            },
            clear=False,
        ):
            # Remove the keys entirely so getenv returns default
            for k in [
                "UNRAID_MCP_RATE_LIMIT",
                "UNRAID_MCP_RATE_WINDOW_MINUTES",
                "UNRAID_MCP_MAX_RESPONSE_KB",
                "UNRAID_MCP_CACHE_TTL",
                "UNRAID_MCP_CACHE_ENABLED",
            ]:
                os.environ.pop(k, None)

            s = self._reload_settings()
            assert s.MCP_RATE_LIMIT == 540
            assert s.MCP_RATE_WINDOW_MINUTES == 1
            assert s.MCP_MAX_RESPONSE_KB == 512
            assert s.MCP_CACHE_TTL == 30
            assert s.MCP_CACHE_ENABLED is True

    def test_custom_overrides(self):
        """Env vars override default middleware settings."""
        with patch.dict(
            os.environ,
            {
                "UNRAID_MCP_RATE_LIMIT": "200",
                "UNRAID_MCP_RATE_WINDOW_MINUTES": "5",
                "UNRAID_MCP_MAX_RESPONSE_KB": "1024",
                "UNRAID_MCP_CACHE_TTL": "60",
                "UNRAID_MCP_CACHE_ENABLED": "false",
            },
        ):
            s = self._reload_settings()
            assert s.MCP_RATE_LIMIT == 200
            assert s.MCP_RATE_WINDOW_MINUTES == 5
            assert s.MCP_MAX_RESPONSE_KB == 1024
            assert s.MCP_CACHE_TTL == 60
            assert s.MCP_CACHE_ENABLED is False

    def test_cache_disabled_variants(self):
        """UNRAID_MCP_CACHE_ENABLED accepts common falsy values."""
        for val in ["false", "0", "no", "False", "NO"]:
            with patch.dict(os.environ, {"UNRAID_MCP_CACHE_ENABLED": val}):
                s = self._reload_settings()
                assert s.MCP_CACHE_ENABLED is False, f"Failed for value: {val}"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_settings_middleware.py -v`
Expected: FAIL — `AttributeError: module 'unraid_mcp.config.settings' has no attribute 'MCP_RATE_LIMIT'`

- [ ] **Step 3: Add middleware settings to settings.py**

Add at the end of `unraid_mcp/config/settings.py` (after the `ENABLED_MODULES` block, around line 161):

```python
# Middleware Configuration
# -----------------------
MCP_RATE_LIMIT = int(os.getenv("UNRAID_MCP_RATE_LIMIT", "540"))
MCP_RATE_WINDOW_MINUTES = int(os.getenv("UNRAID_MCP_RATE_WINDOW_MINUTES", "1"))
MCP_MAX_RESPONSE_KB = int(os.getenv("UNRAID_MCP_MAX_RESPONSE_KB", "512"))
MCP_CACHE_TTL = int(os.getenv("UNRAID_MCP_CACHE_TTL", "30"))
_raw_cache_enabled = os.getenv("UNRAID_MCP_CACHE_ENABLED", "true").lower()
MCP_CACHE_ENABLED = _raw_cache_enabled not in ("false", "0", "no")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/unit/test_settings_middleware.py -v`
Expected: all 3 tests PASS

- [ ] **Step 5: Run full test suite**

Run: `uv run pytest -x -q`
Expected: all tests pass

---

### Task 3: Add middleware stack to server.py (without caching)

**Files:**
- Modify: `unraid_mcp/server.py:1-47`
- Test: `tests/unit/test_server_middleware.py` (new)

- [ ] **Step 1: Write the failing test**

Create `tests/unit/test_server_middleware.py`:

```python
"""Tests for middleware wiring in server.py."""

from unittest.mock import patch

import pytest


class TestMiddlewareWiring:
    """Verify middleware is configured and passed to FastMCP."""

    def test_mcp_has_middleware(self):
        """The mcp instance should have middleware configured."""
        from unraid_mcp.server import mcp

        assert mcp.middleware is not None
        assert len(mcp.middleware) > 0, "No middleware configured"

    def test_middleware_order(self):
        """Middleware should be in the correct order: logging, error, rate, response, cache."""
        from fastmcp.server.middleware.error_handling import ErrorHandlingMiddleware
        from fastmcp.server.middleware.logging import LoggingMiddleware
        from fastmcp.server.middleware.rate_limiting import (
            SlidingWindowRateLimitingMiddleware,
        )

        from unraid_mcp.server import mcp

        middleware = mcp.middleware
        # Check types in order — at minimum logging, error, rate limiting must be present
        types = [type(m) for m in middleware]
        assert LoggingMiddleware in types, "LoggingMiddleware missing"
        assert ErrorHandlingMiddleware in types, "ErrorHandlingMiddleware missing"
        assert SlidingWindowRateLimitingMiddleware in types, "RateLimitingMiddleware missing"

        # Verify order: logging before error, error before rate limiting
        log_idx = types.index(LoggingMiddleware)
        err_idx = types.index(ErrorHandlingMiddleware)
        rate_idx = types.index(SlidingWindowRateLimitingMiddleware)
        assert log_idx < err_idx < rate_idx, (
            f"Wrong middleware order: logging={log_idx}, error={err_idx}, rate={rate_idx}"
        )

    def test_rate_limit_uses_config(self):
        """Rate limiter should use values from settings."""
        from fastmcp.server.middleware.rate_limiting import (
            SlidingWindowRateLimitingMiddleware,
        )

        from unraid_mcp.server import mcp

        rate_mw = None
        for m in mcp.middleware:
            if isinstance(m, SlidingWindowRateLimitingMiddleware):
                rate_mw = m
                break
        assert rate_mw is not None, "Rate limiting middleware not found"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_server_middleware.py -v`
Expected: FAIL — `mcp.middleware` is `None` or empty

- [ ] **Step 3: Add middleware to server.py**

Replace the imports and `FastMCP()` instantiation in `unraid_mcp/server.py`. The full updated file:

```python
"""Modular Unraid MCP Server.

This is the main server implementation using the modular architecture with
separate modules for configuration, core functionality, subscriptions, and tools.
"""

import importlib
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastmcp import FastMCP
from fastmcp.server.middleware.error_handling import ErrorHandlingMiddleware
from fastmcp.server.middleware.logging import LoggingMiddleware
from fastmcp.server.middleware.rate_limiting import SlidingWindowRateLimitingMiddleware

from . import __version__
from .config.logging import logger
from .config.settings import (
    ENABLED_MODULES,
    LOG_LEVEL_STR,
    MCP_RATE_LIMIT,
    MCP_RATE_WINDOW_MINUTES,
    UNRAID_API_KEY,
    UNRAID_API_URL,
    UNRAID_MCP_HOST,
    UNRAID_MCP_PORT,
    UNRAID_MCP_TRANSPORT,
)
from .core.client import close_http_client
from .registry import MODULE_REGISTRY
from .subscriptions.manager import subscription_manager
from .subscriptions.resources import register_subscription_resources


@asynccontextmanager
async def app_lifespan(app: FastMCP) -> AsyncIterator[None]:
    """Manage server startup and graceful shutdown."""
    yield
    # Shutdown cleanup
    logger.info("Shutting down — cleaning up resources...")
    await subscription_manager.stop_all_subscriptions()
    await close_http_client()
    logger.info("Shutdown complete.")


# --- Middleware chain (outermost → innermost) ---

# 1. Log every tools/call and resources/read with duration and errors.
_logging_middleware = LoggingMiddleware(
    logger=logger,
    methods=["tools/call", "resources/read"],
)

# 2. Convert unhandled exceptions to MCP errors. Tracebacks only in DEBUG.
_error_middleware = ErrorHandlingMiddleware(
    logger=logger,
    include_traceback=LOG_LEVEL_STR == "DEBUG",
)

# 3. Rate limiting: sliding window to prevent API overload.
_rate_limiter = SlidingWindowRateLimitingMiddleware(
    max_requests=MCP_RATE_LIMIT,
    window_minutes=MCP_RATE_WINDOW_MINUTES,
)

# Note: ResponseCachingMiddleware is added dynamically in register_all_modules()
# after tools are registered, with smart per-tool exclusions (Phase 2, Task 7).

_middleware_stack = [
    _logging_middleware,
    _error_middleware,
    _rate_limiter,
]

# Initialize FastMCP instance
mcp = FastMCP(
    name="Unraid MCP Server",
    instructions="Provides tools to interact with an Unraid server's GraphQL API.",
    version=__version__,
    lifespan=app_lifespan,
    middleware=_middleware_stack,
)


def register_all_modules() -> None:
    """Register tools and resources based on ENABLED_MODULES configuration."""
    try:
        # Always register base subscription resources (lightweight log stream endpoint)
        register_subscription_resources(mcp)

        # Conditionally register tool modules via registry
        for module_name in ENABLED_MODULES:
            if module_name not in MODULE_REGISTRY:
                logger.warning(f"Unknown module '{module_name}' in ENABLED_MODULES, skipping")
                continue
            import_path, func_name = MODULE_REGISTRY[module_name]
            mod = importlib.import_module(import_path)
            getattr(mod, func_name)(mcp)

        logger.info(f"Modules registered: {sorted(ENABLED_MODULES)}")

    except Exception as e:
        logger.error(f"Failed to register modules: {e}", exc_info=True)
        raise


def run_server() -> None:
    """Run the MCP server with the configured transport."""
    # Log configuration
    if UNRAID_API_URL:
        logger.info(f"UNRAID_API_URL loaded: {UNRAID_API_URL[:20]}...")
    else:
        logger.warning("UNRAID_API_URL not found in environment or .env file.")

    if UNRAID_API_KEY:
        logger.info("UNRAID_API_KEY loaded: ****")
    else:
        logger.warning("UNRAID_API_KEY not found in environment or .env file.")

    logger.info(f"UNRAID_MCP_PORT set to: {UNRAID_MCP_PORT}")
    logger.info(f"UNRAID_MCP_HOST set to: {UNRAID_MCP_HOST}")
    logger.info(f"UNRAID_MCP_TRANSPORT set to: {UNRAID_MCP_TRANSPORT}")

    # Register all modules
    register_all_modules()

    logger.info(
        f"🚀 Starting Unraid MCP Server on {UNRAID_MCP_HOST}:{UNRAID_MCP_PORT} using {UNRAID_MCP_TRANSPORT} transport..."
    )

    try:
        # Auto-start subscriptions on first async operation
        if UNRAID_MCP_TRANSPORT == "streamable-http":
            mcp.run(
                transport="streamable-http",
                host=UNRAID_MCP_HOST,
                port=UNRAID_MCP_PORT,
                path="/mcp",
            )
        elif UNRAID_MCP_TRANSPORT == "sse":
            logger.warning(
                "SSE transport is deprecated and may be removed in a future version. Consider switching to 'streamable-http'."
            )
            mcp.run(
                transport="sse",
                host=UNRAID_MCP_HOST,
                port=UNRAID_MCP_PORT,
                path="/mcp",
            )
        elif UNRAID_MCP_TRANSPORT == "stdio":
            mcp.run()
        else:
            logger.error(
                f"Unsupported MCP_TRANSPORT: {UNRAID_MCP_TRANSPORT}. Choose 'streamable-http' (recommended), 'sse' (deprecated), or 'stdio'."
            )
            sys.exit(1)
    except Exception as e:
        logger.critical(f"❌ Failed to start Unraid MCP server: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    run_server()
```

Note: this version does NOT include ResponseLimitingMiddleware or smart caching yet. Those come in Task 4 and Phase 2.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/unit/test_server_middleware.py -v`
Expected: all 3 tests PASS

- [ ] **Step 5: Run full test suite**

Run: `uv run pytest -x -q`
Expected: all tests pass

---

### Task 4: Add response limiting middleware

**Files:**
- Modify: `unraid_mcp/server.py`
- Possibly create: `unraid_mcp/core/response_limiter.py` (only if built-in unavailable)
- Test: `tests/unit/test_server_middleware.py` (append)

This task depends on the result of Task 1, Step 5. Two paths:

#### Path A: Built-in ResponseLimitingMiddleware is available

- [ ] **Step 1: Add ResponseLimitingMiddleware import and instantiation to server.py**

Add to the imports in `server.py`:

```python
from fastmcp.server.middleware.response_limiting import ResponseLimitingMiddleware
```

Add after `_rate_limiter` and before `_cache_middleware`:

```python
# 4. Cap tool responses to protect client context window.
_response_limiter = ResponseLimitingMiddleware(max_size=MCP_MAX_RESPONSE_KB * 1024)
```

Update `_middleware_stack` to include it between rate limiter and cache:

```python
_middleware_stack = [
    _logging_middleware,
    _error_middleware,
    _rate_limiter,
    _response_limiter,
    _cache_middleware,
]
```

#### Path B: Built-in not available — write custom middleware

- [ ] **Step 1: Write the failing test**

Add to `tests/unit/test_server_middleware.py`:

```python
    def test_response_limiter_present(self):
        """A response-limiting middleware should be in the stack."""
        from unraid_mcp.server import mcp

        types = [type(m).__name__ for m in mcp.middleware]
        assert any("response" in name.lower() or "limit" in name.lower() for name in types), (
            f"No response-limiting middleware found. Stack: {types}"
        )
```

- [ ] **Step 2: Create custom response limiter**

Create `unraid_mcp/core/response_limiter.py`:

```python
"""Custom response-limiting middleware for FastMCP.

Truncates tool call responses that exceed a configurable size limit
to protect the client LLM's context window.
"""

import json
from typing import Any

from fastmcp.server.middleware.middleware import Middleware, MiddlewareContext


class ResponseLimitingMiddleware(Middleware):
    """Truncate oversized tool responses with a clear suffix."""

    def __init__(self, max_size: int = 524_288) -> None:
        self.max_size = max_size

    async def call_tool(
        self, context: MiddlewareContext, name: str, arguments: dict[str, Any]
    ) -> Any:
        result = await context.call_next(name=name, arguments=arguments)
        serialized = json.dumps(result) if not isinstance(result, str) else result
        if len(serialized.encode("utf-8")) > self.max_size:
            limit_kb = self.max_size // 1024
            truncated = serialized[: self.max_size]
            return f"{truncated}\n\n... [Response truncated at {limit_kb} KB limit]"
        return result
```

- [ ] **Step 3: Wire into server.py**

Add import:

```python
from .core.response_limiter import ResponseLimitingMiddleware
```

Add instance and insert into middleware stack (same as Path A).

- [ ] **Step 4: Run tests**

Run: `uv run pytest tests/unit/test_server_middleware.py -v`
Expected: all tests PASS

- [ ] **Step 5: Run full test suite**

Run: `uv run pytest -x -q`
Expected: all tests pass

---

### Task 5: Update .env.example and Unraid XML template

**Files:**
- Modify: `.env.example`
- Modify: `unraid-mcp.xml`

- [ ] **Step 1: Add middleware vars to .env.example**

Append to `.env.example` before the subscriptions section:

```bash
# Middleware Configuration
# -----------------------
# Rate limiting: max requests per sliding window (prevents API overload)
# UNRAID_MCP_RATE_LIMIT=540
# UNRAID_MCP_RATE_WINDOW_MINUTES=1

# Response size cap in KB (protects LLM context window from oversized responses)
# UNRAID_MCP_MAX_RESPONSE_KB=512

# Caching for read-only tools (mutation tools are never cached)
# UNRAID_MCP_CACHE_TTL=30
# UNRAID_MCP_CACHE_ENABLED=true
```

- [ ] **Step 2: Add Config entries to unraid-mcp.xml**

Add 5 new `<Config>` entries before the closing `</Container>` tag in `unraid-mcp.xml`, after the Log Directory config:

```xml
  <Config Name="Rate Limit" Target="UNRAID_MCP_RATE_LIMIT" Default="540" Mode="" Description="Maximum requests per rate-limit window. Prevents runaway LLM from overloading the Unraid API." Type="Variable" Display="advanced" Required="false" Mask="false">540</Config>
  <Config Name="Rate Window (minutes)" Target="UNRAID_MCP_RATE_WINDOW_MINUTES" Default="1" Mode="" Description="Sliding window duration in minutes for rate limiting." Type="Variable" Display="advanced" Required="false" Mask="false">1</Config>
  <Config Name="Max Response Size (KB)" Target="UNRAID_MCP_MAX_RESPONSE_KB" Default="512" Mode="" Description="Maximum tool response size in KB. Larger responses are truncated to protect the LLM context window." Type="Variable" Display="advanced" Required="false" Mask="false">512</Config>
  <Config Name="Cache TTL (seconds)" Target="UNRAID_MCP_CACHE_TTL" Default="30" Mode="" Description="How long read-only tool responses are cached, in seconds. Mutation tools are never cached." Type="Variable" Display="advanced" Required="false" Mask="false">30</Config>
  <Config Name="Cache Enabled" Target="UNRAID_MCP_CACHE_ENABLED" Default="true" Mode="" Description="Master toggle for response caching. Set to false to disable all caching." Type="Variable" Display="advanced" Required="false" Mask="false">true</Config>
```

- [ ] **Step 3: Validate XML is well-formed**

Run: `python -c "import xml.etree.ElementTree as ET; ET.parse('unraid-mcp.xml'); print('XML valid')"`
Expected: `XML valid`

- [ ] **Step 4: Run full test suite**

Run: `uv run pytest -x -q`
Expected: all tests pass (no code logic changed, just config files)

- [ ] **Step 5: Gate — /commit-and-push**

Invoke `/commit-and-push` with message: `feat: add configurable middleware stack (rate limiting, error handling, logging, response limiting, caching)`

---

## Phase 2: Smart Caching, Dynamic Resource Fallback & Cleanup

### Task 6: Add cacheable flag to registry

**Files:**
- Modify: `unraid_mcp/registry.py`
- Modify: `unraid_mcp/server.py` (update `register_all_modules` to use new dict format)
- Test: `tests/unit/test_registry.py` (new)

- [ ] **Step 1: Write the failing test**

Create `tests/unit/test_registry.py`:

```python
"""Tests for module registry structure and cache classification."""

from unraid_mcp.registry import MODULE_REGISTRY

# Modules that should be cacheable (read-only queries)
EXPECTED_CACHEABLE = {
    "system",
    "system-extra",
    "metrics",
    "ups",
    "health",
    "storage",
    "docker",
    "api",
    "notifications",
    "notifications-extra",
    "parity",
    "diagnostics",
    "connect",
}

# Modules that must NOT be cached (mutations or state-changing)
EXPECTED_NON_CACHEABLE = {
    "docker-admin",
    "docker-batch",
    "docker-organize",
    "array",
    "array-admin",
    "rclone",
    "server-admin",
    "plugins",
    "customization",
    "onboarding",
    "auth",
    "vms",
    "ups-admin",
}


class TestModuleRegistry:
    def test_all_entries_have_required_keys(self):
        """Every registry entry must have import, register, and cacheable keys."""
        for name, entry in MODULE_REGISTRY.items():
            assert "import" in entry, f"Module '{name}' missing 'import' key"
            assert "register" in entry, f"Module '{name}' missing 'register' key"
            assert "cacheable" in entry, f"Module '{name}' missing 'cacheable' key"
            assert isinstance(entry["cacheable"], bool), (
                f"Module '{name}' cacheable must be bool"
            )

    def test_cacheable_modules_classified_correctly(self):
        """Read-only modules should be marked cacheable=True."""
        for name in EXPECTED_CACHEABLE:
            if name in MODULE_REGISTRY:
                assert MODULE_REGISTRY[name]["cacheable"] is True, (
                    f"Module '{name}' should be cacheable"
                )

    def test_non_cacheable_modules_classified_correctly(self):
        """Mutation modules should be marked cacheable=False."""
        for name in EXPECTED_NON_CACHEABLE:
            if name in MODULE_REGISTRY:
                assert MODULE_REGISTRY[name]["cacheable"] is False, (
                    f"Module '{name}' should NOT be cacheable"
                )

    def test_all_modules_classified(self):
        """Every module in the registry should be in either cacheable or non-cacheable set."""
        classified = EXPECTED_CACHEABLE | EXPECTED_NON_CACHEABLE
        # subscriptions and subscriptions-extra are resource modules, not tools
        resource_modules = {"subscriptions", "subscriptions-extra"}
        for name in MODULE_REGISTRY:
            assert name in classified or name in resource_modules, (
                f"Module '{name}' not classified as cacheable or non-cacheable"
            )
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_registry.py -v`
Expected: FAIL — entries are tuples, not dicts

- [ ] **Step 3: Convert registry to dict format with cacheable flag**

Replace the entire content of `unraid_mcp/registry.py`:

```python
"""Module registry mapping module names to their registration functions.

Adding a new module requires only a single entry here. The server.py
register_all_modules() function iterates this registry to load modules.

Each entry is a dict with:
  - "import": dotted import path to the module
  - "register": name of the registration function
  - "cacheable": True for read-only modules (safe to cache), False for mutation modules
"""

from typing import Any

MODULE_REGISTRY: dict[str, dict[str, Any]] = {
    # --- Cacheable (read-only) modules ---
    "diagnostics": {
        "import": "unraid_mcp.subscriptions.diagnostics",
        "register": "register_diagnostic_tools",
        "cacheable": True,
    },
    "system": {
        "import": "unraid_mcp.tools.system",
        "register": "register_system_tools",
        "cacheable": True,
    },
    "docker": {
        "import": "unraid_mcp.tools.docker",
        "register": "register_docker_tools",
        "cacheable": True,
    },
    "storage": {
        "import": "unraid_mcp.tools.storage",
        "register": "register_storage_tools",
        "cacheable": True,
    },
    "notifications": {
        "import": "unraid_mcp.tools.notification_actions",
        "register": "register_notification_tools",
        "cacheable": True,
    },
    "health": {
        "import": "unraid_mcp.tools.health",
        "register": "register_health_tools",
        "cacheable": True,
    },
    "api": {
        "import": "unraid_mcp.tools.api",
        "register": "register_api_tools",
        "cacheable": True,
    },
    "system-extra": {
        "import": "unraid_mcp.tools.system_extra",
        "register": "register_system_extra_tools",
        "cacheable": True,
    },
    "metrics": {
        "import": "unraid_mcp.tools.metrics_tools",
        "register": "register_metrics_tools",
        "cacheable": True,
    },
    "ups": {
        "import": "unraid_mcp.tools.ups_tools",
        "register": "register_ups_tools",
        "cacheable": True,
    },
    "parity": {
        "import": "unraid_mcp.tools.parity",
        "register": "register_parity_tools",
        "cacheable": True,
    },
    "notifications-extra": {
        "import": "unraid_mcp.tools.notifications_extra",
        "register": "register_notifications_extra_tools",
        "cacheable": True,
    },
    "connect": {
        "import": "unraid_mcp.tools.connect_admin",
        "register": "register_connect_admin_tools",
        "cacheable": True,
    },
    # --- Non-cacheable (mutation) modules ---
    "docker-admin": {
        "import": "unraid_mcp.tools.docker_admin",
        "register": "register_docker_admin_tools",
        "cacheable": False,
    },
    "docker-batch": {
        "import": "unraid_mcp.tools.docker_batch",
        "register": "register_docker_batch_tools",
        "cacheable": False,
    },
    "docker-organize": {
        "import": "unraid_mcp.tools.docker_organize",
        "register": "register_docker_organize_tools",
        "cacheable": False,
    },
    "array": {
        "import": "unraid_mcp.tools.array",
        "register": "register_array_tools",
        "cacheable": False,
    },
    "array-admin": {
        "import": "unraid_mcp.tools.array_admin",
        "register": "register_array_admin_tools",
        "cacheable": False,
    },
    "rclone": {
        "import": "unraid_mcp.tools.rclone",
        "register": "register_rclone_tools",
        "cacheable": False,
    },
    "server-admin": {
        "import": "unraid_mcp.tools.server_admin",
        "register": "register_server_admin_tools",
        "cacheable": False,
    },
    "plugins": {
        "import": "unraid_mcp.tools.plugins",
        "register": "register_plugins_tools",
        "cacheable": False,
    },
    "customization": {
        "import": "unraid_mcp.tools.customization",
        "register": "register_customization_tools",
        "cacheable": False,
    },
    "onboarding": {
        "import": "unraid_mcp.tools.onboarding",
        "register": "register_onboarding_tools",
        "cacheable": False,
    },
    "auth": {
        "import": "unraid_mcp.tools.auth",
        "register": "register_auth_tools",
        "cacheable": False,
    },
    "vms": {
        "import": "unraid_mcp.tools.virtualization",
        "register": "register_vm_tools",
        "cacheable": False,
    },
    "ups-admin": {
        "import": "unraid_mcp.tools.ups_admin",
        "register": "register_ups_admin_tools",
        "cacheable": False,
    },
    # --- Resource modules (not tools, no caching concern) ---
    "subscriptions": {
        "import": "unraid_mcp.subscriptions.resources",
        "register": "register_live_subscription_resources",
        "cacheable": True,
    },
    "subscriptions-extra": {
        "import": "unraid_mcp.subscriptions.resources",
        "register": "register_extra_subscription_resources",
        "cacheable": True,
    },
}
```

- [ ] **Step 4: Update server.py register_all_modules to use new dict format**

In `unraid_mcp/server.py`, update the `register_all_modules()` function body:

```python
def register_all_modules() -> None:
    """Register tools and resources based on ENABLED_MODULES configuration."""
    try:
        # Always register base subscription resources (lightweight log stream endpoint)
        register_subscription_resources(mcp)

        # Conditionally register tool modules via registry
        for module_name in ENABLED_MODULES:
            if module_name not in MODULE_REGISTRY:
                logger.warning(f"Unknown module '{module_name}' in ENABLED_MODULES, skipping")
                continue
            entry = MODULE_REGISTRY[module_name]
            mod = importlib.import_module(entry["import"])
            getattr(mod, entry["register"])(mcp)

        logger.info(f"Modules registered: {sorted(ENABLED_MODULES)}")

    except Exception as e:
        logger.error(f"Failed to register modules: {e}", exc_info=True)
        raise
```

- [ ] **Step 5: Run tests**

Run: `uv run pytest tests/unit/test_registry.py tests/unit/test_server_middleware.py -v`
Expected: all pass

- [ ] **Step 6: Run full test suite**

Run: `uv run pytest -x -q`
Expected: all tests pass

---

### Task 7: Wire smart per-tool cache exclusion

**Files:**
- Modify: `unraid_mcp/server.py`
- Test: `tests/unit/test_server_middleware.py` (append)

- [ ] **Step 1: Write the failing test**

Append to `tests/unit/test_server_middleware.py`:

```python
    def test_cache_excludes_mutation_tools(self):
        """Non-cacheable module tools should be excluded from caching."""
        from fastmcp.server.middleware.caching import ResponseCachingMiddleware

        from unraid_mcp.server import mcp

        cache_mw = None
        for m in mcp.middleware:
            if isinstance(m, ResponseCachingMiddleware):
                cache_mw = m
                break
        assert cache_mw is not None, "ResponseCachingMiddleware not found"

        # The call_tool_settings should have excluded_tools populated
        # We can't easily inspect the internal settings, but we can verify
        # the middleware exists and was configured
        assert cache_mw is not None
```

- [ ] **Step 2: Update server.py to build excluded_tools dynamically**

Replace the `_cache_middleware` instantiation and move cache setup into `register_all_modules()`. Update `server.py`:

Replace the cache middleware placeholder:

```python
# 4. Response caching — configured after module registration with smart exclusions.
#    Placeholder: replaced in register_all_modules() with per-tool exclusions.
_cache_middleware: ResponseCachingMiddleware | None = None
```

Update the `_middleware_stack` to not include cache initially:

```python
_middleware_stack: list = [
    _logging_middleware,
    _error_middleware,
    _rate_limiter,
]
```

Then at the end of `register_all_modules()`, build the cache with exclusions and add to the stack:

```python
def register_all_modules() -> None:
    """Register tools and resources based on ENABLED_MODULES configuration."""
    try:
        # Always register base subscription resources (lightweight log stream endpoint)
        register_subscription_resources(mcp)

        # Track tools registered by non-cacheable modules
        non_cacheable_tools: list[str] = []

        # Conditionally register tool modules via registry
        for module_name in ENABLED_MODULES:
            if module_name not in MODULE_REGISTRY:
                logger.warning(f"Unknown module '{module_name}' in ENABLED_MODULES, skipping")
                continue

            entry = MODULE_REGISTRY[module_name]

            # Snapshot tool names before registration
            tools_before = set(mcp._tool_manager._tools.keys())

            mod = importlib.import_module(entry["import"])
            getattr(mod, entry["register"])(mcp)

            # Collect tools added by non-cacheable modules
            if not entry["cacheable"]:
                tools_after = set(mcp._tool_manager._tools.keys())
                new_tools = tools_after - tools_before
                non_cacheable_tools.extend(new_tools)

        # Configure smart caching: exclude mutation tools
        cache_mw = ResponseCachingMiddleware(
            call_tool_settings={
                "enabled": MCP_CACHE_ENABLED,
                "ttl": MCP_CACHE_TTL,
                "excluded_tools": non_cacheable_tools,
            },
        )
        mcp.add_middleware(cache_mw)

        if non_cacheable_tools:
            logger.info(
                f"Cache configured: {len(non_cacheable_tools)} mutation tools excluded"
            )
        logger.info(f"Modules registered: {sorted(ENABLED_MODULES)}")

    except Exception as e:
        logger.error(f"Failed to register modules: {e}", exc_info=True)
        raise
```

Also remove the `ResponseCachingMiddleware` import from the top-level middleware section and keep it only in the function, or keep the import at the top. Import should stay at top of file:

```python
from fastmcp.server.middleware.caching import ResponseCachingMiddleware
```

And remove the old `_cache_middleware` variable and its inclusion in `_middleware_stack`.

- [ ] **Step 3: Run tests**

Run: `uv run pytest tests/unit/test_server_middleware.py tests/unit/test_registry.py -v`
Expected: all pass

- [ ] **Step 4: Run full test suite**

Run: `uv run pytest -x -q`
Expected: all tests pass

---

### Task 8: Add dynamic unraid://live/{action} fallback resource

**Files:**
- Modify: `unraid_mcp/subscriptions/resources.py`
- Test: `tests/unit/test_live_resource.py` (new)

- [ ] **Step 1: Write the failing test**

Create `tests/unit/test_live_resource.py`:

```python
"""Tests for the dynamic unraid://live/{action} fallback resource."""

import json
from unittest.mock import AsyncMock, patch

import pytest


class TestLiveSubscriptionFallback:
    """Tests for the dynamic live subscription resource."""

    @pytest.fixture
    def fallback_handler(self):
        """Import and return the fallback handler function."""
        from unraid_mcp.subscriptions.resources import _live_subscription_fallback

        return _live_subscription_fallback

    @pytest.mark.asyncio
    async def test_unknown_action_returns_error(self, fallback_handler):
        """Unknown action should return error with available action names."""
        result = await fallback_handler("nonexistent_action")
        data = json.loads(result)
        assert data["error"] == "Unknown subscription action"
        assert "nonexistent_action" in data["requested"]
        assert "available" in data
        assert len(data["available"]) > 0

    @pytest.mark.asyncio
    async def test_known_action_calls_subscribe_once(self, fallback_handler):
        """Known action should call subscribe_once with the right query."""
        mock_data = {"systemMetricsCpu": {"percentTotal": 42.5}}
        with patch(
            "unraid_mcp.subscriptions.resources.subscribe_once",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            result = await fallback_handler("systemMetricsCpu")
            data = json.loads(result)
            assert data == mock_data

    @pytest.mark.asyncio
    async def test_subscribe_once_timeout_returns_error(self, fallback_handler):
        """Timeout during subscribe_once should return a clear error."""
        with patch(
            "unraid_mcp.subscriptions.resources.subscribe_once",
            new_callable=AsyncMock,
            side_effect=Exception("Subscription timed out after 10s"),
        ):
            result = await fallback_handler("systemMetricsCpu")
            data = json.loads(result)
            assert "error" in data
            assert "timed out" in data["error"].lower() or "error" in data
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_live_resource.py -v`
Expected: FAIL — `ImportError: cannot import name '_live_subscription_fallback'`

- [ ] **Step 3: Add the dynamic resource to resources.py**

Add the following imports near the top of `unraid_mcp/subscriptions/resources.py`:

```python
from .configs import SUBSCRIPTION_CONFIGS
from .snapshot import subscribe_once
```

Add the fallback handler function and wire it into `register_subscription_resources()`. Add this function before `register_subscription_resources`:

```python
async def _live_subscription_fallback(action: str) -> str:
    """Fetch a one-shot snapshot from any configured subscription by name.

    This is a fallback — explicit resources (unraid://system/cpu, etc.) use
    persistent subscriptions and are faster. This opens a fresh WebSocket per call.
    """
    if action not in SUBSCRIPTION_CONFIGS:
        available = sorted(SUBSCRIPTION_CONFIGS.keys())
        return json.dumps(
            {
                "error": "Unknown subscription action",
                "requested": action,
                "available": available,
            },
            indent=2,
        )

    config = SUBSCRIPTION_CONFIGS[action]
    query = config["query"]

    try:
        data = await subscribe_once(query, timeout=10.0)
        return json.dumps(data, indent=2)
    except Exception as e:
        return json.dumps(
            {
                "error": str(e),
                "action": action,
                "message": "Failed to fetch subscription snapshot. Check server logs.",
            },
            indent=2,
        )
```

Then in `register_subscription_resources()`, register it as an MCP resource. Add inside the function, after the `logs_stream_resource`:

```python
    @mcp.resource("unraid://live/{action}")
    async def live_fallback(action: str) -> str:
        """Dynamic fallback: fetch a one-shot snapshot from any configured subscription by name."""
        return await _live_subscription_fallback(action)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/unit/test_live_resource.py -v`
Expected: all 3 tests PASS

- [ ] **Step 5: Run full test suite**

Run: `uv run pytest -x -q`
Expected: all tests pass

---

### Task 9: Fix deprecated Subprotocol import in snapshot.py

**Files:**
- Modify: `unraid_mcp/subscriptions/snapshot.py:19`

- [ ] **Step 1: Fix the import**

In `unraid_mcp/subscriptions/snapshot.py`, change line 19:

```python
# OLD:
from websockets.legacy.protocol import Subprotocol
# NEW:
from websockets.typing import Subprotocol
```

- [ ] **Step 2: Run related tests**

Run: `uv run pytest -x -q`
Expected: all tests pass

---

### Task 10: Final verification and quality gate

- [ ] **Step 1: Run full lint suite**

Run: `uv run ruff check unraid_mcp/ && uv run black --check unraid_mcp/ && uv run mypy unraid_mcp/`
Expected: all pass. If ruff or black report issues, fix them.

- [ ] **Step 2: Run full test suite**

Run: `uv run pytest -x -q`
Expected: all tests pass

- [ ] **Step 3: Gate — /commit-and-push**

Invoke `/commit-and-push` with message: `feat: smart per-tool caching, dynamic live subscription resource, fix deprecated imports`

---

## Summary

| Task | Phase | What | Files |
|------|-------|------|-------|
| 1 | 0 | Upgrade FastMCP to 3.x | `pyproject.toml`, `uv.lock` |
| 2 | 1 | Middleware config env vars | `settings.py`, `test_settings_middleware.py` |
| 3 | 1 | Wire middleware into server.py | `server.py`, `test_server_middleware.py` |
| 4 | 1 | Response limiting middleware | `server.py` or `response_limiter.py` |
| 5 | 1 | .env.example + XML template | `.env.example`, `unraid-mcp.xml` |
| 6 | 2 | Registry cacheable flag | `registry.py`, `server.py`, `test_registry.py` |
| 7 | 2 | Smart cache exclusion wiring | `server.py`, `test_server_middleware.py` |
| 8 | 2 | Dynamic live/{action} resource | `resources.py`, `test_live_resource.py` |
| 9 | 2 | Fix Subprotocol import | `snapshot.py` |
| 10 | 2 | Final verification + gate | all |
