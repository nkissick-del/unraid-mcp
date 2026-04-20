# Unraid MCP Server — Justfile
# Run `just` to list available recipes

default:
    @just --list

# ── Development ───────────────────────────────────────────────────────────────

# Start development server (hot-reload via scripts/dev.sh)
dev:
    ./scripts/dev.sh

# Run tests
test:
    uv run pytest tests/ -v

# Run linter (ruff)
lint:
    uv run ruff check unraid_mcp/ tests/

# Format code (ruff)
fmt:
    uv run ruff format unraid_mcp/ tests/

# Type-check (mypy)
typecheck:
    uv run mypy unraid_mcp/

# Build Docker image
build:
    docker build -t unraid-mcp .

# ── Docker Compose ────────────────────────────────────────────────────────────

up:
    docker compose up -d

down:
    docker compose down

restart:
    docker compose restart

logs:
    docker compose logs -f

# Check /health endpoint
health:
    @PORT=$$(grep -E '^UNRAID_MCP_PORT=' .env 2>/dev/null | cut -d= -f2 || echo 6970); \
    curl -sf "http://localhost:$$PORT/health" | python3 -m json.tool || echo "Health check failed"

# ── Setup ─────────────────────────────────────────────────────────────────────

setup:
    @if [ ! -f .env ]; then \
        cp .env.example .env && chmod 600 .env; \
        echo "Created .env from .env.example — fill in your credentials"; \
    else \
        echo ".env already exists"; \
    fi

gen-token:
    @python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# ── Quality Gates ─────────────────────────────────────────────────────────────

check-contract:
    bash scripts/check-docker-security.sh
    bash scripts/check-no-baked-env.sh
    bash scripts/ensure-ignore-files.sh --check
