# Upstream Improvements Port — Design Spec

**Date**: 2026-04-01
**Status**: Approved
**Scope**: Port security fixes, auth, Dockerfile improvements, UX enhancements, and CI modernization from upstream (`jmagar/unraid-mcp`) into our fork (`nkissick-del/unraid-mcp`).

## Context

The upstream author published ~198 commits since our last sync. A triage identified 10 items worth porting, categorized by priority. Our fork uses a multi-tool architecture with configurable module presets — upstream switched to a consolidated single-tool pattern. We are NOT adopting their architectural changes, only porting discrete improvements that fit our design.

Key constraint: Unraid creates bind-mount directories as `nobody:users` (UID 99:GID 100) with 755 permissions. Non-root container users (e.g., UID 1000) cannot write to these directories without an entrypoint that fixes ownership first.

## Phase 1 — Security Hardening (P0)

### 1a. Path Traversal Fix

**Problem**: File path parameters passed to GraphQL mutations (e.g., flash_backup) can contain traversal sequences like `../../etc/shadow` to read arbitrary files on the Unraid server.

**Implementation**:
- Add `_validate_path(path: str, allowed_prefixes: list[str], param_name: str)` to `core/validation.py`
- Uses `posixpath.normpath` (not `os.path.normpath` — paths are remote Linux paths, `os.sep` is `\\` on Windows dev machines)
- Rejects null bytes (`\x00`)
- Splits on `/` to check for `..` components after normalization
- Validates resolved path starts with one of the allowed prefixes
- Apply to `validate_log_file_path()` (replace current implementation) and any tool accepting user-supplied file paths

**Files changed**: `core/validation.py`

### 1b. Input Validation Constants

**Problem**: RClone remote names and settings keys can contain shell metacharacters, path separators, or control characters, enabling injection attacks.

**Implementation**:
- Add `DANGEROUS_KEY_PATTERN` regex to `core/validation.py`: rejects `..`, path separators (`/`, `\\`), shell metacharacters (`|`, `;`, `$`, `` ` ``), HTML/XML chars (`&`, `<`, `>`, `"`, `'`, `#`), space (0x20), DEL (0x7F), and control chars (0x00-0x1F)
- Add `MAX_VALUE_LENGTH = 4096` constant
- Apply `DANGEROUS_KEY_PATTERN` in `validate_rclone_remote_name()` (augment existing regex)
- Apply in any settings key validation

**Files changed**: `core/validation.py`

### 1c. Improved `tool_error_handler`

**Problem**: Unhandled exceptions in tools produce raw tracebacks as user-facing errors, leaking internal details. `TimeoutError` gives no useful context.

**Implementation**:
- Add `tool_error_handler(tool_name: str, action: str, logger: Logger)` context manager to `core/exceptions.py`
- Re-raises `ToolError` as-is (already user-facing)
- Wraps `TimeoutError` with descriptive message: `"{tool_name}: {action} timed out — the Unraid server may be under heavy load"`
- Catches all other `Exception` with `logger.error(exc_info=True)` and raises `ToolError` with sanitized message: `"{tool_name}: {action} failed — check server logs for details"`
- No `CredentialsNotConfiguredError` — we use env vars, not elicitation
- Adopt in tool modules incrementally (not a hard requirement for this sprint)

**Files changed**: `core/exceptions.py`

### 1d. `safe_display_url()`

**Problem**: Log statements that include API URLs may leak path components, query parameters, or embedded credentials (CWE-200).

**Implementation**:
- Add `safe_display_url(url: str) -> str` to `core/utils.py`
- Parses URL, returns only `scheme://host:port` — strips path, query, fragment, credentials
- Falls back to `"<invalid-url>"` on parse failure
- Apply in `core/client.py` log statements and `config/settings.py` startup logging where API URLs are currently logged with paths

**Files changed**: `core/utils.py`, `core/client.py`, `config/settings.py`

### Phase 1 exit criteria
- All existing tests pass
- New unit tests for `_validate_path`, `DANGEROUS_KEY_PATTERN`, `tool_error_handler`, `safe_display_url`
- `/commit-and-push`

---

## Phase 2 — HTTP Bearer Token Auth + Healthcheck (P1)

### 2a. Bearer Token Auth Middleware

**Problem**: Anyone who can reach port 6970 can call MCP tools. No HTTP-level authentication.

**Design decisions**:
- Token provided via `UNRAID_MCP_AUTH_TOKEN` env var (user-set, no auto-generation)
- If env var is unset/empty, auth is **disabled** with a startup WARNING log
- No credential volume, no auto-generation — keeps the template self-contained
- ASGI middleware (not FastMCP middleware) — wraps the Starlette app before MCP message handling

**Implementation**:
- New file `core/auth.py` with two classes:

**`BearerAuthMiddleware(app, token, disabled=False)`**:
- Pure ASGI `__call__` pattern (no `BaseHTTPMiddleware` — avoids anyio stream overhead)
- Checks `Authorization: Bearer <token>` header on all HTTP requests
- Uses `hmac.compare_digest()` for constant-time comparison (prevents timing attacks)
- Per-IP failure rate limiting: max 60 failures per 60-second window (dict with TTL cleanup)
- Log throttling: one WARNING per IP per 30 seconds (prevents log injection abuse)
- Returns 401 with `WWW-Authenticate: Bearer` header on failure, JSON error body
- Returns 429 when rate limit exceeded
- Passes through WebSocket upgrade requests (MCP doesn't use WS auth this way)
- Passes through ASGI lifespan events

**`HealthMiddleware(app)`**:
- Intercepts `GET /health` requests, returns `200 {"status": "ok"}` immediately
- Placed OUTSIDE `BearerAuthMiddleware` so Docker healthchecks work without a token
- No other logic — single responsibility

**Middleware stack order** (outermost → innermost):
```
HealthMiddleware          → responds to GET /health
  BearerAuthMiddleware    → checks token on all other HTTP requests
    Starlette/FastMCP app → handles MCP protocol
      LoggingMiddleware        ─┐
      ErrorHandlingMiddleware   │ FastMCP middleware
      RateLimitingMiddleware    │ (wraps MCP message handling,
      ResponseLimitingMiddleware│  not HTTP requests)
      CachingMiddleware        ─┘
```

Note: ASGI middleware (Health, Bearer) wraps the HTTP layer. FastMCP middleware wraps the MCP protocol layer inside. They are applied differently:
- ASGI middleware: applied in `server.py` by wrapping the Starlette app after `mcp` creates it
- FastMCP middleware: applied via `mcp.add_middleware()` as currently done

**Integration in `server.py`**:
- Import `BearerAuthMiddleware`, `HealthMiddleware` from `core.auth`
- Read `UNRAID_MCP_AUTH_TOKEN` from settings
- `mcp.http_app()` returns a `StarletteWithLifespan` instance that supports `add_middleware()`. Use this to add ASGI middleware: `app = mcp.http_app(); app.add_middleware(BearerAuthMiddleware, token=token); app.add_middleware(HealthMiddleware)` (Starlette's `add_middleware` wraps outermost-first, so add Health last so it's outermost).
- Alternatively, construct the run manually: get the app, wrap it, and run via `uvicorn` directly instead of `mcp.run()`. Determine the cleaner approach during implementation.

### 2b. Dockerfile Healthcheck Update

- Replace the POST-based JSON-RPC healthcheck with: `curl -sf http://localhost:${UNRAID_MCP_PORT:-6970}/health || exit 1`
- Simpler, faster, doesn't require crafting a JSON-RPC payload
- Works because `HealthMiddleware` responds before auth

### 2c. Configuration Surface

Add `UNRAID_MCP_AUTH_TOKEN` to:
- `config/settings.py` — read from env, export as `MCP_AUTH_TOKEN`
- `unraid-mcp.xml` — new Config element: `<Config Name="Auth Token" Target="UNRAID_MCP_AUTH_TOKEN" ... Type="Variable" Display="advanced" Required="false" Mask="true"/>`
- `.env.example` — with comment explaining behavior when unset
- `docker-compose.yml` — in environment section

### Phase 2 exit criteria
- Auth enabled: requests without valid Bearer token get 401
- Auth disabled (no token): all requests pass through, startup WARNING logged
- `GET /health` always returns 200 regardless of auth state
- Rate limiting: >60 failed attempts from one IP in 60s returns 429
- Unit tests for both middleware classes
- Integration test: healthcheck works with auth enabled
- `/commit-and-push`

---

## Phase 3 — Dockerfile + CI Modernization (P1-P2)

### 3a. Dockerfile — Entrypoint-Chown Pattern

**Problem**: Upstream's simple `USER mcp` directive fails on Unraid because bind-mount directories are owned by `nobody:users` (99:100), and a UID 1000 user can't write to 755 directories.

**Solution**: LinuxServer.io-style entrypoint — start as root, fix ownership, drop privileges.

**Implementation**:

New `entrypoint.sh`:
```bash
#!/bin/sh
set -e

# Fix ownership of bind-mounted directories
# On Unraid, these are created as nobody:users (99:100) with 755
# The mcp user (1000:1000) needs write access
chown -R mcp:mcp /app/logs 2>/dev/null || true

# Drop to non-root and exec the server
exec gosu mcp "$@"
```

Updated Dockerfile:
- **Builder stage**: `python:3.11-slim` with uv (same base as current), `uv sync --frozen --no-dev`
- **Runtime stage**: `python:3.11-slim`
  - Install `curl` (healthcheck) and `gosu` (privilege dropping)
  - Create `mcp` user: `groupadd -g 1000 mcp && useradd -u 1000 -g mcp -m mcp`
  - Copy `.venv` and source from builder
  - Copy `entrypoint.sh`, make executable
  - `ENTRYPOINT ["/app/entrypoint.sh"]`
  - `CMD ["uv", "run", "unraid-mcp-server"]`
  - Healthcheck: `curl -sf http://localhost:${UNRAID_MCP_PORT:-6970}/health || exit 1`
  - Runs as root initially (entrypoint drops to mcp)

**Why `gosu` over `su-exec` or `setpriv`**: `gosu` is the de facto standard in Docker, handles signal forwarding correctly (PID 1 semantics), and is a single static binary. `su-exec` is Alpine-only. `setpriv` requires util-linux.

**Unraid XML template**: Remove `--cap-drop ALL` advice from ExtraParams (the entrypoint needs root briefly). Keep `--security-opt no-new-privileges:true` (prevents privilege escalation AFTER the initial drop).

**docker-compose.yml**: Remove `cap_drop: [ALL]`. Docker applies `cap_drop` to the entire container process from the start — including the entrypoint. With `cap_drop: [ALL]`, root loses `DAC_OVERRIDE` and the entrypoint can't `chown` bind-mounted directories. Keep `security_opt: [no-new-privileges:true]` (prevents privilege escalation after the initial drop). Document this change in CLAUDE.md.

### 3b. CI Additions

**`uv audit` job**: New job in `ci.yml` that runs `uv audit` (or `uv pip audit` depending on uv version) to check for known vulnerabilities in dependencies. Replaces/augments the existing `pip-audit` security job.

**`ruff format --check`**: Add to the lint job alongside existing `ruff check`. Replace `black --check` since ruff's formatter is a drop-in replacement and we already depend on ruff. Remove `black` from dev dependencies.

**Keep existing jobs**: mypy, hadolint, trivy container scan. No changes.

### Phase 3 exit criteria
- Container starts, `chown`s bind mounts, drops to UID 1000
- `docker exec unraid-mcp whoami` returns `mcp`
- Logs are written successfully to the bind-mounted directory
- Healthcheck passes
- CI: `uv audit` job runs, `ruff format --check` passes
- `/commit-and-push`

---

## Phase 4 — UX Improvements (P2-P3)

### 4a. Destructive Action Gating

**Problem**: Mutation tools like `manage_docker_container(action="stop")` execute without confirmation. An LLM hallucinating a tool call could stop critical services.

**Implementation**:
- New file `core/guards.py`
- `gate_destructive_action(ctx, action, destructive_actions, confirm, description)`:
  - If `action` not in `destructive_actions` set → no-op
  - If `confirm=True` → proceed
  - If MCP context supports elicitation → prompt user via `ctx.elicit()` with a confirmation model
  - If elicitation unavailable → raise `ToolError("Action '{action}' requires confirm=True")`
- Apply to `manage_docker_container` for `stop`, `restart`, `kill` actions
- Add `confirm: bool = False` parameter to gated tools
- Future admin tools (array, VM) will use the same pattern

### 4b. Subscription Error Dedup

**Problem**: The `array_state` subscription generates repeated GraphQL errors due to an upstream Unraid API bug, flooding logs with identical ERROR entries.

**Implementation**:
- Add to `subscriptions/manager.py`:
  - `_last_graphql_error: dict[str, str]` — maps subscription name to last error message
  - `_graphql_error_count: dict[str, int]` — maps subscription name to repeat count
- On GraphQL error in `_process_ws_message()`:
  - If error message matches `_last_graphql_error[sub_name]`: increment count, log at DEBUG
  - At counts 10, 100, 1000: log a WARNING reminder with total count
  - If error message differs: reset counter, log at WARNING (first occurrence)
- Non-GraphQL errors (connection, auth) remain at ERROR level

### 4c. `version.py`

- New file `unraid_mcp/version.py`: uses `importlib.metadata.version("unraid-mcp")` with `PackageNotFoundError` fallback to `"0.0.0"`
- Update `__init__.py` to import from `version.py` instead of hardcoding
- Update `server.py` to use `VERSION` from `version.py`

### Phase 4 exit criteria
- Destructive actions require confirmation or `confirm=True`
- Repeated subscription errors downgrade to DEBUG after first occurrence
- `VERSION` reads from package metadata
- Unit tests for all three features
- `/commit-and-push`

---

## Phase 5 — Documentation Sweep

After all implementation phases, audit and update every documentation surface:

### 5a. CLAUDE.md
- Update architecture section: ASGI middleware stack (HealthMiddleware, BearerAuthMiddleware) + FastMCP middleware
- Update gotchas: revise `cap_drop` advice for new entrypoint pattern, add entrypoint-chown gotcha
- Add FastMCP 3.x ASGI middleware integration notes
- Verify all tool counts and module lists are still accurate

### 5b. README.md
- Add auth setup instructions (how to set token, behavior when unset)
- Update quick start examples with `UNRAID_MCP_AUTH_TOKEN`
- Update Docker Compose example
- Update config table with all new env vars
- Update Development section if any commands changed (ruff format replacing black)

### 5c. XML Template
- Add `UNRAID_MCP_AUTH_TOKEN` Config element
- Update Overview text if needed
- Verify ExtraParams are correct for new entrypoint

### 5d. Other files
- `.env.example`: all new env vars with comments
- `docker-compose.yml`: comments for new env vars, security settings
- Verify existing gotchas in CLAUDE.md are still accurate after changes

### Phase 5 exit criteria
- All docs accurately reflect the implemented state
- No stale references to old patterns (black, POST healthcheck, cap_drop ALL in compose)
- `/commit-and-push`

---

## Out of Scope

- Upstream's consolidated single-tool architecture
- Domain split of tool internals (`_array.py`, `_disk.py`, etc.)
- Elicitation-based credential setup
- Removal of `docker-publish.yml`
- Switch from mypy to ty
- Version-sync between pyproject.toml and plugin.json
- `.beads/`, `.omc/`, hooks, skills, AGENTS.md
