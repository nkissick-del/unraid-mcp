#!/bin/sh
set -e

# Fix ownership of bind-mounted directories.
# On Unraid, the Docker UI creates these as nobody:users (99:100) with 755.
# The mcp user (1000:1000) needs write access.
chown -R mcp:mcp /app/logs 2>/dev/null || true

# Drop to non-root user and exec the CMD
exec gosu mcp "$@"
