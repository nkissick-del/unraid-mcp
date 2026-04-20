"""ASGI middleware for bearer token authentication and health endpoint."""

from __future__ import annotations

import hmac
import json
import logging
import posixpath
import time
from typing import Any

logger = logging.getLogger(__name__)


class HealthMiddleware:
    """ASGI middleware that responds to GET /health before any auth check.

    Placed outermost so Docker healthchecks work without a bearer token.
    """

    def __init__(self, app: Any) -> None:
        self.app = app

    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None:
        if (
            scope["type"] == "http"
            and scope.get("method") == "GET"
            and scope.get("path") == "/health"
        ):
            body = json.dumps({"status": "ok"}).encode()
            await send(
                {
                    "type": "http.response.start",
                    "status": 200,
                    "headers": [
                        [b"content-type", b"application/json"],
                        [b"content-length", str(len(body)).encode()],
                    ],
                }
            )
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
        app: Any,
        token: str,
        disabled: bool = False,
        max_failures: int = 60,
        window_seconds: int = 60,
        log_throttle_seconds: int = 30,
    ) -> None:
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

    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None:
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
                send,
                401,
                "Invalid or missing bearer token",
                extra_headers=[[b"www-authenticate", b'Bearer realm="unraid-mcp"']],
            )
            return

        await self.app(scope, receive, send)

    def _extract_token(self, scope: dict[str, Any]) -> str | None:
        """Extract bearer token from Authorization header."""
        for key, value in scope.get("headers", []):
            if key == b"authorization":
                decoded: str = value.decode()
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

    async def _send_error(
        self,
        send: Any,
        status: int,
        message: str,
        extra_headers: list[list[bytes]] | None = None,
    ) -> None:
        """Send a JSON error response."""
        body = json.dumps({"error": message}).encode()
        headers = [
            [b"content-type", b"application/json"],
            [b"content-length", str(len(body)).encode()],
        ]
        if extra_headers:
            headers.extend(extra_headers)
        await send(
            {
                "type": "http.response.start",
                "status": status,
                "headers": headers,
            }
        )
        await send({"type": "http.response.body", "body": body})


class WellKnownMiddleware:
    """ASGI middleware serving RFC 9728 OAuth Protected Resource Metadata.

    MCP clients (e.g. Claude Code) probe GET /.well-known/oauth-protected-resource
    when they receive a 401 from the MCP endpoint — trying to discover an OAuth
    authorization server. Without a valid response here they cascade into a series
    of failed discovery requests and surface a generic "unknown error" to the user.

    This server does NOT implement OAuth. Returning the resource metadata with an
    empty authorization_servers list tells compliant clients: "Bearer auth is
    required; you must configure the token yourself — there is no OAuth flow."

    Place this OUTSIDE BearerAuthMiddleware (before it in the middleware list) so
    the discovery endpoint is reachable without a token. Only GET is handled for
    the well-known paths; all other requests fall through to the auth layer.
    """

    _WELL_KNOWN_PATHS: frozenset[str] = frozenset(
        {
            "/.well-known/oauth-protected-resource",
            "/.well-known/oauth-protected-resource/mcp",
        }
    )

    def __init__(self, app: Any) -> None:
        self.app = app

    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path: str = posixpath.normpath(scope.get("path", ""))
        method: str = scope.get("method", "").upper()

        if method != "GET" or path not in self._WELL_KNOWN_PATHS:
            await self.app(scope, receive, send)
            return

        host = "localhost"
        for key, val in scope.get("headers", []):
            if key.lower() == b"host":
                host = val.decode("latin-1")
                break

        scheme = scope.get("scheme", "http")
        resource = f"{scheme}://{host}"

        body: bytes = json.dumps(
            {
                "resource": resource,
                "bearer_methods_supported": ["header"],
            },
            separators=(",", ":"),
        ).encode()

        headers: list[tuple[bytes, bytes]] = [
            (b"content-type", b"application/json"),
            (b"content-length", str(len(body)).encode()),
        ]
        await send({"type": "http.response.start", "status": 200, "headers": headers})
        await send({"type": "http.response.body", "body": body, "more_body": False})
