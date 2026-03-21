"""Subscription configuration data for all GraphQL subscriptions.

This module contains the static configuration for each subscription type,
extracted from the SubscriptionManager to keep data separate from logic.
"""

from typing import Any

SUBSCRIPTION_CONFIGS: dict[str, dict[str, Any]] = {
    "logFileSubscription": {
        "query": """
                subscription LogFileSubscription($path: String!) {
                    logFile(path: $path) {
                        path
                        content
                        totalLines
                    }
                }
                """,
        "resource": "unraid://logs/stream",
        "description": "Real-time log file streaming",
        "auto_start": False,  # Started manually with path parameter
    },
    "dockerContainerStats": {
        "query": """
                subscription DockerContainerStats {
                    dockerContainerStats {
                        id
                        cpuPercent
                        memUsage
                        memPercent
                        netIO
                        blockIO
                    }
                }
                """,
        "resource": "unraid://docker/stats",
        "description": "Real-time Docker container resource statistics",
        "auto_start": True,
    },
    "systemMetricsCpu": {
        "query": """
                subscription SystemMetricsCpu {
                    systemMetricsCpu {
                        percentTotal
                    }
                }
                """,
        "resource": "unraid://system/cpu",
        "description": "Real-time CPU utilization metrics",
        "auto_start": True,
    },
    "systemMetricsMemory": {
        "query": """
                subscription SystemMetricsMemory {
                    systemMetricsMemory {
                        total
                        used
                        free
                        available
                        percentTotal
                    }
                }
                """,
        "resource": "unraid://system/memory",
        "description": "Real-time memory utilization metrics",
        "auto_start": True,
    },
    "arraySubscription": {
        "query": """
                subscription ArraySubscription {
                    arraySubscription {
                        id
                        state
                        capacity {
                            disks {
                                free
                                size
                            }
                        }
                    }
                }
                """,
        "resource": "unraid://array/status",
        "description": "Real-time array status updates",
        "auto_start": True,
    },
    "notificationAdded": {
        "query": """subscription NotificationAdded {
                    notificationAdded { id type subject description importance timestamp file }
                }""",
        "resource": "unraid://notifications/stream",
        "description": "Real-time notification stream (new notifications as they arrive)",
        "auto_start": True,
    },
    "notificationsWarningsAndAlerts": {
        "query": """subscription NotificationsWarningsAndAlerts {
                    notificationsWarningsAndAlerts { warnings alerts }
                }""",
        "resource": "unraid://notifications/alerts",
        "description": "Real-time warning and alert notification counts",
        "auto_start": True,
    },
    "parityHistorySubscription": {
        "query": """subscription ParityHistorySubscription {
                    parityHistorySubscription { date duration speed status errors elapsed correcting progress }
                }""",
        "resource": "unraid://parity/status",
        "description": "Real-time parity check status and history",
        "auto_start": True,
    },
    "systemMetricsTemperature": {
        "query": """subscription SystemMetricsTemperature {
                    systemMetricsTemperature { cpu motherboard drives { name temp } }
                }""",
        "resource": "unraid://system/temperature",
        "description": "Real-time system temperature metrics",
        "auto_start": True,
    },
    "notificationsOverview": {
        "query": """subscription NotificationsOverview {
                    notificationsOverview { unread total info warning alert }
                }""",
        "resource": "unraid://notifications/overview",
        "description": "Real-time notifications overview with counts by severity",
        "auto_start": True,
    },
    "systemMetricsCpuTelemetry": {
        "query": """subscription SystemMetricsCpuTelemetry {
                    systemMetricsCpuTelemetry { cores { id percent frequency } percentTotal loadAverage { one five fifteen } }
                }""",
        "resource": "unraid://system/cpu-telemetry",
        "description": "Detailed per-core CPU telemetry with load averages",
        "auto_start": True,
    },
    "upsUpdates": {
        "query": """subscription UpsUpdates {
                    upsUpdates { name status batteryCharge runtime load inputVoltage outputVoltage }
                }""",
        "resource": "unraid://ups/status",
        "description": "Real-time UPS status and battery updates",
        "auto_start": True,
    },
    "pluginInstallUpdates": {
        "query": """subscription PluginInstallUpdates {
                    pluginInstallUpdates { plugin status progress message error }
                }""",
        "resource": "unraid://plugins/install-progress",
        "description": "Plugin installation progress updates (event-driven)",
        "auto_start": False,
    },
    "displaySubscription": {
        "query": """subscription DisplaySubscription {
                    displaySubscription { case { icon url error } banner { icon url error } }
                }""",
        "resource": "unraid://display/updates",
        "description": "Real-time display/theme configuration updates",
        "auto_start": True,
    },
    "ownerSubscription": {
        "query": """subscription OwnerSubscription {
                    ownerSubscription { username avatar url }
                }""",
        "resource": "unraid://owner/updates",
        "description": "Real-time owner/account information updates",
        "auto_start": True,
    },
    "serversSubscription": {
        "query": """subscription ServersSubscription {
                    serversSubscription { guid name status localUrl remoteUrl wanIp }
                }""",
        "resource": "unraid://servers/updates",
        "description": "Real-time server discovery and status updates",
        "auto_start": True,
    },
}
