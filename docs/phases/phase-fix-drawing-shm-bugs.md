# Phase: Drawing & SHM Bug Fix

## Goal
Ship fixes for both #181 (DrawingWidget not rendering) and #182 (SharedMemory crash on macOS), with regression tests that prevent recurrence.

## Deliverables

### Backend
- [ ] Fix DrawingWidget rendering (#181): address draw list ordering, clipping rect, and/or render-wake issues identified in the spike diagnosis
- [ ] Ensure canvas_updated signal fires when strokes/shapes/annotations are mutated via MCP tools (add_stroke, add_shape, add_annotation)
- [ ] Fix SharedMemory lifecycle on macOS (#182): unlink before close, register with resource_tracker correctly, add atexit cleanup handler
- [ ] Handle the FileExistsError path in create_regions() so that attaching to a stale region does not double-register with resource_tracker
- [ ] Add regression test for #181: create DrawingWidget, add shapes via add_shape(), verify shapes list is populated and render() does not raise
- [ ] Add regression test for #181: create DrawingWidget, add strokes programmatically, verify strokes are stored and retrievable via get_strokes_by_author()
- [ ] Add regression test for #182: create and cleanup SharedMemoryManager, verify no leaked shm regions (check /dev/shm on Linux, shm_open namespace on macOS)
- [ ] Add regression test for #182: create SharedMemoryManager, force-kill without cleanup(), verify atexit handler prevents resource_tracker warnings on re-create

### Frontend
- [ ] N/A (no web frontend)

### Infrastructure
- [ ] Add macOS to CI matrix if not already present (needed to prevent #182 regressions)

## Done Definition
- DrawingWidget renders strokes, shapes, and annotations visually when added via MCP tools (verified by screenshot_canvas or manual inspection)
- canvas_updated signal count is non-zero after widget mutations
- create_canvas on macOS (Apple Silicon, Python 3.13) does not trigger resource_tracker warnings or process termination
- SharedMemory regions are fully cleaned up on normal shutdown and on abnormal exit (SIGTERM, SIGINT)
- All new regression tests pass on both Linux and macOS
- Existing test suite continues to pass (uv run pytest)
- Linting and type checking pass (uv run ruff check src/ && uv run mypy src/)

## Parallel work
- DrawingWidget fix (#181) can run in parallel with SharedMemory fix (#182) -- completely independent subsystems (widgets/drawing.py vs ipc/shared_memory_manager.py)
- Regression tests for each fix can be written alongside the fix itself

## Phase dependencies
- Requires: Phase: Drawing & SHM Bug Spike (root cause and fix approach must be confirmed before implementation)

## Complexity
- Backend: M (two targeted fixes with clear scope, plus regression tests)
- Frontend: N/A
- Infra: S (CI matrix addition if needed)

## Risks
- macOS SharedMemory behavior differs between Python 3.12 and 3.13 -- fix must be tested on the specific version from the bug report
- DrawingWidget fix may require changes to the Canvas render loop (process_commands timing) if the issue is a render-wake problem rather than draw list ordering
- imgui-bundle add_polyline API may have platform-specific behavior that affects the fix
- atexit handlers do not run on SIGKILL -- document this as a known limitation
