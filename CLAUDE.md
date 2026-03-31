# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
This is an MCP (Model Context Protocol) server that provides tools to interact with an Unraid server's GraphQL API. The server is built using FastMCP with a **modular architecture** consisting of separate packages for configuration, core functionality, subscriptions, and tools.

## Development Commands

### Setup
```bash
# Initialize uv virtual environment and install dependencies
uv sync

# Install dev dependencies
uv sync --group dev
```

### Running the Server
```bash
# Local development with uv (recommended)
uv run unraid-mcp-server

# Using development script with hot reload
./dev.sh

# Direct module execution
uv run -m unraid_mcp.main
```

### Code Quality
```bash
# Format code with black
uv run black unraid_mcp/

# Lint with ruff
uv run ruff check unraid_mcp/

# Type checking with mypy
uv run mypy unraid_mcp/

# Run tests
uv run pytest
```

### Docker Development
```bash
# Build the Docker image
docker build -t unraid-mcp-server .

# Run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f unraid-mcp

# Stop service
docker-compose down
```

### Environment Setup
- Copy `.env.example` to `.env` and configure:
  - `UNRAID_API_URL`: Unraid GraphQL endpoint (required)
  - `UNRAID_API_KEY`: Unraid API key (required)
  - `UNRAID_MCP_TRANSPORT`: Transport type (default: streamable-http)
  - `UNRAID_MCP_PORT`: Server port (default: 6970)
  - `UNRAID_MCP_HOST`: Server host (default: 0.0.0.0)

## Architecture

### Core Components
- **Main Server**: `unraid_mcp/server.py` - Modular MCP server with FastMCP integration
- **Entry Point**: `unraid_mcp/main.py` - Application entry point and startup logic
- **Configuration**: `unraid_mcp/config/` - Settings management and logging configuration
- **Core Infrastructure**: `unraid_mcp/core/` - GraphQL client, exceptions, and shared types
- **Subscriptions**: `unraid_mcp/subscriptions/` - Real-time WebSocket subscriptions and diagnostics
- **Tools**: `unraid_mcp/tools/` - Domain-specific tool implementations
- **GraphQL Client**: Uses httpx for async HTTP requests to Unraid API
- **Transport Layer**: Supports streamable-http (recommended), SSE (deprecated), and stdio

### Key Design Patterns
- **Modular Architecture**: Clean separation of concerns across focused modules
- **Error Handling**: Uses ToolError for user-facing errors, detailed logging for debugging
- **Timeout Management**: Custom timeout configurations for different query types
- **Data Processing**: Tools return both human-readable summaries and detailed raw data
- **Health Monitoring**: Comprehensive health check tool for system monitoring
- **Real-time Subscriptions**: WebSocket-based live data streaming

### Default Module Preset (32 Tools)
1. **System** (7 tools): `get_system_info`, `get_array_status`, `get_network_config`, `get_registration_info`, `get_connect_settings`, `get_unraid_variables`, `manage_docker_container`
2. **Docker** (4 tools): `list_docker_containers`, `get_docker_container_details`, `get_docker_container_logs`, `manage_docker_container`
3. **Storage** (7 tools): `get_shares_info`, `list_physical_disks`, `get_disk_details`, `list_available_log_files`, `get_logs`, `get_notifications_overview`, `list_notifications`
4. **Health** (1 tool): `health_check`
5. **API** (2 tools): `query_unraid_api`, `introspect_schema`
6. **System Extra** (5 tools): `is_server_online`, `get_config_status`, `get_flash_info`, `get_services`, `get_servers`
7. **Metrics** (3 tools): `get_system_metrics`, `get_system_time`, `get_timezone_options`
8. **UPS** (3 tools): `list_ups_devices`, `get_ups_device`, `get_ups_configuration`

Extended adds ~46 tools (notifications, plugins, parity, customization, connect, docker-admin, docker-batch, array, rclone, diagnostics). All adds ~51 more (auth, server-admin, array-admin, vms, onboarding, docker-organize, ups-admin, subscriptions).

### Environment Variable Hierarchy
The server loads environment variables from multiple locations in order:
1. `/app/.env.local` (container mount)
2. `../.env.local` (project root)
3. `../.env` (project root)
4. `.env` (local directory)

### Transport Configuration
- **streamable-http** (recommended): HTTP-based transport on `/mcp` endpoint
- **sse** (deprecated): Server-Sent Events transport
- **stdio**: Standard input/output for direct integration

### Error Handling Strategy
- GraphQL errors are converted to ToolError with descriptive messages
- HTTP errors include status codes and response details
- Network errors are caught and wrapped with connection context
- All errors are logged with full context for debugging

### Middleware Stack (server.py)
The server uses a FastMCP middleware chain (outermost → innermost):
1. **LoggingMiddleware** — logs `tools/call` and `resources/read` requests
2. **ErrorHandlingMiddleware** — catches exceptions, includes tracebacks only at DEBUG level
3. **SlidingWindowRateLimitingMiddleware** — configurable via `UNRAID_MCP_RATE_LIMIT` / `UNRAID_MCP_RATE_WINDOW_MINUTES`
4. **ResponseLimitingMiddleware** — caps response size via `UNRAID_MCP_MAX_RESPONSE_KB`
5. **ResponseCachingMiddleware** — added after module registration with per-tool exclusions for mutation tools

### Performance Considerations
- Increased timeouts for disk operations (90s read timeout)
- Selective queries to avoid GraphQL type overflow issues
- Per-tool response caching with configurable TTL (mutation tools excluded)
- Rotating log files to prevent disk space issues

## Workflow Rules

### Plans must include commit-and-push
Every implementation plan MUST include `/commit-and-push` as the final step. The workflow is: do the work, verify you're happy with it, then invoke `/commit-and-push` which handles the full quality gate loop (CodeRabbit review, lint, test, commit, push, monitor CI, fix and loop on failures until all green).

## Sprint Learnings & Gotchas

### macOS `/tmp` symlink resolution (Phase 8c)
On macOS, `/tmp` is a symlink to `/private/tmp`. When using `Path.resolve()` on an existing path under `/tmp`, the resolved path becomes `/private/tmp/...` which fails prefix checks against `/tmp`. **Fix:** check both the literal string (`str(path)`) and the resolved string (`str(path.resolve())`) against allowed prefixes. This only matters on macOS dev machines — Linux containers are unaffected — but tests must pass on both.

### Module-level imports in `settings.py` (Phase 8c)
`settings.py` executes at import time (no functions, just top-level statements). Adding an import like `from ..core.constants import X` midway through the file triggers ruff's `E402` (module-level import not at top of file). **Fix:** move the import to the top of the file alongside the other imports, not inline where it's used.

### Sync-to-async method signature changes propagate (Phase 8d)
Changing `get_resource_data()` and `get_subscription_status()` from sync `def` to `async def` requires updating every caller to add `await`. Callers to check: `subscriptions/resources.py`, `subscriptions/diagnostics.py`, and all tests. Missing an `await` produces no immediate error — the method returns a coroutine object instead of the data, which evaluates as truthy, causing subtle bugs.

### Error Handling Pattern (Phase 8a)
User-facing `ToolError` messages should contain only the minimum needed to understand the failure (e.g., HTTP status code). Raw API response bodies, stack traces, and internal paths stay in `logger.error()` only. This prevents information leakage while keeping debug info accessible in logs.

### Test assertions must match exact error message text (Phase 8a)
When changing a `ToolError` message string, grep tests for `pytest.raises(ToolError, match=...)` — the `match` parameter is a regex against the exception message. Forgetting to update the test assertion is a silent failure until pytest runs.

### `settings.py` reload behavior in tests (Phase 8c)
Since `settings.py` uses module-level code, tests that validate different env var combinations must `importlib.reload()` the module within each test. Use `warnings.catch_warnings(record=True)` to capture and assert on warnings emitted during reload. Each test should be self-contained — prior reloads in the same process can leave stale state.

### Docker daemon not available in dev environment
The dev machine (macOS) may not have Docker daemon running. Docker build verification (`docker build -t unraid-mcp-server .`) should be treated as a CI-only check when the daemon is unavailable locally. All other quality gates (black, ruff, mypy, pytest) run locally.

### Security hardening — cap_drop ALL differs between compose and XML template
`cap_drop: [ALL]` works in `docker-compose.yml` because Docker Compose creates bind-mount directories as `root:root`. However, the Unraid Docker UI (XML template) creates them as `nobody:users`. With `cap_drop ALL`, root loses `DAC_OVERRIDE` and can't write to `nobody`-owned directories. Therefore: use `cap_drop: [ALL]` in compose, but NOT in the XML template's `<ExtraParams>`. Do NOT use `read_only: true` anywhere — `uv` needs `/app/.cache/uv` at startup.

### Dockerfile healthcheck must use POST for streamable-http
The MCP streamable-http transport only accepts POST requests. A `curl -f GET /mcp` healthcheck returns 406 Not Acceptable, making Docker report the container as unhealthy even though the server is running. The healthcheck must send a valid MCP `initialize` JSON-RPC POST request.

### FastMCP 3.x removed `_tool_manager` (v3.2.0 upgrade)
FastMCP 2.x exposed `mcp._tool_manager._tools` for enumerating registered tools. This was removed in 3.x. The replacement is `mcp.providers[0]._components` — a dict with keys like `tool:name@`. The helper `_get_tool_names()` in `server.py` encapsulates this. Both `_components` and `providers` are internal APIs, so guard defensively and expect this to break again on major upgrades. `list_tools()` exists but is async-only, which doesn't work in the synchronous `register_all_modules()` flow.