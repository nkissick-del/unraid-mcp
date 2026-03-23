"""Extra system information tools.

This module provides tools for retrieving additional system details such as
configuration status, flash drive info, running services, server connectivity,
and multi-server listings.
"""

from typing import Any

from fastmcp import FastMCP

from ..core.client import make_graphql_request
from ..core.decorators import tool_error_handler
from ..core.utils import ensure_dict, ensure_list


def register_system_extra_tools(mcp: FastMCP) -> None:
    """Register system-extra tools with the FastMCP instance."""

    @mcp.tool()
    @tool_error_handler("retrieve config status")
    async def get_config_status() -> dict[str, Any]:
        """Retrieves the Unraid configuration validation status, including whether the config is valid and any errors."""
        query = """
        query GetConfig { config { id valid error } }
        """
        response_data = await make_graphql_request(query)
        config = response_data.get("config", {})
        return ensure_dict(config)

    @mcp.tool()
    @tool_error_handler("retrieve flash info")
    async def get_flash_info() -> dict[str, Any]:
        """Retrieves information about the Unraid boot USB flash drive, including GUID, vendor, and product details."""
        query = """
        query GetFlashInfo { flash { id guid vendor product } }
        """
        response_data = await make_graphql_request(query)
        flash = response_data.get("flash", {})
        return ensure_dict(flash)

    @mcp.tool()
    @tool_error_handler("retrieve services")
    async def get_services() -> dict[str, Any]:
        """Retrieves the list of running services on the Unraid server, with online status, uptime, and version."""
        query = """
        query GetServices { services { id name online uptime { timestamp } version } }
        """
        response_data = await make_graphql_request(query)
        services = ensure_list(response_data.get("services", []))
        online_count = sum(1 for s in services if s.get("online"))
        offline_count = len(services) - online_count
        return {
            "summary": {
                "total": len(services),
                "online": online_count,
                "offline": offline_count,
            },
            "services": services,
        }

    @mcp.tool()
    @tool_error_handler("check server online status")
    async def is_server_online() -> dict[str, Any]:
        """Checks whether the Unraid server is online and reachable."""
        query = """
        query IsServerOnline { online }
        """
        response_data = await make_graphql_request(query)
        return {"online": response_data.get("online", False)}

    @mcp.tool()
    @tool_error_handler("retrieve servers")
    async def get_servers() -> dict[str, Any]:
        """Retrieves a list of all Unraid servers with their status, IP addresses, and connection URLs."""
        query = """
        query GetServers {
          servers {
            id guid name comment status wanip lanip localurl remoteurl
            owner { username url avatar }
          }
        }
        """
        response_data = await make_graphql_request(query)
        servers = ensure_list(response_data.get("servers", []))
        return {
            "count": len(servers),
            "servers": servers,
        }
