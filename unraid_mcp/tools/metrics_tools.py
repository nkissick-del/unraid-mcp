"""System metrics and time tools.

This module provides tools for retrieving system performance metrics (CPU,
memory, temperature), system time configuration, and timezone options.
"""

from typing import Any

from fastmcp import FastMCP

from ..config.logging import logger
from ..core.client import make_graphql_request
from ..core.exceptions import ToolError
from ..core.utils import ensure_dict, ensure_list, format_bytes
from .queries.system_extra import SYSTEM_METRICS_QUERY


def register_metrics_tools(mcp: FastMCP) -> None:
    """Register metrics tools with the FastMCP instance."""

    @mcp.tool()
    async def get_system_metrics() -> dict[str, Any]:
        """Retrieves real-time system metrics including CPU usage, memory utilization, and temperature sensor readings."""
        try:
            logger.info("Executing get_system_metrics")
            response_data = await make_graphql_request(SYSTEM_METRICS_QUERY)
            raw_metrics = response_data.get("metrics", {})
            if not raw_metrics:
                raise ToolError("No metrics data returned from Unraid API")

            summary: dict[str, Any] = {}

            cpu = raw_metrics.get("cpu")
            if cpu:
                summary["cpu_percent_total"] = cpu.get("percentTotal")

            memory = raw_metrics.get("memory")
            if memory:
                summary["memory_percent_total"] = memory.get("percentTotal")
                summary["memory_total"] = format_bytes(memory.get("total"))
                summary["memory_used"] = format_bytes(memory.get("used"))
                summary["memory_free"] = format_bytes(memory.get("free"))

            temperature = raw_metrics.get("temperature")
            if temperature and temperature.get("summary"):
                summary["temperature_summary"] = temperature["summary"]

            return {"summary": summary, "details": raw_metrics}
        except Exception as e:
            logger.error(f"Error in get_system_metrics: {e}", exc_info=True)
            raise ToolError(f"Failed to retrieve system metrics: {str(e)}") from e

    @mcp.tool()
    async def get_system_time() -> dict[str, Any]:
        """Retrieves system time configuration including current time, timezone, NTP settings, and NTP servers."""
        query = """
        query GetSystemTime { systemTime { currentTime timeZone useNtp ntpServers } }
        """
        try:
            logger.info("Executing get_system_time")
            response_data = await make_graphql_request(query)
            time_data = response_data.get("systemTime", {})
            return ensure_dict(time_data)
        except Exception as e:
            logger.error(f"Error in get_system_time: {e}", exc_info=True)
            raise ToolError(f"Failed to retrieve system time: {str(e)}") from e

    @mcp.tool()
    async def get_timezone_options() -> dict[str, Any]:
        """Retrieves the list of available timezone options that can be configured on the Unraid server."""
        query = """
        query GetTimezoneOptions { timeZoneOptions { value label } }
        """
        try:
            logger.info("Executing get_timezone_options")
            response_data = await make_graphql_request(query)
            options = ensure_list(response_data.get("timeZoneOptions", []))
            return {"count": len(options), "timezones": options}
        except Exception as e:
            logger.error(f"Error in get_timezone_options: {e}", exc_info=True)
            raise ToolError(f"Failed to retrieve timezone options: {str(e)}") from e

    logger.info("Metrics tools registered successfully")
