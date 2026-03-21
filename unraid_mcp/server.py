"""Modular Unraid MCP Server.

This is the main server implementation using the modular architecture with
separate modules for configuration, core functionality, subscriptions, and tools.
"""

import importlib
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastmcp import FastMCP

from . import __version__
from .config.logging import logger
from .config.settings import (
    ENABLED_MODULES,
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


# Initialize FastMCP instance
mcp = FastMCP(
    name="Unraid MCP Server",
    instructions="Provides tools to interact with an Unraid server's GraphQL API.",
    version=__version__,
    lifespan=app_lifespan,
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
            # Use the recommended Streamable HTTP transport
            mcp.run(
                transport="streamable-http",
                host=UNRAID_MCP_HOST,
                port=UNRAID_MCP_PORT,
                path="/mcp",  # Standard path for MCP
            )
        elif UNRAID_MCP_TRANSPORT == "sse":
            # Deprecated SSE transport - log warning
            logger.warning(
                "SSE transport is deprecated and may be removed in a future version. Consider switching to 'streamable-http'."
            )
            mcp.run(
                transport="sse",
                host=UNRAID_MCP_HOST,
                port=UNRAID_MCP_PORT,
                path="/mcp",  # Keep custom path for SSE
            )
        elif UNRAID_MCP_TRANSPORT == "stdio":
            mcp.run()  # Defaults to stdio
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
