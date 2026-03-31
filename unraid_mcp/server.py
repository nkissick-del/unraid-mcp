"""Modular Unraid MCP Server.

This is the main server implementation using the modular architecture with
separate modules for configuration, core functionality, subscriptions, and tools.
"""

import importlib
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastmcp import FastMCP
from fastmcp.server.middleware.caching import ResponseCachingMiddleware
from fastmcp.server.middleware.error_handling import ErrorHandlingMiddleware
from fastmcp.server.middleware.logging import LoggingMiddleware
from fastmcp.server.middleware.rate_limiting import SlidingWindowRateLimitingMiddleware
from fastmcp.server.middleware.response_limiting import ResponseLimitingMiddleware

from . import __version__
from .config.logging import logger
from .config.settings import (
    ENABLED_MODULES,
    LOG_LEVEL_STR,
    MCP_AUTH_TOKEN,
    MCP_CACHE_ENABLED,
    MCP_CACHE_TTL,
    MCP_MAX_RESPONSE_KB,
    MCP_RATE_LIMIT,
    MCP_RATE_WINDOW_MINUTES,
    UNRAID_API_KEY,
    UNRAID_API_URL,
    UNRAID_MCP_HOST,
    UNRAID_MCP_PORT,
    UNRAID_MCP_TRANSPORT,
)
from .core.auth import BearerAuthMiddleware, HealthMiddleware
from .core.client import close_http_client
from .core.utils import safe_display_url
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


# --- Middleware chain (outermost -> innermost) ---
_logging_middleware = LoggingMiddleware(
    logger=logger,
    methods=["tools/call", "resources/read"],
)
_error_middleware = ErrorHandlingMiddleware(
    logger=logger,
    include_traceback=LOG_LEVEL_STR == "DEBUG",
)
_rate_limiter = SlidingWindowRateLimitingMiddleware(
    max_requests=MCP_RATE_LIMIT,
    window_minutes=MCP_RATE_WINDOW_MINUTES,
)
_response_limiter = ResponseLimitingMiddleware(max_size=MCP_MAX_RESPONSE_KB * 1024)
_middleware_stack = [
    _logging_middleware,
    _error_middleware,
    _rate_limiter,
    _response_limiter,
]

# Initialize FastMCP instance
mcp = FastMCP(
    name="Unraid MCP Server",
    instructions="Provides tools to interact with an Unraid server's GraphQL API.",
    version=__version__,
    lifespan=app_lifespan,
    middleware=_middleware_stack,
)


def _get_tool_names(mcp: FastMCP) -> set[str]:
    """Extract registered tool names from the FastMCP provider."""
    if not mcp.providers:
        return set()
    provider = mcp.providers[0]
    return {
        k.split(":")[1].split("@")[0]
        for k in provider._components  # type: ignore[attr-defined]
        if k.startswith("tool:")
    }


def register_all_modules() -> None:
    """Register tools and resources based on ENABLED_MODULES configuration."""
    try:
        # Always register base subscription resources (lightweight log stream endpoint)
        register_subscription_resources(mcp)

        non_cacheable_tools: list[str] = []

        # Conditionally register tool modules via registry
        for module_name in ENABLED_MODULES:
            if module_name not in MODULE_REGISTRY:
                logger.warning(f"Unknown module '{module_name}' in ENABLED_MODULES, skipping")
                continue

            entry = MODULE_REGISTRY[module_name]
            tools_before = _get_tool_names(mcp)

            mod = importlib.import_module(entry["import"])
            getattr(mod, entry["register"])(mcp)

            if not entry["cacheable"]:
                tools_after = _get_tool_names(mcp)
                new_tools = tools_after - tools_before
                non_cacheable_tools.extend(new_tools)

        # Add response caching middleware with per-tool exclusions
        cache_mw = ResponseCachingMiddleware(
            call_tool_settings={
                "enabled": MCP_CACHE_ENABLED,
                "ttl": MCP_CACHE_TTL,
                "excluded_tools": non_cacheable_tools,
            },
        )
        mcp.add_middleware(cache_mw)

        if non_cacheable_tools:
            logger.info(f"Cache configured: {len(non_cacheable_tools)} mutation tools excluded")
        logger.info(f"Modules registered: {sorted(ENABLED_MODULES)}")

    except Exception as e:
        logger.error(f"Failed to register modules: {e}", exc_info=True)
        raise


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

            asgi_app = mcp.http_app(
                transport="streamable-http",
                path="/mcp",
            )
            # Wrap with ASGI middleware (outermost added last)
            wrapped = BearerAuthMiddleware(
                asgi_app,
                token=MCP_AUTH_TOKEN,
                disabled=not MCP_AUTH_TOKEN,
            )
            final_app = HealthMiddleware(wrapped)
            uvicorn.run(
                final_app,
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


if __name__ == "__main__":
    run_server()
