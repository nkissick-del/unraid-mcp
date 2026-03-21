"""System metrics and time tools.

This module provides tools for retrieving system performance metrics (CPU,
memory, temperature), system time configuration, and timezone options.
"""

from typing import Any

from fastmcp import FastMCP

from ..config.logging import logger
from ..core.client import make_graphql_request
from ..core.decorators import tool_error_handler
from ..core.exceptions import ToolError
from ..core.utils import ensure_dict, ensure_list, format_bytes
from .queries.system_extra import SYSTEM_METRICS_QUERY


def register_metrics_tools(mcp: FastMCP) -> None:
    """Register metrics tools with the FastMCP instance."""

    @mcp.tool()
    @tool_error_handler("retrieve system metrics")
    async def get_system_metrics() -> dict[str, Any]:
        """Retrieves real-time system metrics including CPU usage, memory utilization, and temperature sensor readings."""
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

    @mcp.tool()
    @tool_error_handler("retrieve system time")
    async def get_system_time() -> dict[str, Any]:
        """Retrieves system time configuration including current time, timezone, NTP settings, and NTP servers."""
        query = """
        query GetSystemTime { systemTime { currentTime timeZone useNtp ntpServers } }
        """
        response_data = await make_graphql_request(query)
        time_data = response_data.get("systemTime", {})
        return ensure_dict(time_data)

    @mcp.tool()
    @tool_error_handler("retrieve timezone options")
    async def get_timezone_options() -> dict[str, Any]:
        """Retrieves the list of available timezone options that can be configured on the Unraid server."""
        query = """
        query GetTimezoneOptions { timeZoneOptions { value label } }
        """
        response_data = await make_graphql_request(query)
        options = ensure_list(response_data.get("timeZoneOptions", []))
        return {"count": len(options), "timezones": options}

    logger.info("Metrics tools registered successfully")
