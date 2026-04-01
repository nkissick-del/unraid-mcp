# Stage 1: Builder
FROM python:3.11-slim AS builder
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:0.5.24 /uv /uvx /bin/
COPY pyproject.toml uv.lock README.md ./
COPY unraid_mcp/ ./unraid_mcp/
RUN uv sync --frozen --no-dev

# Stage 2: Runtime
FROM python:3.11-slim

# hadolint ignore=DL3008
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl gosu \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -g 1000 mcp && useradd -u 1000 -g mcp -m mcp

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.5.24 /uv /uvx /bin/
COPY --from=builder /app /app
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Remove base image packages not needed at runtime (uv manages its own venv)
# Also removes wheel/setuptools which may have known vulnerabilities
RUN pip uninstall -y wheel setuptools pip 2>/dev/null; true

RUN mkdir -p /app/logs && chown -R mcp:mcp /app

EXPOSE 6970

ENV PYTHONUNBUFFERED=1
ENV UNRAID_MCP_PORT=6970
ENV UNRAID_MCP_HOST="0.0.0.0"
ENV UNRAID_MCP_TRANSPORT="streamable-http"
ENV UNRAID_API_URL=""
ENV UNRAID_VERIFY_SSL="true"
ENV UNRAID_MCP_LOG_LEVEL="INFO"
ENV UNRAID_MCP_LOG_DIR="/app/logs"
ENV UNRAID_MCP_LOG_FORMAT="text"

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -sf http://localhost:${UNRAID_MCP_PORT:-6970}/health || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["uv", "run", "unraid-mcp-server"]
