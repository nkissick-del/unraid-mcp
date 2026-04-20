# syntax=docker/dockerfile:1

# ── Stage 1: Builder (uv base image with uv pre-installed) ──────────────────
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim AS builder

WORKDIR /app

# Install deps (cached layer) — frozen lockfile, no project yet
COPY pyproject.toml uv.lock README.md ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Copy source and install project
COPY unraid_mcp/ ./unraid_mcp/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# ── Stage 2: Runtime ────────────────────────────────────────────────────────
FROM python:3.11-slim-bookworm AS runtime

# hadolint ignore=DL3008
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl gosu \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user (matches Unraid defaults)
RUN groupadd -g 1000 mcp && useradd -u 1000 -g mcp -m mcp

WORKDIR /app

# Copy venv and source from builder; re-copy project metadata fresh from host
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/unraid_mcp /app/unraid_mcp
COPY pyproject.toml uv.lock README.md /app/
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Remove base-image pip/setuptools/wheel. The runtime uses /app/.venv directly
# and these packages can pull in known CVEs (e.g. wheel, jaraco.context)
# that Trivy flags as CRITICAL/HIGH.
RUN pip uninstall -y wheel setuptools pip 2>/dev/null || true

# Ensure venv bin is on PATH so `unraid-mcp-server` resolves without uv
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UNRAID_MCP_PORT=6970 \
    UNRAID_MCP_HOST="0.0.0.0" \
    UNRAID_MCP_TRANSPORT="streamable-http" \
    UNRAID_API_URL="" \
    UNRAID_VERIFY_SSL="true" \
    UNRAID_MCP_LOG_LEVEL="INFO" \
    UNRAID_MCP_LOG_DIR="/app/logs" \
    UNRAID_MCP_LOG_FORMAT="text"

# Pre-create log dir with mcp ownership
RUN mkdir -p /app/logs && chown -R mcp:mcp /app

EXPOSE 6970

# NOTE: intentionally no `USER mcp` here — entrypoint.sh starts as root to
# chown bind-mounted /app/logs, then drops to mcp via gosu. This is required
# for Unraid deployments with security_opt: no-new-privileges:true.
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -sf "http://localhost:${UNRAID_MCP_PORT:-6970}/health" || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["unraid-mcp-server"]
