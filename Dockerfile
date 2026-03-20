# Stage 1: Builder
FROM python:3.11-slim AS builder
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:0.5.24 /uv /uvx /bin/
COPY pyproject.toml uv.lock README.md ./
COPY unraid_mcp/ ./unraid_mcp/
RUN uv sync --frozen

# Stage 2: Runtime
FROM python:3.11-slim

# hadolint ignore=DL3008
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.5.24 /uv /uvx /bin/
COPY --from=builder /app /app

RUN groupadd -r mcp && useradd -r -g mcp -d /app -s /sbin/nologin mcp \
    && mkdir -p /app/logs \
    && chown -R mcp:mcp /app
USER mcp

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
    CMD curl -f "http://localhost:${UNRAID_MCP_PORT:-6970}/mcp" || exit 1

CMD ["uv", "run", "unraid-mcp-server"]
