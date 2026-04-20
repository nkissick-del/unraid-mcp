"""Tests for ASGI auth and health middleware."""

import inspect
import json
from unittest.mock import AsyncMock

import pytest


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

        source = inspect.getsource(auth.BearerAuthMiddleware)
        assert "hmac.compare_digest" in source or "compare_digest" in source


class TestWellKnownMiddleware:
    """Tests for the RFC 9728 OAuth Protected Resource Metadata endpoint."""

    @pytest.mark.asyncio
    async def test_well_known_middleware_serves_oauth_discovery(self):
        """GET /.well-known/oauth-protected-resource returns 200 with RFC 9728 body."""
        from unraid_mcp.core.auth import WellKnownMiddleware

        async def inner_app(scope, receive, send):
            raise AssertionError("inner app should not be called")

        mw = WellKnownMiddleware(inner_app)

        messages: list = []

        async def receive():
            return {"type": "http.request"}

        async def send(message):
            messages.append(message)

        scope = {
            "type": "http",
            "method": "GET",
            "path": "/.well-known/oauth-protected-resource",
            "scheme": "http",
            "headers": [(b"host", b"example.test:6970")],
        }

        await mw(scope, receive, send)

        assert messages[0]["type"] == "http.response.start"
        assert messages[0]["status"] == 200
        assert dict(messages[0]["headers"])[b"content-type"] == b"application/json"

        body = json.loads(messages[1]["body"])
        assert body["resource"] == "http://example.test:6970"
        assert body["bearer_methods_supported"] == ["header"]
        assert "authorization_servers" not in body

    @pytest.mark.asyncio
    async def test_well_known_middleware_serves_mcp_variant(self):
        """GET /.well-known/oauth-protected-resource/mcp is also handled."""
        from unraid_mcp.core.auth import WellKnownMiddleware

        async def inner_app(scope, receive, send):
            raise AssertionError("inner app should not be called")

        mw = WellKnownMiddleware(inner_app)
        messages: list = []

        async def receive():
            return {"type": "http.request"}

        async def send(message):
            messages.append(message)

        scope = {
            "type": "http",
            "method": "GET",
            "path": "/.well-known/oauth-protected-resource/mcp",
            "scheme": "http",
            "headers": [(b"host", b"localhost")],
        }
        await mw(scope, receive, send)
        assert messages[0]["status"] == 200

    @pytest.mark.asyncio
    async def test_well_known_middleware_passes_through_other_paths(self):
        """GET /mcp and other paths pass through to inner app."""
        from unraid_mcp.core.auth import WellKnownMiddleware

        called = {"flag": False}

        async def inner_app(scope, receive, send):
            called["flag"] = True

        mw = WellKnownMiddleware(inner_app)
        scope = {
            "type": "http",
            "method": "GET",
            "path": "/mcp",
            "scheme": "http",
            "headers": [(b"host", b"localhost")],
        }

        async def receive():
            return {"type": "http.request"}

        async def send(message):
            pass

        await mw(scope, receive, send)
        assert called["flag"] is True

    @pytest.mark.asyncio
    async def test_well_known_middleware_rejects_non_get(self):
        """POST /.well-known/oauth-protected-resource passes through (only GET is handled)."""
        from unraid_mcp.core.auth import WellKnownMiddleware

        called = {"flag": False}

        async def inner_app(scope, receive, send):
            called["flag"] = True

        mw = WellKnownMiddleware(inner_app)
        scope = {
            "type": "http",
            "method": "POST",
            "path": "/.well-known/oauth-protected-resource",
            "scheme": "http",
            "headers": [(b"host", b"localhost")],
        }

        async def receive():
            return {"type": "http.request"}

        async def send(message):
            pass

        await mw(scope, receive, send)
        assert called["flag"] is True

    @pytest.mark.asyncio
    async def test_well_known_middleware_skips_non_http_scope(self):
        """Lifespan / websocket scopes pass straight through."""
        from unraid_mcp.core.auth import WellKnownMiddleware

        called = {"flag": False}

        async def inner_app(scope, receive, send):
            called["flag"] = True

        mw = WellKnownMiddleware(inner_app)
        scope = {"type": "lifespan"}

        async def receive():
            return {"type": "lifespan.startup"}

        async def send(message):
            pass

        await mw(scope, receive, send)
        assert called["flag"] is True
