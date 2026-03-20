# Codebase Audit & Security Hardening Plan

> Living tracking document. Each phase is self-contained — ask Claude to "implement Phase N" to execute.

---

## Phase 1: Foundation ✅ (completed 2026-03-20, commit 65254a6)
- [x] HTTP connection pooling (`core/client.py`) — singleton AsyncClient with asyncio.Lock
- [x] Remove dead exception class (`core/exceptions.py`) — `IdempotentOperationError` removed
- [x] Extract shared helpers (`core/utils.py`) — `ensure_dict`, `ensure_list`, `format_bytes`, `format_kb`
- [x] Update tool files to use shared helpers (system, storage, docker, virtualization, rclone)
- [x] Fix temperature 0°C truthiness bug in `storage.py` (CodeRabbit catch)
- [x] Apply black formatting across all files for CI compliance

## Phase 2: Security & Validation ✅ (completed 2026-03-20)
- [x] Harden GraphQL field interpolation (`virtualization.py`, `docker.py`) — dict-based mutation lookup
- [x] Input validation on tool params — `log_file_path`, `offset`/`limit`, `container_id`, `disk_id`, etc.
- [x] Truncate error responses (`client.py`) — `e.response.text` capped at 500 chars
- [x] Add dependency upper bounds (`pyproject.toml`) — all deps capped at `<NEXT_MAJOR`

## Phase 3: Reliability & Error Handling ✅ (completed 2026-03-20)
- [x] Fix subscription startup race condition (`resources.py`) — asyncio.Lock double-check guard
- [x] Add graceful shutdown via FastMCP lifespan (`server.py`) — stop subscriptions + close HTTP client
- [x] Deduplicate WebSocket auth (`manager.py`) — extracted `_build_ws_auth_payload()` helper
- [x] Replace silent failures with explicit warnings — `logger.warning` in rclone, storage, docker tools
- [x] Use specific exception catches instead of bare `except Exception` — narrowed in manager.py and docker.py

## Phase 4: Performance & Infrastructure ✅ (completed 2026-03-20)
- [x] Dockerfile — multi-stage build, curl healthcheck, `PYTHONUNBUFFERED=1`, persistent logs
- [x] Fix logging filesystem I/O (`logging.py`) — counter-based throttling, eliminated redundant stat calls
- [x] Structured/JSON logging option for production — `UNRAID_MCP_LOG_FORMAT=json`
- [x] Fix CI `pip-audit` — temp file instead of process substitution, removed `--no-deps`
- [x] Fix `dev.sh` portability — `stat -f%z` → `wc -c` (POSIX portable)

## Phase 5: Polish & Tests ✅ (completed 2026-03-21)
- [x] Unit tests for GraphQL client, core tools, subscriptions (91 tests passing)
- [x] Remaining DRY cleanup — `_CONTAINER_LIST_FIELDS` in docker.py
- [x] Standardize error message format across tools
- [x] Extract magic numbers/strings to `core/constants.py`

---

## Phase 6: Critical Security Fixes

> CRITICAL severity. These are exploitable vulnerabilities that should be fixed before any public deployment.

### 6a — GraphQL mutation bypass via regex (`tools/api.py`)
**Severity:** CRITICAL
**File:** `tools/api.py:196-224`
**Issue:** `query_unraid_api` uses `re.search(r"\bmutation\b", ...)` to block mutations. Bypass is possible via whitespace tricks, unicode escapes, or nested query structures.
**Fix:**
- Add `graphql-core` as a dependency
- Parse the query string into an AST with `graphql.parse()`
- Walk the AST and reject any `OperationType` that is not `query`
- Remove the regex-based check entirely

### 6b — Unsafe WebSocket URL construction (`subscriptions/manager.py`)
**Severity:** CRITICAL
**File:** `subscriptions/manager.py:208-216`
**Issue:** `UNRAID_API_URL` is naively string-sliced (`"https://"` prefix swap) to build WebSocket URLs. No host/scheme validation. Could enable SSRF if the env var is compromised.
**Fix:**
- Parse `UNRAID_API_URL` with `urllib.parse.urlparse()`
- Validate scheme is `http` or `https`, hostname is non-empty
- Reconstruct WS URL explicitly: `urlunparse((ws_scheme, parsed.netloc, path, ...))`
- Reject URLs with empty hosts, userinfo, or fragments
- Extract to a helper function `_build_ws_url(api_url: str) -> str` for testability

### 6c — API key over-exposed in WS auth payload (`subscriptions/manager.py`)
**Severity:** CRITICAL
**File:** `subscriptions/manager.py:31-43`
**Issue:** `_build_ws_auth_payload()` puts the API key in 7 redundant fields across the payload dict. If any debug logging captures this dict, the key leaks. The subscription diagnostics tool (`test_subscription_query`) also surfaces this.
**Fix:**
- Reduce to a single standard auth method: `{"Authorization": f"Bearer {UNRAID_API_KEY}"}`
- Remove redundant `X-API-Key`, `x-api-key`, and nested `headers` dict
- Add `[REDACTED]` replacement in any log/debug output of the init payload
- Audit `diagnostics.py` to ensure auth payload is never surfaced to tool output

### 6d — Log file path validation misses symlinks (`core/utils.py`)
**Severity:** CRITICAL
**File:** `core/utils.py:79-89`
**Issue:** `validate_log_file_path()` blocks `..` but does not resolve symlinks. A symlink `/var/log/safe -> /etc/shadow` would pass validation. The path is then sent to the Unraid GraphQL API (not read locally), but the API-side behavior is unknown.
**Fix:**
- This path is sent to the remote API, not opened locally, so `Path.resolve()` cannot help
- Add an allowlist of permitted path prefixes: `/var/log/`, `/boot/logs/`, `/mnt/user/`
- Add a constant `ALLOWED_LOG_PREFIXES` to `core/constants.py`
- Reject paths not starting with any allowed prefix

### Verification
1. `uv run pytest tests/unit/ -v` — all tests pass (add new tests for each fix)
2. `uv run ruff check unraid_mcp/` — no lint errors
3. `uv run mypy unraid_mcp/` — type checking passes

---

## Phase 7: High-Severity Hardening

> HIGH severity. Defense-in-depth measures that reduce attack surface and prevent misuse.

### 7a — SSL verification warning (`config/settings.py`)
**Severity:** HIGH
**File:** `config/settings.py:42-48`
**Issue:** `UNRAID_VERIFY_SSL=false` disables all TLS cert checks silently. Default is safe (`true`), but no warning is emitted when disabled.
**Fix:**
- After loading `UNRAID_VERIFY_SSL`, if it is `False`, set a flag
- In `log_configuration_status()` (`config/logging.py`), emit `logger.critical("SSL certificate verification is DISABLED — this is unsafe in production")`
- Add a comment in `.env.example` warning against disabling in production

### 7b — HTTP connection pool limits (`core/client.py`)
**Severity:** HIGH
**File:** `core/client.py:36-42`
**Issue:** `httpx.AsyncClient` has no explicit `limits=` parameter. Unbounded concurrent requests could exhaust file descriptors.
**Fix:**
- Add `limits=httpx.Limits(max_connections=20, max_keepalive_connections=10)` to the client constructor
- Add constants `HTTP_MAX_CONNECTIONS = 20` and `HTTP_MAX_KEEPALIVE = 10` to `core/constants.py`

### 7c — RClone remote name validation (`tools/rclone.py`)
**Severity:** HIGH
**File:** `tools/rclone.py:112-155`
**Issue:** `create_rclone_remote()` and `delete_rclone_remote()` accept arbitrary `name` without character or length validation.
**Fix:**
- Add `validate_rclone_remote_name()` to `core/utils.py`: pattern `^[a-zA-Z0-9_-]{1,64}$`
- Call it in both `create_rclone_remote()` and `delete_rclone_remote()`
- Validate `provider_type` is non-empty string

### 7d — Stricter container ID validation (`tools/docker.py`)
**Severity:** HIGH
**File:** `tools/docker.py:56-64`
**Issue:** `_is_container_id()` returns `True` for any string containing `:`, which is overly permissive. `"not:a:container"` passes.
**Fix:**
- Change colon check to validate prefixed ID format: `^[a-z0-9]+:[0-9a-f]{12,64}$`
- Add constant `CONTAINER_PREFIXED_ID_PATTERN` to `core/constants.py`
- Update existing tests in `test_docker_helpers.py`

### 7e — Subscription query validation (`subscriptions/manager.py`)
**Severity:** HIGH
**File:** `subscriptions/manager.py:116-148`
**Issue:** `start_subscription()` accepts arbitrary GraphQL queries without checking operation type. Could execute mutations via WebSocket.
**Fix:**
- If `graphql-core` is added in Phase 6a, reuse the parser here
- Validate that the parsed operation type is `subscription`
- Reject `query` and `mutation` operation types
- Alternatively, only allow queries from the predefined `subscription_configs` dict (whitelist approach)

### Verification
1. `uv run pytest tests/unit/ -v` — all tests pass
2. `uv run ruff check unraid_mcp/` — no lint errors
3. `uv run mypy unraid_mcp/` — type checking passes

---

## Phase 8: Medium-Severity Improvements

> MEDIUM severity. Reduces information disclosure, improves async safety, hardens container config.

### 8a — Sanitize error messages returned to users (`core/client.py`)
**Severity:** MEDIUM
**File:** `core/client.py:190-199`
**Issue:** HTTP error responses are truncated at 500 chars but may still contain internal paths, stack traces, or database errors from the Unraid API.
**Fix:**
- For `HTTPStatusError`: return generic message `"Unraid API returned HTTP {status_code}"` to the user
- Log the full truncated response at ERROR level for debugging
- Keep the detailed message in the `from e` chain for programmatic access

### 8b — Redact registration key contents (`tools/system.py`)
**Severity:** MEDIUM
**File:** `tools/system.py:268-272`
**Issue:** `get_registration_info()` queries `keyFile { location contents }` and returns the full license key contents to the MCP client.
**Fix:**
- Remove `contents` from the GraphQL query — only fetch `location`
- Or: redact the `contents` field before returning: `result["keyFile"]["contents"] = "[REDACTED]"`

### 8c — Validate log directory at startup (`config/settings.py`)
**Severity:** MEDIUM
**File:** `config/settings.py:53-58`
**Issue:** `UNRAID_MCP_LOG_DIR` from env is used directly with `mkdir(parents=True)`, which could create arbitrary directories. `UNRAID_MCP_LOG_FILE` is not validated for path traversal.
**Fix:**
- Validate `LOG_FILE_NAME` does not contain `/` or `..`
- Validate `LOGS_DIR` resolves to a path under `/app/`, `/tmp/`, or `/var/log/`
- Add allowed log directory list to `core/constants.py`

### 8d — Add asyncio.Lock to `resource_data` access (`subscriptions/manager.py`)
**Severity:** MEDIUM
**File:** `subscriptions/manager.py:51`
**Issue:** `resource_data` dict is written by subscription loop tasks and read by `get_resource_data()` without synchronization. Dict operations are atomic in CPython but not guaranteed by the language spec — and compound read-modify-write sequences are not safe.
**Fix:**
- Add a `resource_data_lock = asyncio.Lock()` to `SubscriptionManager.__init__()`
- Wrap writes in `_subscription_loop` and reads in `get_resource_data()` with the lock
- Keep the existing `subscription_lock` for subscription lifecycle operations

### 8e — Docker Compose security hardening (`docker-compose.yml`)
**Severity:** MEDIUM
**File:** `docker-compose.yml`
**Issue:** Container runs without restricted capabilities, no read-only filesystem, no `no-new-privileges` flag.
**Fix:**
- Add `security_opt: ["no-new-privileges:true"]`
- Add `cap_drop: ["ALL"]`
- Add `read_only: true` with `tmpfs: ["/tmp"]` for temp files
- Add `mem_limit` and `cpus` resource constraints
- Document that `UNRAID_API_KEY` should use Docker secrets in production

### 8f — Dockerfile healthcheck fix
**Severity:** MEDIUM
**File:** `Dockerfile`
**Issue:** HEALTHCHECK `curl` command may not use `-f` flag to fail on HTTP errors.
**Fix:**
- Ensure healthcheck uses `curl -f` to fail on non-2xx responses
- Verify `--fail-with-body` or `-f` is present

### Verification
1. `uv run pytest tests/unit/ -v` — all tests pass
2. `uv run ruff check unraid_mcp/` — no lint errors
3. `uv run mypy unraid_mcp/` — type checking passes
4. `docker build -t unraid-mcp-server .` — Docker build succeeds

---

## Phase 9: Security Tests & Logging Hardening

> Final pass. Adds security-focused tests and a logging redaction filter for defense-in-depth.

### 9a — Security-focused unit tests
**File:** `tests/unit/test_security.py` (NEW)
**Tests to add:**
- `query_unraid_api` rejects mutations (basic, whitespace, unicode variations)
- `validate_log_file_path` rejects paths outside allowlist (after Phase 6d)
- `_build_ws_url()` rejects malformed URLs (after Phase 6b)
- `_build_ws_auth_payload()` does not appear in any log output
- `_is_container_id()` rejects invalid prefixed IDs (after Phase 7d)
- `validate_rclone_remote_name()` rejects special characters (after Phase 7c)
- `sanitize_query()` strips sensitive variable definitions
- Error messages from `make_graphql_request()` do not contain raw API responses (after Phase 8a)

### 9b — Logging redaction filter
**File:** `config/logging.py`
**Issue:** Even with variable-level redaction, API keys or tokens could appear in exception messages, WebSocket payloads, or raw error strings.
**Fix:**
- Add a `RedactingFilter(logging.Filter)` that regex-replaces patterns matching API keys, Bearer tokens, and common secret formats in log messages
- Apply the filter to all handlers (console, file, FastMCP)
- Patterns: `api[_-]?key\s*[:=]\s*\S+`, `Bearer\s+\S+`, hex strings >32 chars that match known key formats

### 9c — Add `pip-audit` to test suite
**File:** `pyproject.toml` or CI config
**Fix:**
- Add `pip-audit` as a dev dependency if not already present
- Add a test or CI step that runs `pip-audit` and fails on known vulnerabilities

### Verification
1. `uv run pytest tests/unit/ -v` — all tests pass (including new security tests)
2. `uv run ruff check unraid_mcp/ tests/` — no lint errors
3. `uv run mypy unraid_mcp/` — type checking passes
4. `uv run pip-audit` — no known vulnerabilities

---

## Summary

| Phase | Status | Severity | Items |
|-------|--------|----------|-------|
| 1 — Foundation | ✅ | — | 6 |
| 2 — Security & Validation | ✅ | — | 4 |
| 3 — Reliability & Error Handling | ✅ | — | 5 |
| 4 — Performance & Infrastructure | ✅ | — | 5 |
| 5 — Polish & Tests | ✅ | — | 4 |
| 6 — Critical Security Fixes | ⬜ | CRITICAL | 4 |
| 7 — High-Severity Hardening | ⬜ | HIGH | 5 |
| 8 — Medium-Severity Improvements | ⬜ | MEDIUM | 6 |
| 9 — Security Tests & Logging | ⬜ | MEDIUM | 3 |
