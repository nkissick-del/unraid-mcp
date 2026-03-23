# Unraid MCP Plugin for Claude Code

This plugin connects Claude Code to your Unraid server via the GraphQL API, giving Claude the ability to monitor and manage your array, Docker containers, disks, UPS devices, notifications, and more.

## Installation

### Option A: Claude Code Plugin (recommended)

Place this repository where Claude Code can find it and add it as a plugin:

```bash
git clone https://github.com/nkissick-del/unraid-mcp.git
cd unraid-mcp
cp .env.example .env
# Edit .env with your UNRAID_API_URL and UNRAID_API_KEY
```

### Option B: Manual MCP server registration

```bash
claude mcp add unraid -- uv run --directory /path/to/unraid-mcp unraid-mcp-server
```

Set the required environment variables before starting:

```bash
export UNRAID_API_URL="https://<your-unraid-ip>:PORT/graphql"
export UNRAID_API_KEY="your-api-key"
export UNRAID_MCP_TRANSPORT="stdio"
```

## Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `UNRAID_API_URL` | Yes | Unraid GraphQL API endpoint |
| `UNRAID_API_KEY` | Yes | API key for authentication |
| `UNRAID_MCP_TRANSPORT` | No | Transport type (default: `stdio` for plugin usage) |

## What you can do

Once installed, ask Claude to:

- "Show me the array status"
- "List all Docker containers"
- "Check the health of the server"
- "Show disk temperatures"
- "List UPS devices"
- "Get recent notifications"
