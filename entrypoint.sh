#!/bin/sh
# Ensure mounted volumes are writable by the mcp user (UID 999)
# On fresh installs, Docker creates bind-mount dirs as root
chown -R mcp:mcp /app/logs 2>/dev/null
chown -R mcp:mcp /app/.cache 2>/dev/null

exec gosu mcp uv run unraid-mcp-server
