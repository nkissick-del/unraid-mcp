"""MCP resources that expose subscription data.

This module defines MCP resources that bridge between the subscription manager
and the MCP protocol, providing fallback queries when subscription data is unavailable.
"""

import asyncio
import json
import os
from pathlib import Path

from fastmcp import FastMCP

from ..config.logging import logger
from .configs import SUBSCRIPTION_CONFIGS
from .manager import subscription_manager
from .snapshot import subscribe_once

# Async-safe subscription startup guard
_subscriptions_lock = asyncio.Lock()
_subscriptions_started = False
_subscriptions_start_failed = False
_MAX_STARTUP_RETRIES = 3
_startup_attempts = 0


async def ensure_subscriptions_started() -> None:
    """Ensure subscriptions are started, called from async context."""
    global _subscriptions_started, _subscriptions_start_failed, _startup_attempts

    if _subscriptions_started:
        return  # Fast path — no lock needed once started

    if _subscriptions_start_failed:
        return  # Startup previously failed permanently — don't retry

    async with _subscriptions_lock:
        if _subscriptions_started or _subscriptions_start_failed:
            return  # Double-check after acquiring lock

        _startup_attempts += 1
        logger.info(
            f"[STARTUP] Starting subscriptions (attempt {_startup_attempts}/{_MAX_STARTUP_RETRIES})..."
        )
        try:
            await autostart_subscriptions()
            _subscriptions_started = True
            logger.info("[STARTUP] Subscriptions started successfully")
        except Exception as e:
            logger.error(f"[STARTUP] Failed to start subscriptions: {e}", exc_info=True)
            if _startup_attempts >= _MAX_STARTUP_RETRIES:
                _subscriptions_start_failed = True
                logger.error(
                    f"[STARTUP] Max startup attempts ({_MAX_STARTUP_RETRIES}) reached — giving up"
                )


async def autostart_subscriptions() -> None:
    """Auto-start all subscriptions marked for auto-start in SubscriptionManager."""
    logger.info("[AUTOSTART] Initiating subscription auto-start process...")

    try:
        # Use the new SubscriptionManager auto-start method
        await subscription_manager.auto_start_all_subscriptions()
        logger.info("[AUTOSTART] Auto-start process completed successfully")
    except Exception as e:
        logger.error(f"[AUTOSTART] Failed during auto-start process: {e}", exc_info=True)
        raise  # Re-raise to allow ensure_subscriptions_started() to handle retries

    # Optional log file subscription
    log_path = os.getenv("UNRAID_AUTOSTART_LOG_PATH")
    if log_path is None:
        # Default to syslog if available
        default_path = "/var/log/syslog"
        if Path(default_path).exists():
            log_path = default_path
            logger.info(f"[AUTOSTART] Using default log path: {default_path}")

    if log_path:
        try:
            logger.info(f"[AUTOSTART] Starting log file subscription for: {log_path}")
            config = subscription_manager.subscription_configs.get("logFileSubscription")
            if config:
                await subscription_manager.start_subscription(
                    "logFileSubscription", str(config["query"]), {"path": log_path}
                )
                logger.info(f"[AUTOSTART] Log file subscription started for: {log_path}")
            else:
                logger.error("[AUTOSTART] logFileSubscription config not found")
        except Exception as e:
            logger.error(f"[AUTOSTART] Failed to start log file subscription: {e}", exc_info=True)
    else:
        logger.info("[AUTOSTART] No log file path configured for auto-start")


async def _live_subscription_fallback(action: str) -> str:
    """Fetch a one-shot snapshot from any configured subscription by name.

    This is a fallback — explicit resources (unraid://system/cpu, etc.) use
    persistent subscriptions and are faster. This opens a fresh WebSocket per call.
    """
    if action not in SUBSCRIPTION_CONFIGS:
        available = sorted(SUBSCRIPTION_CONFIGS.keys())
        return json.dumps(
            {
                "error": "Unknown subscription action",
                "requested": action,
                "available": available,
            },
            indent=2,
        )

    config = SUBSCRIPTION_CONFIGS[action]
    query = config["query"]

    try:
        data = await subscribe_once(query, timeout=10.0)
        return json.dumps(data, indent=2)
    except Exception as e:
        return json.dumps(
            {
                "error": str(e),
                "action": action,
                "message": "Failed to fetch subscription snapshot. Check server logs.",
            },
            indent=2,
        )


def register_subscription_resources(mcp: FastMCP) -> None:
    """Register all subscription resources with the FastMCP instance.

    Args:
        mcp: FastMCP instance to register resources with
    """

    @mcp.resource("unraid://logs/stream")
    async def logs_stream_resource() -> str:
        """Real-time log stream data from subscription."""
        await ensure_subscriptions_started()
        data = await subscription_manager.get_resource_data("logFileSubscription")
        if data:
            return json.dumps(data, indent=2)
        if _subscriptions_start_failed:
            return json.dumps(
                {
                    "status": "Subscription startup failed",
                    "message": f"Subscriptions failed to start after {_MAX_STARTUP_RETRIES} attempts. Check server logs for details.",
                }
            )
        return json.dumps(
            {
                "status": "No subscription data yet",
                "message": "Subscriptions auto-start on server boot. If this persists, check server logs for WebSocket/auth issues.",
            }
        )

    @mcp.resource("unraid://live/{action}")
    async def live_fallback(action: str) -> str:
        """Dynamic fallback: fetch a one-shot snapshot from any configured subscription by name."""
        return await _live_subscription_fallback(action)

    logger.info("Subscription resources registered successfully")


def register_live_subscription_resources(mcp: FastMCP) -> None:
    """Register live subscription resources gated under the 'subscriptions' module.

    These resources expose real-time streaming data (Docker stats, CPU, memory, array).

    Args:
        mcp: FastMCP instance to register resources with
    """

    @mcp.resource("unraid://docker/stats")
    async def docker_stats_resource() -> str:
        """Real-time Docker container resource statistics."""
        await ensure_subscriptions_started()
        data = await subscription_manager.get_resource_data("dockerContainerStats")
        if data:
            return json.dumps(data, indent=2)
        if _subscriptions_start_failed:
            return json.dumps(
                {
                    "status": "Subscription startup failed",
                    "message": f"Subscriptions failed to start after {_MAX_STARTUP_RETRIES} attempts.",
                }
            )
        return json.dumps(
            {
                "status": "No subscription data yet",
                "message": "Docker stats subscription is starting. Data will appear shortly.",
            }
        )

    @mcp.resource("unraid://system/cpu")
    async def cpu_metrics_resource() -> str:
        """Real-time CPU utilization metrics."""
        await ensure_subscriptions_started()
        data = await subscription_manager.get_resource_data("systemMetricsCpu")
        if data:
            return json.dumps(data, indent=2)
        if _subscriptions_start_failed:
            return json.dumps(
                {
                    "status": "Subscription startup failed",
                    "message": f"Subscriptions failed to start after {_MAX_STARTUP_RETRIES} attempts.",
                }
            )
        return json.dumps(
            {
                "status": "No subscription data yet",
                "message": "CPU metrics subscription is starting. Data will appear shortly.",
            }
        )

    @mcp.resource("unraid://system/memory")
    async def memory_metrics_resource() -> str:
        """Real-time memory utilization metrics."""
        await ensure_subscriptions_started()
        data = await subscription_manager.get_resource_data("systemMetricsMemory")
        if data:
            return json.dumps(data, indent=2)
        if _subscriptions_start_failed:
            return json.dumps(
                {
                    "status": "Subscription startup failed",
                    "message": f"Subscriptions failed to start after {_MAX_STARTUP_RETRIES} attempts.",
                }
            )
        return json.dumps(
            {
                "status": "No subscription data yet",
                "message": "Memory metrics subscription is starting. Data will appear shortly.",
            }
        )

    @mcp.resource("unraid://array/status")
    async def array_status_resource() -> str:
        """Real-time array status updates."""
        await ensure_subscriptions_started()
        data = await subscription_manager.get_resource_data("arraySubscription")
        if data:
            return json.dumps(data, indent=2)
        if _subscriptions_start_failed:
            return json.dumps(
                {
                    "status": "Subscription startup failed",
                    "message": f"Subscriptions failed to start after {_MAX_STARTUP_RETRIES} attempts.",
                }
            )
        return json.dumps(
            {
                "status": "No subscription data yet",
                "message": "Array status subscription is starting. Data will appear shortly.",
            }
        )

    logger.info("Live subscription resources registered successfully")


# Extra subscription resources (gated under subscriptions-extra module)
_EXTRA_SUBSCRIPTION_RESOURCES: list[tuple[str, str, str]] = [
    (
        "notificationAdded",
        "unraid://notifications/stream",
        "Real-time notification stream (new notifications as they arrive)",
    ),
    (
        "notificationsWarningsAndAlerts",
        "unraid://notifications/alerts",
        "Real-time warning and alert notification counts",
    ),
    (
        "parityHistorySubscription",
        "unraid://parity/status",
        "Real-time parity check status and history",
    ),
    (
        "systemMetricsTemperature",
        "unraid://system/temperature",
        "Real-time system temperature metrics",
    ),
    (
        "notificationsOverview",
        "unraid://notifications/overview",
        "Real-time notifications overview with counts by severity",
    ),
    (
        "systemMetricsCpuTelemetry",
        "unraid://system/cpu-telemetry",
        "Detailed per-core CPU telemetry with load averages",
    ),
    (
        "upsUpdates",
        "unraid://ups/status",
        "Real-time UPS status and battery updates",
    ),
    (
        "pluginInstallUpdates",
        "unraid://plugins/install-progress",
        "Plugin installation progress updates (event-driven)",
    ),
    (
        "displaySubscription",
        "unraid://display/updates",
        "Real-time display/theme configuration updates",
    ),
    (
        "ownerSubscription",
        "unraid://owner/updates",
        "Real-time owner/account information updates",
    ),
    (
        "serversSubscription",
        "unraid://servers/updates",
        "Real-time server discovery and status updates",
    ),
]


def _register_subscription_resource(mcp: FastMCP, sub_name: str, uri: str, desc: str) -> None:
    """Register a single subscription as an MCP resource.

    Each call creates a new closure capturing sub_name for the resource handler.
    """

    @mcp.resource(uri)
    async def _resource_handler() -> str:
        await ensure_subscriptions_started()
        data = await subscription_manager.get_resource_data(sub_name)
        if data:
            return json.dumps(data, indent=2)
        if _subscriptions_start_failed:
            return json.dumps(
                {
                    "status": "Subscription startup failed",
                    "message": f"Subscriptions failed to start after {_MAX_STARTUP_RETRIES} attempts.",
                }
            )
        return json.dumps(
            {
                "status": "No subscription data yet",
                "message": f"{desc} — subscription is starting. Data will appear shortly.",
            }
        )

    _resource_handler.__doc__ = desc


def register_extra_subscription_resources(mcp: FastMCP) -> None:
    """Register all extra subscription resources gated under subscriptions-extra module."""
    for sub_name, uri, desc in _EXTRA_SUBSCRIPTION_RESOURCES:
        _register_subscription_resource(mcp, sub_name, uri, desc)
    logger.info("Extra subscription resources registered successfully")
