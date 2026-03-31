# Middleware Stack, Smart Caching & Dynamic Resource Fallback

**Date:** 2026-03-31
**Status:** Approved
**Approach:** B — Upgrade FastMCP + smart per-tool caching leveraging multi-tool architecture

## Motivation

The upstream `jmagar/unraid-mcp` repo added a production-quality middleware stack (rate limiting, error handling, logging, response capping, caching) that this fork lacks. However, upstream had to disable caching entirely because their single consolidated `unraid` tool mixes reads and mutations under one name.

This fork's multi-tool architecture (127 tools across 27 modules) lets us do better: cache read-only tools selectively while excluding mutation tools by name. This design adds the middleware stack, upgrades FastMCP to 3.x for built-in middleware support, and adds a dynamic subscription resource fallback.

## Phases

### Phase 0: FastMCP Upgrade

**Goal:** Bump FastMCP from 2.14.5 to 3.x to gain built-in middleware classes.

**Changes:**
- `pyproject.toml`: Change `fastmcp>=2.14.2,<3.0` to `>=3.2.0,<4.0`
- Run `uv sync` to update lockfile
- Run full test suite (506 tests must pass)

**Migration risk:** Low. The codebase uses only three FastMCP surfaces:
- `from fastmcp import FastMCP` (30 files) — kept in 3.x
- `from fastmcp.exceptions import ToolError` (1 file) — kept in 3.x
- `from fastmcp.utilities.logging import get_logger` (1 file) — needs verification

**3.0 breaking changes that affect us:** 16 deprecated `FastMCP()` constructor kwargs were removed. We only use `name`, `instructions`, `version`, `lifespan`, and `middleware` — all kept.

**Rollback:** If 3.x is fundamentally incompatible, pin to `>=2.14.5,<3.0` and write a custom `ResponseLimitingMiddleware` (~20 lines). All other middleware classes exist in 2.14.5.

**Gate:** `/commit-and-push` — full quality gate loop (CodeRabbit, lint, test, commit, push, CI).

---

### Phase 1: Middleware Stack + Configuration

**Goal:** Add 5 middleware layers to `server.py` with env-var-driven configuration.

#### Middleware Chain (outermost to innermost)

Order matters — each layer wraps everything inside it:

1. **LoggingMiddleware** — Logs every `tools/call` and `resources/read` with duration and errors. Uses existing `logger` instance from `config/logging.py`.

2. **ErrorHandlingMiddleware** — Catches unhandled exceptions, converts to proper MCP errors. Includes tracebacks only when `LOG_LEVEL` is `DEBUG` (prevents information leakage in production).

3. **SlidingWindowRateLimitingMiddleware** — Caps total requests per sliding window. Prevents a runaway LLM from hammering the Unraid API. Note: does not cap sub-window bursts; use nginx `limit_req` in front for tighter burst control.

4. **ResponseLimitingMiddleware** — Truncates oversized tool responses to protect the client LLM's context window. Responses over the limit are truncated with a clear suffix message rather than erroring. If this class doesn't exist in 3.x, implement a custom middleware (~20 lines) that measures `len(json.dumps(result))` and truncates.

5. **ResponseCachingMiddleware** — Per-tool caching with smart read/write separation (see Phase 2).

#### Configuration

New environment variables in `settings.py`:

| Env Var | Type | Default | Purpose |
|---------|------|---------|---------|
| `UNRAID_MCP_RATE_LIMIT` | int | `540` | Max requests per sliding window |
| `UNRAID_MCP_RATE_WINDOW_MINUTES` | int | `1` | Sliding window duration in minutes |
| `UNRAID_MCP_MAX_RESPONSE_KB` | int | `512` | Max response size in KB before truncation |
| `UNRAID_MCP_CACHE_TTL` | int | `30` | Cache TTL in seconds for read-only tools |
| `UNRAID_MCP_CACHE_ENABLED` | bool | `true` | Master toggle to disable all caching |

#### File Changes

- **`unraid_mcp/config/settings.py`** — Add the 5 new env vars with defaults, loaded same way as existing config (os.getenv with type conversion).
- **`unraid_mcp/server.py`** — Import middleware classes, instantiate each with config values, pass `middleware=[...]` to `FastMCP()` constructor.
- **`.env.example`** — Add the new env vars with comments explaining each.
- **`unraid-mcp.xml`** — Add the 5 new env vars as `<Config>` entries in the Unraid Community Applications XML template, under `Display="advanced"` with sensible defaults matching the env var defaults. This ensures Unraid users can configure middleware from the Docker UI without editing env files.

**Gate:** `/commit-and-push`

---

### Phase 2: Smart Caching, Dynamic Resource Fallback & Cleanup

#### 2a: Smart Per-Tool Caching

**Goal:** Cache read-only tools while excluding mutation tools, leveraging the multi-tool architecture.

**Module classification:**

Cacheable (read-only queries):
- `system`, `system-extra`, `metrics`, `ups`, `health`, `storage`, `docker`, `api`, `notifications`, `notifications-extra`, `parity`, `diagnostics`, `connect`

Excluded from cache (mutations or state-changing):
- `docker-admin`, `docker-batch`, `docker-organize`, `array`, `array-admin`, `rclone`, `server-admin`, `plugins`, `customization`, `onboarding`, `auth`, `vms`, `ups-admin`

**Implementation:**

- **`unraid_mcp/registry.py`** — Add a `cacheable` flag to each registry entry. Change the tuple `(import_path, func_name)` to a dict: `{"import": str, "register": str, "cacheable": bool}`.
- **`unraid_mcp/server.py`** — At startup, iterate the registry to build the list of non-cacheable tool names. Pass to `CallToolSettings(excluded_tools=[...])`. Note: `CallToolSettings` is a TypedDict, so it's constructed as a dict: `CallToolSettings(excluded_tools=[...], ttl=CACHE_TTL)`.

**Why this works:** The module split already separates reads from writes. `docker` contains `list_docker_containers` and `get_docker_container_details` (reads). `docker-admin` contains `manage_docker_container` (mutations). No individual tool straddles the line.

#### 2b: Dynamic `unraid://live/{action}` Fallback Resource

**Goal:** Add a single dynamic resource that can access any configured subscription by name, as a fallback to the explicit resources.

**Implementation:**

Register one resource in `resources.py`:

```python
@mcp.resource("unraid://live/{action}")
async def live_subscription_fallback(action: str) -> str:
    """Fallback: fetch a snapshot from any configured subscription by name."""
```

**Behavior:**
1. Look up `action` in `SUBSCRIPTION_CONFIGS` from `configs.py`
2. If not found, return a JSON error with available action names
3. If found, call `subscribe_once(query, variables, timeout=10.0)`
4. Return the snapshot data as JSON

**Where to register:** In `register_subscription_resources()` (always-on, not gated behind a module flag) since it's a lightweight fallback that doesn't maintain persistent connections.

**Relationship to explicit resources:** The explicit resources (`unraid://system/cpu`, etc.) remain the primary interface. They use the persistent subscription manager and return cached data. The dynamic fallback uses `subscribe_once()` — a fresh one-shot WebSocket connection — so it's slower but always works regardless of which subscription modules are enabled.

#### 2c: Fix Remaining Deprecated Import

**File:** `unraid_mcp/subscriptions/snapshot.py` line 19
**Change:** `from websockets.legacy.protocol import Subprotocol` to `from websockets.typing import Subprotocol`

(Same fix already applied to `diagnostics.py` and `manager.py` in the pre-design bugfix batch.)

**Gate:** `/commit-and-push`

---

## Testing Strategy

**Phase 0:** Existing 506 tests must pass after upgrade. No new tests needed — the upgrade is validated by the existing suite.

**Phase 1:** Add tests for:
- Middleware instantiation with default config values
- Middleware instantiation with custom env var overrides
- Verify middleware list is passed to FastMCP constructor (mock-based)

**Phase 2:**
- Registry `cacheable` flag: verify all entries have the flag, verify the excluded tools list is built correctly
- Dynamic resource: test with valid action name, test with invalid action name (returns error with available names), test subscription timeout handling
- Import fix: covered by existing snapshot tests

## Files Changed (Summary)

| File | Phase | Change |
|------|-------|--------|
| `pyproject.toml` | 0 | Bump fastmcp version constraint |
| `uv.lock` | 0 | Auto-updated by `uv sync` |
| `unraid_mcp/config/settings.py` | 1 | Add 5 middleware env vars |
| `unraid_mcp/server.py` | 1, 2 | Add middleware stack, build cache exclusion list |
| `.env.example` | 1 | Document new env vars |
| `unraid-mcp.xml` | 1 | Add 5 middleware env vars to Unraid XML template |
| `unraid_mcp/registry.py` | 2 | Add `cacheable` flag to all entries |
| `unraid_mcp/subscriptions/resources.py` | 2 | Add `unraid://live/{action}` fallback |
| `unraid_mcp/subscriptions/snapshot.py` | 2 | Fix Subprotocol import |
| `tests/unit/test_middleware.py` | 1 | New: middleware config tests |
| `tests/unit/test_live_resource.py` | 2 | New: dynamic resource tests |
