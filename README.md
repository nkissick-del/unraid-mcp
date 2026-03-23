# Unraid MCP Server

[![CI](https://github.com/nkissick-del/unraid-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/nkissick-del/unraid-mcp/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

An MCP (Model Context Protocol) server that gives AI assistants full visibility and control over an Unraid server via its GraphQL API. Connect it to Claude Code, Claude Desktop, or any MCP-compatible client.

## What it does

- **Monitor** — system info, CPU/RAM/temps, array health, disk SMART data, UPS status, Docker containers, notifications, logs
- **Manage** — start/stop containers, update images, manage plugins, control parity checks, array operations
- **Query** — raw GraphQL escape hatch for anything not covered by dedicated tools
- **129 tools** across 26 modules, organized into three tiers

## Quick Start

### Pull and run (recommended)

```bash
docker run -d \
  --name unraid-mcp \
  -p 6970:6970 \
  -e UNRAID_API_URL=https://YOUR-UNRAID-IP/graphql \
  -e UNRAID_API_KEY=YOUR-API-KEY \
  -e UNRAID_VERIFY_SSL=false \
  --security-opt no-new-privileges:true \
  --cap-drop ALL \
  -v /mnt/user/appdata/unraid-mcp/logs:/app/logs \
  ghcr.io/nkissick-del/unraid-mcp:latest
```

### Unraid Community Applications

Copy `unraid-mcp.xml` to `/boot/config/plugins/dockerMan/templates-user/` on your Unraid server, then add the container through the Docker UI.

### Docker Compose

```yaml
services:
  unraid-mcp:
    image: ghcr.io/nkissick-del/unraid-mcp:latest
    container_name: unraid-mcp
    restart: unless-stopped
    ports:
      - "6970:6970"
    environment:
      - UNRAID_API_URL=https://YOUR-UNRAID-IP/graphql
      - UNRAID_API_KEY=YOUR-API-KEY
      - UNRAID_VERIFY_SSL=false
      - UNRAID_MCP_ENABLED_MODULES=default
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    volumes:
      - /mnt/user/appdata/unraid-mcp/logs:/app/logs
```

## Connecting to Claude

### Claude Code

```bash
claude mcp add --transport http unraid http://YOUR-UNRAID-IP:6970/mcp --scope user
```

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "unraid": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "http://YOUR-UNRAID-IP:6970/mcp", "--allow-http"]
    }
  }
}
```

## Module Tiers

Control which tools are loaded via `UNRAID_MCP_ENABLED_MODULES`:

| Tier | Tools | Modules | Best for |
|------|-------|---------|----------|
| `default` | 32 | system, docker, storage, health, api, system-extra, metrics, ups | Daily monitoring, low token overhead |
| `extended` | 78 | default + notifications, plugins, parity, customization, connect, docker-admin, docker-batch, array, rclone, diagnostics | Full management |
| `all` | 129 | extended + auth, server-admin, array-admin, vms, onboarding, docker-organize, ups-admin, subscriptions | Everything including admin operations |

Mix presets with individual modules:

```bash
UNRAID_MCP_ENABLED_MODULES=default,plugins,auth
UNRAID_MCP_ENABLED_MODULES=extended,server-admin
```

## Tools

### Default Tier (32 tools)

**System** — `get_system_info`, `get_array_status`, `get_network_config`, `get_registration_info`, `get_connect_settings`, `get_unraid_variables`, `manage_docker_container`

**Docker** — `list_docker_containers`, `get_docker_container_details`, `get_docker_container_logs`

**Storage** — `get_shares_info`, `list_physical_disks`, `get_disk_details`, `list_available_log_files`, `get_logs`, `get_notifications_overview`, `list_notifications`

**Monitoring** — `get_system_metrics`, `get_system_time`, `get_timezone_options`, `get_parity_history`, `health_check`, `is_server_online`, `get_config_status`, `get_flash_info`, `get_services`, `get_servers`

**UPS** — `list_ups_devices`, `get_ups_device`, `get_ups_configuration`

**API** — `query_unraid_api`, `introspect_schema`

### Extended Tier (adds 46 tools)

**Docker Admin** — `remove_docker_container`, `update_docker_container`, `update_docker_containers`, `update_all_docker_containers`, `update_docker_autostart`

**Notifications** — `archive_notification`, `archive_all_notifications`, `delete_notification`, `delete_archived_notifications`, `create_notification`, `archive_notifications`, `notify_if_unique`, `unread_notification`, `unarchive_notifications`, `unarchive_all_notifications`, `recalculate_notification_overview`

**Plugins** — `list_plugins`, `list_installed_unraid_plugins`, `get_plugin_install_operation`, `list_plugin_install_operations`, `add_plugin`, `remove_plugin`, `install_plugin`

**Customization** — `get_display_settings`, `get_current_user`, `get_owner_info`, `get_customization`, `get_public_theme`, `set_theme`, `set_locale`

**Connect** — `get_connect_info`, `get_remote_access`, `get_cloud_info`, `update_api_settings`, `connect_sign_in`, `connect_sign_out`, `setup_remote_access`, `enable_dynamic_remote_access`

**Array & Parity** — `manage_array`, `manage_parity_check`

**RClone** — `list_rclone_remotes`, `get_rclone_config_form`, `create_rclone_remote`, `delete_rclone_remote`

**Diagnostics** — `diagnose_subscriptions`, `test_subscription_query`

### All Tier (adds 51 tools)

Auth (13), Server Admin (6), Array Admin (6), Onboarding (11), Docker Organize (11), VMs (3), UPS Admin (1)

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `UNRAID_API_URL` | *(required)* | Unraid GraphQL endpoint (e.g. `https://192.168.1.101/graphql`) |
| `UNRAID_API_KEY` | *(required)* | API key from Settings > Management Access > API |
| `UNRAID_MCP_ENABLED_MODULES` | `default` | Module tier: `default`, `extended`, `all`, or comma-separated list |
| `UNRAID_MCP_TRANSPORT` | `streamable-http` | Transport: `streamable-http`, `sse`, `stdio` |
| `UNRAID_MCP_PORT` | `6970` | Server port |
| `UNRAID_MCP_HOST` | `0.0.0.0` | Bind address |
| `UNRAID_MCP_LOG_LEVEL` | `INFO` | Log level: `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `UNRAID_VERIFY_SSL` | `true` | SSL verification: `true`, `false`, or CA bundle path |

## Development

```bash
# Setup
git clone https://github.com/nkissick-del/unraid-mcp
cd unraid-mcp
uv sync --extra dev

# Quality gates
uv run black unraid_mcp/ tests/
uv run ruff check unraid_mcp/ tests/
uv run mypy unraid_mcp/
uv run pytest

# Run locally
uv run unraid-mcp-server
```

### Project Structure

```
unraid_mcp/
├── main.py                  # Entry point
├── server.py                # FastMCP server setup
├── registry.py              # Module registry
├── config/
│   ├── settings.py          # Environment & module gating
│   ├── logging.py           # Structured logging
│   └── logging_handlers.py  # File handlers & filters
├── core/
│   ├── client.py            # GraphQL HTTP client
│   ├── constants.py         # Shared constants
│   ├── decorators.py        # Tool error handler
│   ├── exceptions.py        # ToolError, ValidationError
│   ├── types.py             # SubscriptionData
│   ├── utils.py             # Helpers (confirm gates, formatting)
│   └── validation.py        # Input validators
├── subscriptions/
│   ├── configs.py           # 16 subscription definitions
│   ├── manager.py           # WebSocket lifecycle
│   ├── resources.py         # MCP resource providers
│   └── diagnostics.py       # Subscription testing tools
└── tools/
    ├── queries/             # GraphQL query definitions (14 files)
    ├── system.py            # System info (7 tools)
    ├── docker.py            # Docker containers (4 tools)
    ├── storage.py           # Shares, disks, logs (7 tools)
    ├── health.py            # Health check (1 tool)
    ├── api.py               # Raw GraphQL + introspection (2 tools)
    ├── system_extra.py      # Config, flash, services (5 tools)
    ├── metrics_tools.py     # CPU/RAM/temp metrics (3 tools)
    ├── ups_tools.py         # UPS monitoring (3 tools)
    └── ... (17 more modules)
```

### 501 unit tests, CI with lint + type check + security scan + container scan.

## License

MIT — see [LICENSE](LICENSE).
