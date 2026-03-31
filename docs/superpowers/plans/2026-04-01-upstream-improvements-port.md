# Upstream Improvements Port — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Port 10 security, auth, Docker, CI, and UX improvements from upstream into our fork across 5 phases.

**Architecture:** Each phase is independently shippable. Phase 1 (security) touches only `core/` modules with no architecture changes. Phase 2 adds ASGI middleware for bearer auth via `mcp.http_app().add_middleware()`. Phase 3 replaces the Dockerfile with an entrypoint-chown pattern using `gosu`. Phase 4 adds UX features (guards, log dedup, version). Phase 5 sweeps all docs.

**Tech Stack:** Python 3.11, FastMCP 3.2.0, httpx, Starlette ASGI, gosu, ruff, pytest

**Spec:** `docs/superpowers/specs/2026-04-01-upstream-improvements-port.md`

---

## Phase 1 — Security Hardening

### Task 1: Path Traversal Fix (`_validate_path`)

**Files:**
- Modify: `unraid_mcp/core/validation.py`
- Test: `tests/unit/test_utils_validators.py`

- [ ] **Step 1: Write failing tests for `_validate_path`**

Add to `tests/unit/test_utils_validators.py`:

```python
import pytest
from unraid_mcp.core.validation import validate_path


class TestValidatePath:
    """Tests for posixpath-based path traversal prevention."""

    def test_valid_path(self):
        validate_path("/var/log/syslog", ["/var/log"], "log_path")

    def test_valid_path_nested(self):
        validate_path("/var/log/nginx/access.log", ["/var/log"], "log_path")

    def test_rejects_null_bytes(self):
        with pytest.raises(Exception, match="null byte"):
            validate_path("/var/log/sys\x00log", ["/var/log"], "log_path")

    def test_rejects_traversal_simple(self):
        with pytest.raises(Exception, match="path traversal"):
            validate_path("/var/log/../../etc/shadow", ["/var/log"], "log_path")

    def test_rejects_traversal_encoded(self):
        with pytest.raises(Exception, match="path traversal"):
            validate_path("/var/log/foo/../../../etc/passwd", ["/var/log"], "log_path")

    def test_rejects_outside_prefix(self):
        with pytest.raises(Exception, match="outside allowed"):
            validate_path("/etc/shadow", ["/var/log"], "log_path")

    def test_multiple_prefixes(self):
        validate_path("/boot/config/file.txt", ["/var/log", "/boot/config"], "path")

    def test_normpath_resolves_dot(self):
        validate_path("/var/log/./syslog", ["/var/log"], "log_path")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/unit/test_utils_validators.py::TestValidatePath -v`
Expected: FAIL — `cannot import name 'validate_path'`

- [ ] **Step 3: Implement `validate_path` in `core/validation.py`**

Add at the end of `unraid_mcp/core/validation.py`:

```python
import posixpath


def validate_path(path: str, allowed_prefixes: list[str], param_name: str) -> str:
    """Validate a file path against traversal attacks and allowed prefixes.

    Uses posixpath (not os.path) because paths are remote Linux paths,
    even when this code runs on macOS/Windows dev machines.

    Returns the normalized path.
    """
    if "\x00" in path:
        raise ValidationError(f"{param_name}: null byte in path")

    normalized = posixpath.normpath(path)

    # Check for traversal components after normalization
    parts = normalized.split("/")
    if ".." in parts:
        raise ValidationError(f"{param_name}: path traversal detected")

    # Validate against allowed prefixes
    if not any(normalized.startswith(prefix) for prefix in allowed_prefixes):
        raise ValidationError(
            f"{param_name}: path outside allowed directories"
        )

    return normalized
```

Move the `import posixpath` to the top of the file alongside other imports.

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/unit/test_utils_validators.py::TestValidatePath -v`
Expected: All 8 PASS

- [ ] **Step 5: Refactor `validate_log_file_path` to use `validate_path`**

In `unraid_mcp/core/validation.py`, replace the body of `validate_log_file_path()` (lines 71-85) with:

```python
def validate_log_file_path(path: str) -> str:
    """Validate log file path — delegates to validate_path with log prefixes."""
    from .constants import ALLOWED_LOG_PREFIXES

    return validate_path(path, list(ALLOWED_LOG_PREFIXES), "log_file_path")
```

- [ ] **Step 6: Run full test suite to verify no regressions**

Run: `uv run pytest tests/unit tests/contract -x -q`
Expected: 521 passed

- [ ] **Step 7: Commit**

```bash
git add unraid_mcp/core/validation.py tests/unit/test_utils_validators.py
git commit -m "feat: add posixpath-based path traversal prevention

Adds validate_path() using posixpath.normpath, null-byte rejection,
and prefix validation. Refactors validate_log_file_path to delegate.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: Dangerous Key Pattern + MAX_VALUE_LENGTH

**Files:**
- Modify: `unraid_mcp/core/validation.py`
- Test: `tests/unit/test_utils_validators.py`

- [ ] **Step 1: Write failing tests**

Add to `tests/unit/test_utils_validators.py`:

```python
import re
from unraid_mcp.core.validation import DANGEROUS_KEY_PATTERN, MAX_VALUE_LENGTH


class TestDangerousKeyPattern:
    """Tests for injection-preventing key pattern."""

    def test_rejects_path_traversal(self):
        assert DANGEROUS_KEY_PATTERN.search("..")

    def test_rejects_forward_slash(self):
        assert DANGEROUS_KEY_PATTERN.search("foo/bar")

    def test_rejects_backslash(self):
        assert DANGEROUS_KEY_PATTERN.search("foo\\bar")

    def test_rejects_shell_pipe(self):
        assert DANGEROUS_KEY_PATTERN.search("foo|bar")

    def test_rejects_semicolon(self):
        assert DANGEROUS_KEY_PATTERN.search("foo;bar")

    def test_rejects_dollar(self):
        assert DANGEROUS_KEY_PATTERN.search("foo$bar")

    def test_rejects_backtick(self):
        assert DANGEROUS_KEY_PATTERN.search("foo`bar")

    def test_rejects_null_byte(self):
        assert DANGEROUS_KEY_PATTERN.search("foo\x00bar")

    def test_rejects_control_char(self):
        assert DANGEROUS_KEY_PATTERN.search("foo\x01bar")

    def test_rejects_space(self):
        assert DANGEROUS_KEY_PATTERN.search("foo bar")

    def test_allows_clean_key(self):
        assert not DANGEROUS_KEY_PATTERN.search("my_remote_name")

    def test_allows_hyphen_underscore(self):
        assert not DANGEROUS_KEY_PATTERN.search("my-remote_name-123")

    def test_max_value_length(self):
        assert MAX_VALUE_LENGTH == 4096
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/unit/test_utils_validators.py::TestDangerousKeyPattern -v`
Expected: FAIL — `cannot import name 'DANGEROUS_KEY_PATTERN'`

- [ ] **Step 3: Add constants to `core/validation.py`**

Add near the top of `unraid_mcp/core/validation.py`, after imports:

```python
import re

# Maximum length for user-supplied values (prevents resource exhaustion)
MAX_VALUE_LENGTH = 4096

# Rejects path traversal, shell metacharacters, HTML/XML chars, control chars.
# Use .search() — matches if ANY dangerous character is present.
DANGEROUS_KEY_PATTERN = re.compile(
    r"\.\."           # path traversal
    r"|[/\\]"         # path separators
    r"|[|;$`]"        # shell metacharacters
    r"|[&<>\"'#]"     # HTML/XML injection chars
    r"|[\x00-\x1f]"   # control characters (includes null)
    r"|[\x7f]"         # DEL
    r"|[ ]"            # space
)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/unit/test_utils_validators.py::TestDangerousKeyPattern -v`
Expected: All 13 PASS

- [ ] **Step 5: Apply `DANGEROUS_KEY_PATTERN` in `validate_rclone_remote_name`**

In `unraid_mcp/core/validation.py`, update `validate_rclone_remote_name()` to add a check after the existing regex:

```python
def validate_rclone_remote_name(name: str) -> str:
    """Validate an RClone remote name."""
    validate_string_not_empty(name, "remote_name")
    if len(name) > 64:
        raise ValidationError("Remote name must be 64 characters or fewer")
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9_-]*$", name):
        raise ValidationError(
            "Remote name must start with a letter and contain only "
            "alphanumeric characters, hyphens, and underscores"
        )
    if DANGEROUS_KEY_PATTERN.search(name):
        raise ValidationError("Remote name contains disallowed characters")
    return name
```

- [ ] **Step 6: Run full test suite**

Run: `uv run pytest tests/unit tests/contract -x -q`
Expected: All pass (existing rclone tests should still pass — clean names are unaffected)

- [ ] **Step 7: Commit**

```bash
git add unraid_mcp/core/validation.py tests/unit/test_utils_validators.py
git commit -m "feat: add DANGEROUS_KEY_PATTERN and MAX_VALUE_LENGTH constants

Rejects shell metacharacters, path traversal, control chars, and
HTML/XML injection chars in user-supplied key names.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: `tool_error_handler` Context Manager

**Files:**
- Modify: `unraid_mcp/core/exceptions.py`
- Test: `tests/unit/test_exceptions.py`

- [ ] **Step 1: Write failing tests**

Add to `tests/unit/test_exceptions.py`:

```python
import logging
import pytest
from unraid_mcp.core.exceptions import ToolError, tool_error_handler


class TestToolErrorHandler:
    """Tests for the tool_error_handler context manager."""

    def test_tool_error_passes_through(self):
        with pytest.raises(ToolError, match="custom error"):
            with tool_error_handler("test_tool", "test_action", logging.getLogger()):
                raise ToolError("custom error")

    def test_timeout_gets_descriptive_message(self):
        with pytest.raises(ToolError, match="timed out"):
            with tool_error_handler("my_tool", "fetch_data", logging.getLogger()):
                raise TimeoutError("connection timed out")

    def test_generic_exception_is_sanitized(self):
        with pytest.raises(ToolError, match="failed.*check server logs"):
            with tool_error_handler("my_tool", "query", logging.getLogger()):
                raise RuntimeError("internal details that should not leak")

    def test_generic_exception_logs_full_traceback(self, caplog):
        with caplog.at_level(logging.ERROR):
            with pytest.raises(ToolError):
                with tool_error_handler("my_tool", "query", logging.getLogger()):
                    raise RuntimeError("secret internal error")
        assert "secret internal error" in caplog.text

    def test_no_exception_passes_through(self):
        with tool_error_handler("test_tool", "test_action", logging.getLogger()):
            pass  # No exception — should not raise
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/unit/test_exceptions.py::TestToolErrorHandler -v`
Expected: FAIL — `cannot import name 'tool_error_handler'`

- [ ] **Step 3: Implement `tool_error_handler`**

Add to the end of `unraid_mcp/core/exceptions.py`:

```python
from contextlib import contextmanager
from logging import Logger


@contextmanager
def tool_error_handler(tool_name: str, action: str, logger: Logger):
    """Context manager that catches exceptions and converts to ToolError.

    - ToolError: re-raised as-is (already user-facing)
    - TimeoutError: wrapped with descriptive timeout message
    - All others: logged with full traceback, raised as sanitized ToolError
    """
    try:
        yield
    except ToolError:
        raise
    except TimeoutError:
        raise ToolError(
            f"{tool_name}: {action} timed out — the Unraid server may be under heavy load"
        )
    except Exception as e:
        logger.error(f"{tool_name}: {action} failed: {e}", exc_info=True)
        raise ToolError(
            f"{tool_name}: {action} failed — check server logs for details"
        ) from e
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/unit/test_exceptions.py::TestToolErrorHandler -v`
Expected: All 5 PASS

- [ ] **Step 5: Commit**

```bash
git add unraid_mcp/core/exceptions.py tests/unit/test_exceptions.py
git commit -m "feat: add tool_error_handler context manager

Sanitizes user-facing errors, wraps TimeoutError with descriptive
message, logs full traceback for debugging.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

### Task 4: `safe_display_url()`

**Files:**
- Modify: `unraid_mcp/core/utils.py`
- Modify: `unraid_mcp/config/settings.py`
- Test: `tests/unit/test_utils.py`

- [ ] **Step 1: Write failing tests**

Add to `tests/unit/test_utils.py`:

```python
from unraid_mcp.core.utils import safe_display_url


class TestSafeDisplayUrl:
    """Tests for URL redaction (CWE-200 mitigation)."""

    def test_strips_path(self):
        assert safe_display_url("https://192.168.1.101:8443/graphql") == "https://192.168.1.101:8443"

    def test_strips_query(self):
        assert safe_display_url("https://host:443/path?key=secret") == "https://host:443"

    def test_strips_credentials(self):
        assert safe_display_url("https://user:pass@host:443/path") == "https://host:443"

    def test_preserves_scheme_and_host(self):
        assert safe_display_url("http://myserver:6970") == "http://myserver:6970"

    def test_no_port(self):
        assert safe_display_url("https://myserver/graphql") == "https://myserver"

    def test_invalid_url_returns_placeholder(self):
        assert safe_display_url("not a url at all") == "<invalid-url>"

    def test_empty_string(self):
        assert safe_display_url("") == "<invalid-url>"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/unit/test_utils.py::TestSafeDisplayUrl -v`
Expected: FAIL — `cannot import name 'safe_display_url'`

- [ ] **Step 3: Implement `safe_display_url`**

Add to `unraid_mcp/core/utils.py`:

```python
from urllib.parse import urlparse


def safe_display_url(url: str) -> str:
    """Redact URL to scheme://host:port only (CWE-200 mitigation).

    Strips path, query, fragment, and embedded credentials.
    """
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.hostname:
            return "<invalid-url>"
        port_suffix = f":{parsed.port}" if parsed.port else ""
        return f"{parsed.scheme}://{parsed.hostname}{port_suffix}"
    except Exception:
        return "<invalid-url>"
```

Add `safe_display_url` to the `__all__` list.

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/unit/test_utils.py::TestSafeDisplayUrl -v`
Expected: All 7 PASS

- [ ] **Step 5: Apply `safe_display_url` in settings.py startup logging**

In `unraid_mcp/config/settings.py`, the startup URL is logged at line ~33 (`UNRAID_API_URL`). This is module-level code that runs at import time, so we can't easily call `safe_display_url` there (it would create a circular import). Instead, apply it in `server.py` where the URL is logged at line ~143:

In `unraid_mcp/server.py`, change the URL logging (around line 143):

```python
from .core.utils import safe_display_url

# In run_server():
    if UNRAID_API_URL:
        logger.info(f"UNRAID_API_URL loaded: {safe_display_url(UNRAID_API_URL)}")
```

This replaces the current `UNRAID_API_URL[:20]...` truncation with proper redaction.

- [ ] **Step 6: Run full test suite**

Run: `uv run pytest tests/unit tests/contract -x -q`
Expected: All pass

- [ ] **Step 7: Lint check**

Run: `uv run ruff check unraid_mcp/`
Expected: All checks passed

- [ ] **Step 8: Commit**

```bash
git add unraid_mcp/core/utils.py unraid_mcp/server.py tests/unit/test_utils.py
git commit -m "feat: add safe_display_url for log redaction (CWE-200)

Strips path, query, credentials from URLs before logging.
Applied in server.py startup logging.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

### Task 5: Phase 1 quality gate

- [ ] **Step 1: Run full quality gates**

```bash
uv run ruff check unraid_mcp/
uv run mypy unraid_mcp/
uv run pytest tests/unit tests/contract -x -q
```

Expected: All pass

- [ ] **Step 2: `/commit-and-push`**

Invoke the commit-and-push skill. This runs CodeRabbit, lint, test, commit, push, and monitors CI.

---

## Phase 2 — HTTP Bearer Token Auth + Healthcheck

### Task 6: Add `UNRAID_MCP_AUTH_TOKEN` to settings

**Files:**
- Modify: `unraid_mcp/config/settings.py`
- Modify: `.env.example`
- Test: `tests/unit/test_settings_validation.py`

- [ ] **Step 1: Write failing test**

Add to `tests/unit/test_settings_validation.py`:

```python
import os
import importlib


def test_auth_token_loaded_from_env(monkeypatch):
    """MCP_AUTH_TOKEN should be read from UNRAID_MCP_AUTH_TOKEN env var."""
    monkeypatch.setenv("UNRAID_MCP_AUTH_TOKEN", "test-secret-token")
    monkeypatch.setenv("UNRAID_API_URL", "https://fake:8443/graphql")
    monkeypatch.setenv("UNRAID_API_KEY", "fake-key")
    import unraid_mcp.config.settings as settings_mod
    importlib.reload(settings_mod)
    assert settings_mod.MCP_AUTH_TOKEN == "test-secret-token"


def test_auth_token_empty_when_unset(monkeypatch):
    """MCP_AUTH_TOKEN should be empty string when env var is not set."""
    monkeypatch.delenv("UNRAID_MCP_AUTH_TOKEN", raising=False)
    monkeypatch.setenv("UNRAID_API_URL", "https://fake:8443/graphql")
    monkeypatch.setenv("UNRAID_API_KEY", "fake-key")
    import unraid_mcp.config.settings as settings_mod
    importlib.reload(settings_mod)
    assert settings_mod.MCP_AUTH_TOKEN == ""
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/unit/test_settings_validation.py::test_auth_token_loaded_from_env -v`
Expected: FAIL — `has no attribute 'MCP_AUTH_TOKEN'`

- [ ] **Step 3: Add `MCP_AUTH_TOKEN` to settings.py**

Add at the end of `unraid_mcp/config/settings.py` (after the middleware config section):

```python
# Authentication
MCP_AUTH_TOKEN: str = os.environ.get("UNRAID_MCP_AUTH_TOKEN", "")
```

- [ ] **Step 4: Add to `.env.example`**

Add to `.env.example`:

```bash
# Authentication
# Set a bearer token to require authentication on all HTTP requests.
# If unset or empty, authentication is disabled (WARNING logged on startup).
# UNRAID_MCP_AUTH_TOKEN=your-secret-token-here
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `uv run pytest tests/unit/test_settings_validation.py::test_auth_token_loaded_from_env tests/unit/test_settings_validation.py::test_auth_token_empty_when_unset -v`
Expected: Both PASS

- [ ] **Step 6: Commit**

```bash
git add unraid_mcp/config/settings.py .env.example tests/unit/test_settings_validation.py
git commit -m "feat: add MCP_AUTH_TOKEN setting for bearer auth

Read from UNRAID_MCP_AUTH_TOKEN env var. Empty = auth disabled.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

### Task 7: `HealthMiddleware` and `BearerAuthMiddleware`

**Files:**
- Create: `unraid_mcp/core/auth.py`
- Create: `tests/unit/test_auth_middleware.py`

- [ ] **Step 1: Write failing tests for `HealthMiddleware`**

Create `tests/unit/test_auth_middleware.py`:

```python
import hmac
import json
import pytest
from unittest.mock import AsyncMock


async def _receive():
    return {"type": "http.request", "body": b""}


async def _send_collect(messages: list):
    async def _send(message):
        messages.append(message)
    return _send


class TestHealthMiddleware:
    """Tests for the GET /health endpoint."""

    @pytest.mark.asyncio
    async def test_health_returns_200(self):
        from unraid_mcp.core.auth import HealthMiddleware

        inner_app = AsyncMock()
        app = HealthMiddleware(inner_app)

        scope = {"type": "http", "method": "GET", "path": "/health", "headers": []}
        messages = []
        await app(scope, _receive, await _send_collect(messages))

        response = messages[0]
        assert response["status"] == 200
        body = json.loads(messages[1]["body"])
        assert body["status"] == "ok"
        inner_app.assert_not_called()

    @pytest.mark.asyncio
    async def test_non_health_passes_through(self):
        from unraid_mcp.core.auth import HealthMiddleware

        inner_app = AsyncMock()
        app = HealthMiddleware(inner_app)

        scope = {"type": "http", "method": "POST", "path": "/mcp", "headers": []}
        await app(scope, _receive, AsyncMock())

        inner_app.assert_called_once()

    @pytest.mark.asyncio
    async def test_lifespan_passes_through(self):
        from unraid_mcp.core.auth import HealthMiddleware

        inner_app = AsyncMock()
        app = HealthMiddleware(inner_app)

        scope = {"type": "lifespan"}
        await app(scope, _receive, AsyncMock())

        inner_app.assert_called_once()
```

- [ ] **Step 2: Write failing tests for `BearerAuthMiddleware`**

Add to the same file:

```python
class TestBearerAuthMiddleware:
    """Tests for bearer token authentication."""

    def _make_scope(self, path="/mcp", method="POST", headers=None):
        raw_headers = []
        for k, v in (headers or {}).items():
            raw_headers.append([k.lower().encode(), v.encode()])
        return {
            "type": "http",
            "method": method,
            "path": path,
            "headers": raw_headers,
            "client": ("127.0.0.1", 12345),
        }

    @pytest.mark.asyncio
    async def test_valid_token_passes_through(self):
        from unraid_mcp.core.auth import BearerAuthMiddleware

        inner_app = AsyncMock()
        app = BearerAuthMiddleware(inner_app, token="secret123")

        scope = self._make_scope(headers={"authorization": "Bearer secret123"})
        await app(scope, _receive, AsyncMock())

        inner_app.assert_called_once()

    @pytest.mark.asyncio
    async def test_missing_token_returns_401(self):
        from unraid_mcp.core.auth import BearerAuthMiddleware

        inner_app = AsyncMock()
        app = BearerAuthMiddleware(inner_app, token="secret123")

        scope = self._make_scope()
        messages = []
        await app(scope, _receive, await _send_collect(messages))

        assert messages[0]["status"] == 401
        inner_app.assert_not_called()

    @pytest.mark.asyncio
    async def test_wrong_token_returns_401(self):
        from unraid_mcp.core.auth import BearerAuthMiddleware

        inner_app = AsyncMock()
        app = BearerAuthMiddleware(inner_app, token="secret123")

        scope = self._make_scope(headers={"authorization": "Bearer wrong"})
        messages = []
        await app(scope, _receive, await _send_collect(messages))

        assert messages[0]["status"] == 401
        inner_app.assert_not_called()

    @pytest.mark.asyncio
    async def test_disabled_passes_all_through(self):
        from unraid_mcp.core.auth import BearerAuthMiddleware

        inner_app = AsyncMock()
        app = BearerAuthMiddleware(inner_app, token="", disabled=True)

        scope = self._make_scope()
        await app(scope, _receive, AsyncMock())

        inner_app.assert_called_once()

    @pytest.mark.asyncio
    async def test_lifespan_passes_through(self):
        from unraid_mcp.core.auth import BearerAuthMiddleware

        inner_app = AsyncMock()
        app = BearerAuthMiddleware(inner_app, token="secret123")

        scope = {"type": "lifespan"}
        await app(scope, _receive, AsyncMock())

        inner_app.assert_called_once()

    @pytest.mark.asyncio
    async def test_constant_time_comparison(self):
        """Verify hmac.compare_digest is used (not ==)."""
        from unraid_mcp.core import auth
        import hmac as hmac_mod

        # If the implementation uses hmac.compare_digest, this is a design check.
        # We verify by checking the source references hmac.
        import inspect
        source = inspect.getsource(auth.BearerAuthMiddleware)
        assert "hmac.compare_digest" in source or "compare_digest" in source
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `uv run pytest tests/unit/test_auth_middleware.py -v`
Expected: FAIL — `No module named 'unraid_mcp.core.auth'`

- [ ] **Step 4: Implement `core/auth.py`**

Create `unraid_mcp/core/auth.py`:

```python
"""ASGI middleware for bearer token authentication and health endpoint."""

import hmac
import json
import logging
import time

logger = logging.getLogger(__name__)


class HealthMiddleware:
    """ASGI middleware that responds to GET /health before any auth check.

    Placed outermost so Docker healthchecks work without a bearer token.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and scope.get("method") == "GET" and scope.get("path") == "/health":
            body = json.dumps({"status": "ok"}).encode()
            await send({
                "type": "http.response.start",
                "status": 200,
                "headers": [
                    [b"content-type", b"application/json"],
                    [b"content-length", str(len(body)).encode()],
                ],
            })
            await send({"type": "http.response.body", "body": body})
            return

        await self.app(scope, receive, send)


class BearerAuthMiddleware:
    """ASGI middleware for RFC 6750 bearer token authentication.

    Features:
    - Constant-time token comparison via hmac.compare_digest
    - Per-IP failure rate limiting (max_failures per window)
    - Log throttling (one warning per IP per log_throttle_seconds)
    - Passes through WebSocket upgrades and ASGI lifespan events
    """

    def __init__(
        self,
        app,
        token: str,
        disabled: bool = False,
        max_failures: int = 60,
        window_seconds: int = 60,
        log_throttle_seconds: int = 30,
    ):
        self.app = app
        self.token = token
        self.disabled = disabled
        self.max_failures = max_failures
        self.window_seconds = window_seconds
        self.log_throttle_seconds = log_throttle_seconds
        # Per-IP tracking: {ip: [timestamp, ...]}
        self._failure_counts: dict[str, list[float]] = {}
        # Per-IP log throttle: {ip: last_log_timestamp}
        self._last_log: dict[str, float] = {}

    async def __call__(self, scope, receive, send):
        # Pass through non-HTTP scopes (lifespan, websocket)
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Disabled = pass everything through
        if self.disabled:
            await self.app(scope, receive, send)
            return

        # Extract client IP
        client = scope.get("client", ("unknown", 0))
        client_ip = client[0] if client else "unknown"

        # Check rate limit
        if self._is_rate_limited(client_ip):
            await self._send_error(send, 429, "Too many failed authentication attempts")
            return

        # Extract and validate bearer token
        token = self._extract_token(scope)
        if token is None or not hmac.compare_digest(token.encode(), self.token.encode()):
            self._record_failure(client_ip)
            self._throttled_log(client_ip)
            await self._send_error(
                send, 401, "Invalid or missing bearer token",
                extra_headers=[[b"www-authenticate", b'Bearer realm="unraid-mcp"']],
            )
            return

        await self.app(scope, receive, send)

    def _extract_token(self, scope) -> str | None:
        """Extract bearer token from Authorization header."""
        for key, value in scope.get("headers", []):
            if key == b"authorization":
                decoded = value.decode()
                if decoded.startswith("Bearer "):
                    return decoded[7:]
        return None

    def _is_rate_limited(self, ip: str) -> bool:
        """Check if IP has exceeded failure rate limit."""
        now = time.monotonic()
        attempts = self._failure_counts.get(ip, [])
        # Prune expired entries
        attempts = [t for t in attempts if now - t < self.window_seconds]
        self._failure_counts[ip] = attempts
        return len(attempts) >= self.max_failures

    def _record_failure(self, ip: str) -> None:
        """Record a failed auth attempt for rate limiting."""
        now = time.monotonic()
        if ip not in self._failure_counts:
            self._failure_counts[ip] = []
        self._failure_counts[ip].append(now)

    def _throttled_log(self, ip: str) -> None:
        """Log auth failure, throttled to one warning per IP per interval."""
        now = time.monotonic()
        last = self._last_log.get(ip, 0)
        if now - last >= self.log_throttle_seconds:
            logger.warning(f"Bearer auth failed from {ip}")
            self._last_log[ip] = now

    async def _send_error(self, send, status: int, message: str, extra_headers=None):
        """Send a JSON error response."""
        body = json.dumps({"error": message}).encode()
        headers = [
            [b"content-type", b"application/json"],
            [b"content-length", str(len(body)).encode()],
        ]
        if extra_headers:
            headers.extend(extra_headers)
        await send({
            "type": "http.response.start",
            "status": status,
            "headers": headers,
        })
        await send({"type": "http.response.body", "body": body})
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `uv run pytest tests/unit/test_auth_middleware.py -v`
Expected: All 9 PASS

- [ ] **Step 6: Commit**

```bash
git add unraid_mcp/core/auth.py tests/unit/test_auth_middleware.py
git commit -m "feat: add BearerAuthMiddleware and HealthMiddleware

ASGI middleware with hmac.compare_digest, per-IP rate limiting,
log throttling. HealthMiddleware responds to GET /health before auth.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

### Task 8: Integrate auth middleware into server.py

**Files:**
- Modify: `unraid_mcp/server.py`
- Modify: `unraid_mcp/config/settings.py` (add import to server)

- [ ] **Step 1: Investigate FastMCP 3.x ASGI app wrapping**

Run this to confirm the integration approach:

```bash
uv run python3 -c "
from fastmcp import FastMCP
m = FastMCP('test')
app = m.http_app()
print(type(app))
print(hasattr(app, 'add_middleware'))
"
```

Expected: `StarletteWithLifespan`, `True`

- [ ] **Step 2: Modify `run_server()` in server.py**

In `unraid_mcp/server.py`, add imports at the top:

```python
from .core.auth import BearerAuthMiddleware, HealthMiddleware
from .core.utils import safe_display_url
```

And add `MCP_AUTH_TOKEN` to the settings import.

Then modify the `run_server()` function. Before the transport-specific `mcp.run()` calls, add ASGI middleware setup for the `streamable-http` transport. The key insight: instead of calling `mcp.run()` which starts uvicorn internally, we get the app, wrap it, and run uvicorn ourselves for `streamable-http`. For `sse` and `stdio`, ASGI middleware doesn't apply.

```python
def run_server() -> None:
    """Run the MCP server with the configured transport."""
    # Log configuration
    if UNRAID_API_URL:
        logger.info(f"UNRAID_API_URL loaded: {safe_display_url(UNRAID_API_URL)}")
    else:
        logger.warning("UNRAID_API_URL not found in environment or .env file.")

    if UNRAID_API_KEY:
        logger.info("UNRAID_API_KEY loaded: ****")
    else:
        logger.warning("UNRAID_API_KEY not found in environment or .env file.")

    if MCP_AUTH_TOKEN:
        logger.info("Bearer auth enabled")
    else:
        logger.warning(
            "UNRAID_MCP_AUTH_TOKEN not set — HTTP auth disabled. "
            "Set this variable to require bearer token authentication."
        )

    logger.info(f"UNRAID_MCP_PORT set to: {UNRAID_MCP_PORT}")
    logger.info(f"UNRAID_MCP_HOST set to: {UNRAID_MCP_HOST}")
    logger.info(f"UNRAID_MCP_TRANSPORT set to: {UNRAID_MCP_TRANSPORT}")

    # Register all modules
    register_all_modules()

    logger.info(
        f"Starting Unraid MCP Server on {UNRAID_MCP_HOST}:{UNRAID_MCP_PORT} "
        f"using {UNRAID_MCP_TRANSPORT} transport..."
    )

    try:
        if UNRAID_MCP_TRANSPORT == "streamable-http":
            import uvicorn
            app = mcp.http_app(
                transport="streamable-http",
                path="/mcp",
            )
            # Wrap with ASGI middleware (outermost added last)
            app = BearerAuthMiddleware(
                app,
                token=MCP_AUTH_TOKEN,
                disabled=not MCP_AUTH_TOKEN,
            )
            app = HealthMiddleware(app)
            uvicorn.run(
                app,
                host=UNRAID_MCP_HOST,
                port=UNRAID_MCP_PORT,
            )
        elif UNRAID_MCP_TRANSPORT == "sse":
            logger.warning(
                "SSE transport is deprecated. Bearer auth is not available on SSE. "
                "Consider switching to 'streamable-http'."
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
                f"Unsupported MCP_TRANSPORT: {UNRAID_MCP_TRANSPORT}. "
                "Choose 'streamable-http' (recommended), 'sse' (deprecated), or 'stdio'."
            )
            sys.exit(1)
    except Exception as e:
        logger.critical(f"Failed to start Unraid MCP server: {e}", exc_info=True)
        sys.exit(1)
```

Note: This changes the `streamable-http` path from `mcp.run()` to `mcp.http_app()` + `uvicorn.run()`. The `http_app()` method returns the Starlette app without starting uvicorn, allowing us to wrap it with ASGI middleware first. Verify during implementation that `mcp.http_app()` accepts `transport` and `path` params — if not, adjust the call signature based on the FastMCP 3.x API.

- [ ] **Step 3: Run full test suite**

Run: `uv run pytest tests/unit tests/contract -x -q`
Expected: All pass (server.py isn't directly tested by unit tests — it's integration-level)

- [ ] **Step 4: Test locally with auth disabled**

```bash
uv run unraid-mcp-server &
sleep 3
curl -sf http://localhost:6970/health
curl -sf -X POST -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"test","version":"1.0.0"}}}' http://localhost:6970/mcp
kill %1
```

Expected: Health returns `{"status": "ok"}`, MCP initialize works (no auth required when token unset).

- [ ] **Step 5: Test locally with auth enabled**

```bash
UNRAID_MCP_AUTH_TOKEN=test123 uv run unraid-mcp-server &
sleep 3
# Health should work without token
curl -sf http://localhost:6970/health
# MCP without token should fail
curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:6970/mcp
# MCP with correct token should work
curl -sf -X POST -H "Authorization: Bearer test123" -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"test","version":"1.0.0"}}}' http://localhost:6970/mcp
kill %1
```

Expected: Health 200, unauthenticated 401, authenticated 200.

- [ ] **Step 6: Commit**

```bash
git add unraid_mcp/server.py
git commit -m "feat: integrate bearer auth and health middleware into server

streamable-http now uses mcp.http_app() + uvicorn.run() to allow
ASGI middleware wrapping. Auth disabled when token is empty.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

### Task 9: Update Dockerfile healthcheck + config surfaces

**Files:**
- Modify: `Dockerfile`
- Modify: `unraid-mcp.xml`
- Modify: `docker-compose.yml`

- [ ] **Step 1: Update Dockerfile healthcheck**

In `Dockerfile`, replace the existing HEALTHCHECK (lines 39-43) with:

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -sf http://localhost:${UNRAID_MCP_PORT:-6970}/health || exit 1
```

- [ ] **Step 2: Add auth token to docker-compose.yml**

In `docker-compose.yml`, add to the environment section:

```yaml
      # Authentication (optional — if unset, HTTP auth is disabled)
      - UNRAID_MCP_AUTH_TOKEN=${UNRAID_MCP_AUTH_TOKEN:-}
```

- [ ] **Step 3: Add auth token to XML template**

In `unraid-mcp.xml`, add before the closing `</Container>`:

```xml
  <Config Name="Auth Token" Target="UNRAID_MCP_AUTH_TOKEN" Default="" Mode="" Description="Bearer token for HTTP authentication. If empty, authentication is disabled. Set a strong random token to secure the MCP endpoint." Type="Variable" Display="advanced" Required="false" Mask="true"/>
```

- [ ] **Step 4: Commit**

```bash
git add Dockerfile unraid-mcp.xml docker-compose.yml
git commit -m "feat: update healthcheck to GET /health, add auth token config

Simpler curl healthcheck replaces JSON-RPC POST. Auth token added
to docker-compose, XML template, and .env.example.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

### Task 10: Phase 2 quality gate

- [ ] **Step 1: Run full quality gates**

```bash
uv run ruff check unraid_mcp/
uv run mypy unraid_mcp/
uv run pytest tests/unit tests/contract -x -q
```

- [ ] **Step 2: `/commit-and-push`**

---

## Phase 3 — Dockerfile + CI Modernization

### Task 11: Entrypoint-chown Dockerfile

**Files:**
- Create: `entrypoint.sh`
- Modify: `Dockerfile`
- Modify: `docker-compose.yml`

- [ ] **Step 1: Create `entrypoint.sh`**

Create `entrypoint.sh` in the project root:

```bash
#!/bin/sh
set -e

# Fix ownership of bind-mounted directories.
# On Unraid, the Docker UI creates these as nobody:users (99:100) with 755.
# The mcp user (1000:1000) needs write access.
chown -R mcp:mcp /app/logs 2>/dev/null || true

# Drop to non-root user and exec the CMD
exec gosu mcp "$@"
```

Make it executable: `chmod +x entrypoint.sh`

- [ ] **Step 2: Rewrite Dockerfile**

Replace the entire `Dockerfile` with:

```dockerfile
# Stage 1: Builder
FROM python:3.11-slim AS builder
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:0.5.24 /uv /uvx /bin/
COPY pyproject.toml uv.lock README.md ./
COPY unraid_mcp/ ./unraid_mcp/
RUN uv sync --frozen --no-dev

# Stage 2: Runtime
FROM python:3.11-slim

# hadolint ignore=DL3008
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl gosu \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -g 1000 mcp && useradd -u 1000 -g mcp -m mcp

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.5.24 /uv /uvx /bin/
COPY --from=builder /app /app
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

RUN mkdir -p /app/logs && chown -R mcp:mcp /app/logs

EXPOSE 6970

ENV PYTHONUNBUFFERED=1
ENV UNRAID_MCP_PORT=6970
ENV UNRAID_MCP_HOST="0.0.0.0"
ENV UNRAID_MCP_TRANSPORT="streamable-http"
ENV UNRAID_API_URL=""
ENV UNRAID_VERIFY_SSL="true"
ENV UNRAID_MCP_LOG_LEVEL="INFO"
ENV UNRAID_MCP_LOG_DIR="/app/logs"
ENV UNRAID_MCP_LOG_FORMAT="text"

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -sf http://localhost:${UNRAID_MCP_PORT:-6970}/health || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["uv", "run", "unraid-mcp-server"]
```

- [ ] **Step 3: Update docker-compose.yml security settings**

In `docker-compose.yml`, replace `cap_drop: [ALL]` with a comment explaining why it's removed:

```yaml
    security_opt:
      - no-new-privileges:true
    # Note: cap_drop ALL is NOT used because the entrypoint needs root
    # briefly to chown bind-mounted directories before dropping to the
    # mcp user via gosu. no-new-privileges prevents re-escalation.
```

Remove the `cap_drop` section entirely.

- [ ] **Step 4: Commit**

```bash
git add entrypoint.sh Dockerfile docker-compose.yml
git commit -m "feat: entrypoint-chown pattern for non-root container

Starts as root, chowns bind-mounted dirs, drops to mcp user (1000)
via gosu. Removes cap_drop ALL (incompatible with entrypoint chown).

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

### Task 12: CI — `ruff format` and `uv audit`

**Files:**
- Modify: `.github/workflows/ci.yml`
- Modify: `pyproject.toml` (remove black from dev deps)

- [ ] **Step 1: Add `ruff format --check` to CI lint job**

In `.github/workflows/ci.yml`, find the lint job's run step. Add `uv run ruff format --check unraid_mcp/ tests/` after the existing `ruff check` command.

- [ ] **Step 2: Replace `black` with `ruff format` in lint job**

Remove the `uv run black --check` step if present. Remove `black` from `pyproject.toml` dev dependencies.

- [ ] **Step 3: Add `uv audit` job to CI**

Add a new job to `.github/workflows/ci.yml`:

```yaml
  dependency-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
        with:
          version: "0.5.24"
      - run: uv sync --frozen
      - run: uv run pip audit
```

Note: Check whether `uv audit` exists in uv 0.5.24. If not, use `uv run pip audit` (pip-audit is already a dev dependency). Adjust during implementation.

- [ ] **Step 4: Run `ruff format --check` locally to verify**

```bash
uv run ruff format --check unraid_mcp/ tests/
```

If it fails, run `uv run ruff format unraid_mcp/ tests/` to fix, then re-check.

- [ ] **Step 5: Commit**

```bash
git add .github/workflows/ci.yml pyproject.toml
git commit -m "chore: add ruff format check and dependency audit to CI

Replaces black with ruff format. Adds pip-audit job for dependency
security scanning.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

### Task 13: Phase 3 quality gate

- [ ] **Step 1: Run full quality gates**

```bash
uv run ruff check unraid_mcp/
uv run ruff format --check unraid_mcp/ tests/
uv run mypy unraid_mcp/
uv run pytest tests/unit tests/contract -x -q
```

- [ ] **Step 2: `/commit-and-push`**

---

## Phase 4 — UX Improvements

### Task 14: Destructive Action Gating

**Files:**
- Create: `unraid_mcp/core/guards.py`
- Create: `tests/unit/test_guards.py`
- Modify: `unraid_mcp/tools/docker.py`

- [ ] **Step 1: Write failing tests**

Create `tests/unit/test_guards.py`:

```python
import pytest
from unittest.mock import AsyncMock, MagicMock
from unraid_mcp.core.exceptions import ToolError


class TestGateDestructiveAction:
    """Tests for destructive action confirmation gating."""

    @pytest.mark.asyncio
    async def test_non_destructive_action_passes(self):
        from unraid_mcp.core.guards import gate_destructive_action

        # "start" is not in the destructive set — should pass
        await gate_destructive_action(
            ctx=None,
            action="start",
            destructive_actions={"stop", "kill"},
            confirm=False,
        )

    @pytest.mark.asyncio
    async def test_destructive_with_confirm_passes(self):
        from unraid_mcp.core.guards import gate_destructive_action

        await gate_destructive_action(
            ctx=None,
            action="stop",
            destructive_actions={"stop", "kill"},
            confirm=True,
        )

    @pytest.mark.asyncio
    async def test_destructive_without_confirm_raises(self):
        from unraid_mcp.core.guards import gate_destructive_action

        with pytest.raises(ToolError, match="requires confirm=True"):
            await gate_destructive_action(
                ctx=None,
                action="stop",
                destructive_actions={"stop", "kill"},
                confirm=False,
            )

    @pytest.mark.asyncio
    async def test_destructive_with_description(self):
        from unraid_mcp.core.guards import gate_destructive_action

        with pytest.raises(ToolError, match="requires confirm=True"):
            await gate_destructive_action(
                ctx=None,
                action="kill",
                destructive_actions={"stop", "kill"},
                confirm=False,
                description="Force-kill the container",
            )
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/unit/test_guards.py -v`
Expected: FAIL — `No module named 'unraid_mcp.core.guards'`

- [ ] **Step 3: Implement `core/guards.py`**

Create `unraid_mcp/core/guards.py`:

```python
"""Destructive action confirmation gating.

Uses MCP elicitation when available, falls back to requiring confirm=True.
"""

import logging

from .exceptions import ToolError

logger = logging.getLogger(__name__)


async def gate_destructive_action(
    ctx,
    action: str,
    destructive_actions: set[str],
    confirm: bool,
    description: str | None = None,
) -> None:
    """Gate a destructive action behind user confirmation.

    Args:
        ctx: MCP context (may be None in tests or non-interactive flows).
        action: The action being performed (e.g., "stop", "kill").
        destructive_actions: Set of action names that require confirmation.
        confirm: Whether the caller explicitly confirmed the action.
        description: Optional human-readable description of the action.
    """
    if action not in destructive_actions:
        return

    if confirm:
        return

    # TODO: When MCP elicitation is widely supported, add ctx.elicit() path here.
    # For now, require confirm=True as the only confirmation mechanism.

    desc = f" ({description})" if description else ""
    raise ToolError(
        f"Action '{action}'{desc} is destructive and requires confirm=True. "
        f"Pass confirm=True to proceed."
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/unit/test_guards.py -v`
Expected: All 4 PASS

- [ ] **Step 5: Add `confirm` parameter to `manage_docker_container`**

In `unraid_mcp/tools/docker.py`, find the `manage_docker_container` function definition (around line 139). Add `confirm: bool = False` parameter and call `gate_destructive_action` at the start of the function body:

```python
from unraid_mcp.core.guards import gate_destructive_action

# Inside manage_docker_container, after parameter validation:
    await gate_destructive_action(
        ctx=None,  # ctx not available in current tool signature
        action=action,
        destructive_actions={"stop", "restart", "kill"},
        confirm=confirm,
    )
```

Note: The exact integration depends on how the function receives MCP context. If the tool function signature includes a `ctx` parameter from FastMCP, pass it. Otherwise pass `None` (falls back to confirm=True requirement). Investigate during implementation.

- [ ] **Step 6: Run full test suite**

Run: `uv run pytest tests/unit tests/contract -x -q`
Expected: All pass (existing docker tests don't use destructive actions, or use them with mocked GraphQL)

- [ ] **Step 7: Commit**

```bash
git add unraid_mcp/core/guards.py tests/unit/test_guards.py unraid_mcp/tools/docker.py
git commit -m "feat: add destructive action gating with confirm parameter

Requires confirm=True for stop/restart/kill actions on docker
containers. Will support MCP elicitation when widely available.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

### Task 15: Subscription Error Dedup

**Files:**
- Modify: `unraid_mcp/subscriptions/manager.py`
- Test: `tests/unit/test_subscription_manager.py`

- [ ] **Step 1: Write failing tests**

Add to `tests/unit/test_subscription_manager.py`:

```python
class TestGraphQLErrorDedup:
    """Tests for repeated GraphQL error log deduplication."""

    def test_first_error_logs_warning(self, caplog):
        """First occurrence of a GraphQL error should log at WARNING."""
        manager = SubscriptionManager()
        with caplog.at_level(logging.WARNING):
            manager._handle_graphql_error("array_state", "some error message")
        assert "some error message" in caplog.text
        assert caplog.records[-1].levelno == logging.WARNING

    def test_repeat_error_logs_debug(self, caplog):
        """Repeated identical errors should downgrade to DEBUG."""
        manager = SubscriptionManager()
        manager._handle_graphql_error("array_state", "same error")
        with caplog.at_level(logging.DEBUG):
            caplog.clear()
            manager._handle_graphql_error("array_state", "same error")
        assert caplog.records[-1].levelno == logging.DEBUG

    def test_different_error_resets_counter(self, caplog):
        """A different error message should reset and log at WARNING."""
        manager = SubscriptionManager()
        manager._handle_graphql_error("array_state", "error A")
        with caplog.at_level(logging.WARNING):
            caplog.clear()
            manager._handle_graphql_error("array_state", "error B")
        assert "error B" in caplog.text
        assert caplog.records[-1].levelno == logging.WARNING

    def test_periodic_reminder_at_10(self, caplog):
        """At count 10, a WARNING reminder should be logged."""
        manager = SubscriptionManager()
        for i in range(10):
            manager._handle_graphql_error("array_state", "repeated error")
        # The 10th occurrence should have triggered a WARNING
        warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
        assert any("10" in r.message for r in warnings)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/unit/test_subscription_manager.py::TestGraphQLErrorDedup -v`
Expected: FAIL — `has no attribute '_handle_graphql_error'`

- [ ] **Step 3: Add dedup tracking to SubscriptionManager**

In `unraid_mcp/subscriptions/manager.py`, add instance variables in `__init__`:

```python
# GraphQL error deduplication
self._last_graphql_error: dict[str, str] = {}
self._graphql_error_count: dict[str, int] = {}
```

Add the `_handle_graphql_error` method:

```python
def _handle_graphql_error(self, sub_name: str, error_msg: str) -> None:
    """Handle a GraphQL error with deduplication.

    First occurrence: WARNING. Repeats: DEBUG.
    Periodic reminders at 10, 100, 1000.
    """
    last = self._last_graphql_error.get(sub_name)
    if last == error_msg:
        self._graphql_error_count[sub_name] = self._graphql_error_count.get(sub_name, 1) + 1
        count = self._graphql_error_count[sub_name]
        if count in (10, 100, 1000):
            logger.warning(
                f"[{sub_name}] GraphQL error repeated {count} times: {error_msg}"
            )
        else:
            logger.debug(f"[{sub_name}] GraphQL error (repeat #{count}): {error_msg}")
    else:
        self._last_graphql_error[sub_name] = error_msg
        self._graphql_error_count[sub_name] = 1
        logger.warning(f"[{sub_name}] GraphQL error: {error_msg}")
```

Then in `_process_ws_message`, where GraphQL errors are currently logged at ERROR level, replace with a call to `self._handle_graphql_error(sub_name, error_message)`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/unit/test_subscription_manager.py::TestGraphQLErrorDedup -v`
Expected: All 4 PASS

- [ ] **Step 5: Commit**

```bash
git add unraid_mcp/subscriptions/manager.py tests/unit/test_subscription_manager.py
git commit -m "feat: deduplicate repeated GraphQL subscription errors

First occurrence logs WARNING, repeats downgrade to DEBUG.
Periodic reminders at 10/100/1000 occurrences.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

### Task 16: `version.py`

**Files:**
- Create: `unraid_mcp/version.py`
- Modify: `unraid_mcp/__init__.py`
- Modify: `unraid_mcp/server.py`
- Test: `tests/unit/test_utils.py`

- [ ] **Step 1: Write failing test**

Add to `tests/unit/test_utils.py`:

```python
def test_version_is_string():
    from unraid_mcp.version import VERSION
    assert isinstance(VERSION, str)
    assert VERSION != ""


def test_version_matches_init():
    from unraid_mcp import __version__
    from unraid_mcp.version import VERSION
    assert __version__ == VERSION
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/unit/test_utils.py::test_version_is_string -v`
Expected: FAIL — `No module named 'unraid_mcp.version'`

- [ ] **Step 3: Create `version.py`**

Create `unraid_mcp/version.py`:

```python
"""Single source of truth for package version."""

from importlib.metadata import PackageNotFoundError, version

try:
    VERSION = version("unraid-mcp")
except PackageNotFoundError:
    VERSION = "0.0.0"
```

- [ ] **Step 4: Update `__init__.py`**

Replace the contents of `unraid_mcp/__init__.py`:

```python
"""Unraid MCP Server — MCP tools for Unraid via GraphQL."""

from .version import VERSION

__version__ = VERSION
```

- [ ] **Step 5: Update `server.py` import**

In `unraid_mcp/server.py`, change:

```python
from . import __version__
```

to:

```python
from .version import VERSION as __version__
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `uv run pytest tests/unit/test_utils.py::test_version_is_string tests/unit/test_utils.py::test_version_matches_init -v`
Expected: Both PASS

- [ ] **Step 7: Commit**

```bash
git add unraid_mcp/version.py unraid_mcp/__init__.py unraid_mcp/server.py tests/unit/test_utils.py
git commit -m "feat: add version.py using importlib.metadata

Single source of truth from pyproject.toml. Falls back to 0.0.0.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

### Task 17: Phase 4 quality gate

- [ ] **Step 1: Run full quality gates**

```bash
uv run ruff check unraid_mcp/
uv run mypy unraid_mcp/
uv run pytest tests/unit tests/contract -x -q
```

- [ ] **Step 2: `/commit-and-push`**

---

## Phase 5 — Documentation Sweep

### Task 18: Update all documentation

**Files:**
- Modify: `CLAUDE.md`
- Modify: `README.md`
- Modify: `unraid-mcp.xml`
- Modify: `.env.example`

- [ ] **Step 1: Update CLAUDE.md**

Audit and update the following sections:

1. **Architecture > Core Components**: Add `core/auth.py` (ASGI middleware for bearer auth and health endpoint) and `core/guards.py` (destructive action gating)
2. **Architecture > Key Design Patterns**: Add "ASGI Middleware" pattern — HealthMiddleware and BearerAuthMiddleware wrap the HTTP layer outside FastMCP's protocol middleware
3. **Tool Categories**: Verify the 32-tool count and 8-category structure is still accurate
4. **Sprint Learnings & Gotchas**:
   - Update the `cap_drop ALL` gotcha: explain the entrypoint-chown pattern makes `cap_drop ALL` incompatible in BOTH compose and XML template (not just XML). Use `no-new-privileges` only.
   - Add gotcha: "Entrypoint needs root for chown — `cap_drop ALL` drops `DAC_OVERRIDE` at container start, preventing the entrypoint from fixing bind-mount ownership. Use `security_opt: [no-new-privileges:true]` instead."
   - Add gotcha: "ASGI vs FastMCP middleware — HealthMiddleware and BearerAuthMiddleware are pure ASGI middleware wrapping the Starlette app via `mcp.http_app()`. FastMCP middleware (Logging, RateLimit, etc.) wraps the MCP protocol layer inside. They are configured differently: ASGI middleware via app wrapping, FastMCP middleware via `mcp.add_middleware()`."

- [ ] **Step 2: Update README.md**

1. **Quick Start**: Add `UNRAID_MCP_AUTH_TOKEN` to the `docker run` example
2. **Docker Compose**: Update example to show auth token env var, remove `cap_drop: ALL`
3. **Configuration table**: Add `UNRAID_MCP_AUTH_TOKEN` row
4. **Development section**: Replace `black` with `ruff format` in commands
5. **Test count**: Update to reflect current count after all new tests

- [ ] **Step 3: Update XML template**

Verify `unraid-mcp.xml`:
- Auth token Config element was added in Task 9
- ExtraParams still has `--security-opt no-new-privileges:true` (no cap_drop)
- Overview text is still accurate

- [ ] **Step 4: Update .env.example**

Verify all new env vars are present with comments:
- `UNRAID_MCP_AUTH_TOKEN` (added in Task 6)
- All middleware vars from previous sprint

- [ ] **Step 5: Verify no stale references**

Search for stale patterns:

```bash
grep -r "black" unraid_mcp/ tests/ .github/ --include="*.py" --include="*.yml" --include="*.md" | grep -v ".venv" | grep -v "node_modules"
grep -r "cap_drop" . --include="*.yml" --include="*.xml" --include="*.md" | grep -v ".venv"
grep -r "POST.*initialize.*healthcheck\|healthcheck.*POST" Dockerfile docker-compose.yml
```

Fix any stale references found.

- [ ] **Step 6: Run lint on docs-adjacent files**

```bash
uv run ruff check unraid_mcp/
uv run pytest tests/unit tests/contract -x -q
```

- [ ] **Step 7: Commit**

```bash
git add CLAUDE.md README.md unraid-mcp.xml .env.example
git commit -m "docs: comprehensive documentation sweep for upstream port

Updates architecture, gotchas, config tables, and examples to
reflect bearer auth, entrypoint-chown, ruff format, and guards.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

### Task 19: Final quality gate

- [ ] **Step 1: Full quality gate run**

```bash
uv run ruff check unraid_mcp/
uv run ruff format --check unraid_mcp/ tests/
uv run mypy unraid_mcp/
uv run pytest tests/unit tests/contract -x -q
```

- [ ] **Step 2: `/commit-and-push`**

This is the final push. Monitor all CI workflows until green. The sprint is complete.
