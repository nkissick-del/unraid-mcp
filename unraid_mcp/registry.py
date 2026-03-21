"""Module registry mapping module names to their registration functions.

Adding a new module requires only a single entry here. The server.py
register_all_modules() function iterates this registry to load modules.
"""

# Each entry maps a module name (as used in ENABLED_MODULES / settings.py)
# to a (import_path, function_name) tuple.
MODULE_REGISTRY: dict[str, tuple[str, str]] = {
    "diagnostics": ("unraid_mcp.subscriptions.diagnostics", "register_diagnostic_tools"),
    "system": ("unraid_mcp.tools.system", "register_system_tools"),
    "docker": ("unraid_mcp.tools.docker", "register_docker_tools"),
    "docker-admin": ("unraid_mcp.tools.docker_admin", "register_docker_admin_tools"),
    "vms": ("unraid_mcp.tools.virtualization", "register_vm_tools"),
    "storage": ("unraid_mcp.tools.storage", "register_storage_tools"),
    "notifications": ("unraid_mcp.tools.notification_actions", "register_notification_tools"),
    "array": ("unraid_mcp.tools.array", "register_array_tools"),
    "health": ("unraid_mcp.tools.health", "register_health_tools"),
    "rclone": ("unraid_mcp.tools.rclone", "register_rclone_tools"),
    "api": ("unraid_mcp.tools.api", "register_api_tools"),
    "system-extra": ("unraid_mcp.tools.system_extra", "register_system_extra_tools"),
    "metrics": ("unraid_mcp.tools.metrics_tools", "register_metrics_tools"),
    "ups": ("unraid_mcp.tools.ups_tools", "register_ups_tools"),
    "parity": ("unraid_mcp.tools.parity", "register_parity_tools"),
    "docker-batch": ("unraid_mcp.tools.docker_batch", "register_docker_batch_tools"),
    "notifications-extra": (
        "unraid_mcp.tools.notifications_extra",
        "register_notifications_extra_tools",
    ),
    "ups-admin": ("unraid_mcp.tools.ups_admin", "register_ups_admin_tools"),
    "subscriptions": (
        "unraid_mcp.subscriptions.resources",
        "register_live_subscription_resources",
    ),
    "subscriptions-extra": (
        "unraid_mcp.subscriptions.resources",
        "register_extra_subscription_resources",
    ),
    "customization": ("unraid_mcp.tools.customization", "register_customization_tools"),
    "onboarding": ("unraid_mcp.tools.onboarding", "register_onboarding_tools"),
    "docker-organize": ("unraid_mcp.tools.docker_organize", "register_docker_organize_tools"),
    "plugins": ("unraid_mcp.tools.plugins", "register_plugins_tools"),
    "server-admin": ("unraid_mcp.tools.server_admin", "register_server_admin_tools"),
    "connect": ("unraid_mcp.tools.connect_admin", "register_connect_admin_tools"),
    "auth": ("unraid_mcp.tools.auth", "register_auth_tools"),
    "array-admin": ("unraid_mcp.tools.array_admin", "register_array_admin_tools"),
}
