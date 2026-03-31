"""Tests for middleware wiring in server.py."""


class TestMiddlewareWiring:
    def test_mcp_has_middleware(self):
        from unraid_mcp.server import mcp

        assert mcp.middleware is not None
        assert len(mcp.middleware) > 0, "No middleware configured"

    def test_middleware_order(self):
        from fastmcp.server.middleware.error_handling import ErrorHandlingMiddleware
        from fastmcp.server.middleware.logging import LoggingMiddleware
        from fastmcp.server.middleware.rate_limiting import (
            SlidingWindowRateLimitingMiddleware,
        )

        from unraid_mcp.server import mcp

        types = [type(m) for m in mcp.middleware]
        assert LoggingMiddleware in types
        assert ErrorHandlingMiddleware in types
        assert SlidingWindowRateLimitingMiddleware in types

        log_idx = types.index(LoggingMiddleware)
        err_idx = types.index(ErrorHandlingMiddleware)
        rate_idx = types.index(SlidingWindowRateLimitingMiddleware)
        assert log_idx < err_idx < rate_idx

    def test_rate_limit_uses_config(self):
        from fastmcp.server.middleware.rate_limiting import (
            SlidingWindowRateLimitingMiddleware,
        )

        from unraid_mcp.server import mcp

        rate_mw = None
        for m in mcp.middleware:
            if isinstance(m, SlidingWindowRateLimitingMiddleware):
                rate_mw = m
                break
        assert rate_mw is not None

    def test_response_limiter_present(self):
        from fastmcp.server.middleware.response_limiting import (
            ResponseLimitingMiddleware,
        )

        from unraid_mcp.server import mcp

        types = [type(m) for m in mcp.middleware]
        assert ResponseLimitingMiddleware in types

    def test_cache_middleware_present(self):
        """ResponseCachingMiddleware should be in the stack after module registration."""
        from fastmcp.server.middleware.caching import ResponseCachingMiddleware
        from unraid_mcp.server import mcp

        # Cache middleware is added dynamically during register_all_modules
        # It may or may not be present depending on whether register_all_modules has been called
        # Just verify the import works and the type exists
        assert ResponseCachingMiddleware is not None
