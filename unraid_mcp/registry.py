"""Module registry mapping module names to their registration functions.

Adding a new module requires only a single entry here. The server.py
register_all_modules() function iterates this registry to load modules.
"""

from typing import Any

# Each entry maps a module name (as used in ENABLED_MODULES / settings.py)
# to a dict with:
#   "import"    – the dotted import path for the module
#   "register"  – the name of the registration function to call
#   "cacheable" – True for read-only / query modules, False for mutations
MODULE_REGISTRY: dict[str, dict[str, Any]] = {
    "diagnostics": {
        "import": "unraid_mcp.subscriptions.diagnostics",
        "register": "register_diagnostic_tools",
        "cacheable": True,
    },
    "system": {
        "import": "unraid_mcp.tools.system",
        "register": "register_system_tools",
        "cacheable": True,
    },
    "docker": {
        "import": "unraid_mcp.tools.docker",
        "register": "register_docker_tools",
        "cacheable": True,
    },
    "docker-admin": {
        "import": "unraid_mcp.tools.docker_admin",
        "register": "register_docker_admin_tools",
        "cacheable": False,
    },
    "vms": {
        "import": "unraid_mcp.tools.virtualization",
        "register": "register_vm_tools",
        "cacheable": False,
    },
    "storage": {
        "import": "unraid_mcp.tools.storage",
        "register": "register_storage_tools",
        "cacheable": True,
    },
    "notifications": {
        "import": "unraid_mcp.tools.notification_actions",
        "register": "register_notification_tools",
        "cacheable": True,
    },
    "array": {
        "import": "unraid_mcp.tools.array",
        "register": "register_array_tools",
        "cacheable": False,
    },
    "health": {
        "import": "unraid_mcp.tools.health",
        "register": "register_health_tools",
        "cacheable": True,
    },
    "rclone": {
        "import": "unraid_mcp.tools.rclone",
        "register": "register_rclone_tools",
        "cacheable": False,
    },
    "api": {
        "import": "unraid_mcp.tools.api",
        "register": "register_api_tools",
        "cacheable": True,
    },
    "system-extra": {
        "import": "unraid_mcp.tools.system_extra",
        "register": "register_system_extra_tools",
        "cacheable": True,
    },
    "metrics": {
        "import": "unraid_mcp.tools.metrics_tools",
        "register": "register_metrics_tools",
        "cacheable": True,
    },
    "ups": {
        "import": "unraid_mcp.tools.ups_tools",
        "register": "register_ups_tools",
        "cacheable": True,
    },
    "parity": {
        "import": "unraid_mcp.tools.parity",
        "register": "register_parity_tools",
        "cacheable": True,
    },
    "docker-batch": {
        "import": "unraid_mcp.tools.docker_batch",
        "register": "register_docker_batch_tools",
        "cacheable": False,
    },
    "notifications-extra": {
        "import": "unraid_mcp.tools.notifications_extra",
        "register": "register_notifications_extra_tools",
        "cacheable": True,
    },
    "ups-admin": {
        "import": "unraid_mcp.tools.ups_admin",
        "register": "register_ups_admin_tools",
        "cacheable": False,
    },
    "subscriptions": {
        "import": "unraid_mcp.subscriptions.resources",
        "register": "register_live_subscription_resources",
        "cacheable": True,
    },
    "subscriptions-extra": {
        "import": "unraid_mcp.subscriptions.resources",
        "register": "register_extra_subscription_resources",
        "cacheable": True,
    },
    "customization": {
        "import": "unraid_mcp.tools.customization",
        "register": "register_customization_tools",
        "cacheable": False,
    },
    "onboarding": {
        "import": "unraid_mcp.tools.onboarding",
        "register": "register_onboarding_tools",
        "cacheable": False,
    },
    "docker-organize": {
        "import": "unraid_mcp.tools.docker_organize",
        "register": "register_docker_organize_tools",
        "cacheable": False,
    },
    "plugins": {
        "import": "unraid_mcp.tools.plugins",
        "register": "register_plugins_tools",
        "cacheable": False,
    },
    "server-admin": {
        "import": "unraid_mcp.tools.server_admin",
        "register": "register_server_admin_tools",
        "cacheable": False,
    },
    "connect": {
        "import": "unraid_mcp.tools.connect_admin",
        "register": "register_connect_admin_tools",
        "cacheable": True,
    },
    "auth": {
        "import": "unraid_mcp.tools.auth",
        "register": "register_auth_tools",
        "cacheable": False,
    },
    "array-admin": {
        "import": "unraid_mcp.tools.array_admin",
        "register": "register_array_admin_tools",
        "cacheable": False,
    },
}
