# Codebase Audit - Improvement Plan

> Temporary tracking document. Delete when complete.

## Phase 1: Foundation ✅ (completed 2026-03-20, commit 65254a6)
- [x] HTTP connection pooling (`core/client.py`) — singleton AsyncClient with asyncio.Lock
- [x] Remove dead exception class (`core/exceptions.py`) — `IdempotentOperationError` removed
- [x] Extract shared helpers (`core/utils.py`) — `ensure_dict`, `ensure_list`, `format_bytes`, `format_kb`
- [x] Update tool files to use shared helpers (system, storage, docker, virtualization, rclone)
- [x] Fix temperature 0°C truthiness bug in `storage.py` (CodeRabbit catch)
- [x] Apply black formatting across all files for CI compliance

## Phase 2: Security & Validation ✅ (completed 2026-03-20)
- [x] Harden GraphQL field interpolation (`virtualization.py`, `docker.py`) — dict-based mutation lookup
- [x] Input validation on tool params — `log_file_path`, `offset`/`limit`, `container_id`, `disk_id`, etc.
- [x] Truncate error responses (`client.py`) — `e.response.text` capped at 500 chars
- [x] Add dependency upper bounds (`pyproject.toml`) — all deps capped at `<NEXT_MAJOR`

## Phase 3: Reliability & Error Handling ✅ (completed 2026-03-20)
- [x] Fix subscription startup race condition (`resources.py`) — asyncio.Lock double-check guard
- [x] Add graceful shutdown via FastMCP lifespan (`server.py`) — stop subscriptions + close HTTP client
- [x] Deduplicate WebSocket auth (`manager.py`) — extracted `_build_ws_auth_payload()` helper
- [x] Replace silent failures with explicit warnings — `logger.warning` in rclone, storage, docker tools
- [x] Use specific exception catches instead of bare `except Exception` — narrowed in manager.py and docker.py

## Phase 4: Performance & Infrastructure ✅ (completed 2026-03-20)
- [x] Dockerfile — multi-stage build, curl healthcheck, `PYTHONUNBUFFERED=1`, persistent logs
- [x] Fix logging filesystem I/O (`logging.py`) — counter-based throttling, eliminated redundant stat calls
- [x] Structured/JSON logging option for production — `UNRAID_MCP_LOG_FORMAT=json`
- [x] Fix CI `pip-audit` — temp file instead of process substitution, removed `--no-deps`
- [x] Fix `dev.sh` portability — `stat -f%z` → `wc -c` (POSIX portable)

## Phase 5: Polish & Tests
- [ ] Unit tests for GraphQL client, core tools, subscriptions
- [ ] Remaining DRY cleanup
- [ ] Standardize error message format across tools
- [ ] Extract magic numbers/strings to module-level constants

## Notes
- Phase 4 can run in parallel with Phases 2-3
- Phases 1-2 are highest value — address critical perf, security, maintainability
- Write tests last (Phase 5) so they target stable interfaces
