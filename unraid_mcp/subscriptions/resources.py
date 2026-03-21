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
from .manager import subscription_manager

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
