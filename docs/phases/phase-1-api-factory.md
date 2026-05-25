# Phase 1: Directory Restructure + API Factory

## Goal
Replace module-level globals with a `create_mcp_app()` factory in a renamed `api/` directory, enabling dependency injection and proper cleanup via FastMCP lifespan.

## Deliverables

### Backend
- [ ] Rename `src/champi_imgui/server/` to `src/champi_imgui/api/`
- [ ] Rename `main.py` to `server.py` inside the new `api/` directory
- [ ] Implement `create_mcp_app(**overrides) -> FastMCP` factory function
- [ ] All 9 managers instantiated as locals inside the factory (not module globals)
- [ ] All 70+ `@mcp.tool()` definitions as closures capturing local manager refs
- [ ] FastMCP lifespan context manager calling `canvas_manager.cleanup()` on shutdown
- [ ] `api/__init__.py` exports `create_mcp_app`
- [ ] Remove old `server/` directory entirely (no leftover files)

### Frontend
- [ ] N/A

### Infrastructure
- [ ] Update any internal imports referencing `champi_imgui.server` to `champi_imgui.api`

## Done Definition
- `from champi_imgui.api import create_mcp_app` resolves without error
- `create_mcp_app()` returns a FastMCP instance with all tools registered
- `create_mcp_app(canvas_manager=mock)` injects the mock successfully
- No module-level manager globals exist in `api/server.py`
- `ruff check src/` passes
- `mypy src/` passes
- `uv run pytest` passes (existing tests may need import path updates)

## Parallel work
- N/A (single-track: this phase is backend-only structural change)

## Phase dependencies
- Requires: none

## Complexity
- Backend: L
- Frontend: N/A
- Infra: S

## Risks
- Circular import issues when moving 70+ tool closures into a single factory
- Performance regression from closure overhead (unlikely but measurable)
- Missed import references in CLI or tests pointing to old `server.main` path
