# Phase: FastMCP 3.2 Compatibility

## Goal
Upgrade champi-imgui from FastMCP 2.x to 3.2, fixing all internal API breakages in tests and ensuring the full test suite passes against the new version.

## Deliverables

### Backend
- [ ] Bump `fastmcp` dependency from `>=2.12.0` to `>=3.2.0` in `pyproject.toml`
- [ ] Update test helper `_Server.__getattr__` to use `mcp._local_provider._components` (replaces `mcp._tool_manager._tools`)
- [ ] Update `test_integration_canvas.py` tool lookup to use `_local_provider._components` with `tool:{name}@` key format
- [ ] Update `test_system_state.py` tool lookup pattern
- [ ] Update `test_create_canvas_health_poll.py` tool lookup pattern
- [ ] Update all remaining test files using the old `_tool_manager` internal API (11 files total)
- [ ] Run `uv lock` to regenerate lockfile with FastMCP 3.2 dependency tree

### Frontend
- [ ] N/A

### Infrastructure
- [ ] Verify CI passes with new dependency versions
- [ ] Add `[project.optional-dependencies] ecosystem` group to `pyproject.toml` with `champi-signals` and `champi-ipc` (deferred from IPC Prerequisite phase)

## Done Definition
- `uv run pytest` passes with zero failures against FastMCP 3.2
- `uv run ruff check src/ tests/` passes
- `uv run mypy src/` passes
- No references to `_tool_manager._tools` remain in the test suite
- `fastmcp>=3.2.0` is the declared minimum in `pyproject.toml`
- `uv.lock` is committed and consistent

## Parallel work
- N/A (single-track: all changes are test compatibility fixes for the same API migration)

## Phase dependencies
- Requires: Phase 1 (API Factory) — tests already use `create_mcp_app()` pattern

## Complexity
- Backend: S
- Frontend: N/A
- Infra: S

## Risks
- FastMCP 3.x may have additional breaking changes beyond `_tool_manager` removal (e.g., lifespan hooks, tool registration API)
- The `_local_provider._components` path is still a private API — future FastMCP releases may break it again
- Downstream consumers pinning `fastmcp<3` would conflict with champi-imgui's new minimum
