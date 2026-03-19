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

## Phase 3: Reliability & Error Handling
- [ ] Fix subscription startup race condition (`resources.py`) — global `_subscriptions_started` not async-safe
- [ ] Add graceful shutdown handlers (`main.py`) — no SIGTERM/SIGINT cleanup
- [ ] Deduplicate WebSocket auth (`manager.py:183-194`) — API key sent 5 ways
- [ ] Replace silent failures with explicit errors — tools return `{}`/`[]` on bad data instead of raising
- [ ] Use specific exception catches instead of bare `except Exception`

## Phase 4: Performance & Infrastructure
- [ ] Dockerfile — multi-stage build, curl healthcheck, `PYTHONUNBUFFERED=1`, persistent logs
- [ ] Fix logging filesystem I/O (`logging.py`) — `os.path.exists` + `os.path.getsize` on every emit
- [ ] Structured/JSON logging option for production
- [ ] Fix CI `pip-audit` (`--no-deps` skips transitive deps)
- [ ] Fix `dev.sh` portability — BSD-only `stat -f%z`

## Phase 5: Polish & Tests
- [ ] Unit tests for GraphQL client, core tools, subscriptions
- [ ] Remaining DRY cleanup
- [ ] Standardize error message format across tools
- [ ] Extract magic numbers/strings to module-level constants

## Notes
- Phase 4 can run in parallel with Phases 2-3
- Phases 1-2 are highest value — address critical perf, security, maintainability
- Write tests last (Phase 5) so they target stable interfaces
