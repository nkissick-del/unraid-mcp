"""UPS device management tools.

This module provides tools for retrieving UPS (Uninterruptible Power Supply)
device information, individual device details, and UPS daemon configuration.
"""

from typing import Any

from fastmcp import FastMCP

from ..core.client import make_graphql_request
from ..core.decorators import tool_error_handler
from ..core.utils import ensure_dict, ensure_list, validate_string_not_empty
from .queries.ups import UPS_CONFIGURATION_QUERY, UPS_DEVICE_BY_ID_QUERY, UPS_DEVICES_QUERY


def register_ups_tools(mcp: FastMCP) -> None:
    """Register UPS tools with the FastMCP instance."""

    @mcp.tool()
    @tool_error_handler("retrieve UPS devices")
    async def list_ups_devices() -> dict[str, Any]:
        """Retrieves all UPS devices connected to the Unraid server, including battery and power status."""
        response_data = await make_graphql_request(UPS_DEVICES_QUERY)
        devices = ensure_list(response_data.get("upsDevices", []))
        return {"count": len(devices), "devices": devices}

    @mcp.tool()
    @tool_error_handler("retrieve UPS device")
    async def get_ups_device(device_id: str) -> dict[str, Any]:
        """Retrieves detailed information about a specific UPS device by its ID, including battery and power data."""
        validate_string_not_empty(device_id, "device_id")
        response_data = await make_graphql_request(
            UPS_DEVICE_BY_ID_QUERY, variables={"id": device_id}
        )
        device = response_data.get("upsDeviceById", {})
        return ensure_dict(device)

    @mcp.tool()
    @tool_error_handler("retrieve UPS configuration")
    async def get_ups_configuration() -> dict[str, Any]:
        """Retrieves the UPS daemon configuration, including service type, cable, device, and shutdown settings."""
        response_data = await make_graphql_request(UPS_CONFIGURATION_QUERY)
        config = response_data.get("upsConfiguration", {})
        return ensure_dict(config)
