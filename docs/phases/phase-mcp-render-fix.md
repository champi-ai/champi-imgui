# Phase: MCP Render Fix

## Goal
Canvas windows created via the MCP server render successfully, with ecosystem-aligned health monitoring and structured error surfacing.

## Deliverables

### Backend
- [ ] Store last render-thread exception on Canvas instance (`_render_error: Exception | None`)
- [ ] Add `is_render_healthy()` method to Canvas: checks `_render_thread.is_alive()` + reports stored exception
- [ ] Emit `RENDER_FRAME` (ImgUIEventTypes=130) via `SignalProcessor` after each rendered frame in `_render_frame()` (ecosystem path only, guarded by `HAS_ECOSYSTEM`)
- [ ] `create_canvas` MCP tool: poll RENDER_FRAME ACK region (2s timeout) before returning success (ecosystem path); fallback to 0.5s sleep (standalone)
- [ ] Add `get_render_error(canvas_id)` MCP tool returning stored render-thread exception
- [ ] Add `get_render_health(canvas_id)` MCP tool returning `thread_alive`, `ack_lag_seconds` (ecosystem), `last_error`
- [ ] RENDER_FRAME struct: `seq_num (Q) + canvas_id (64s)`

### Infrastructure
- [ ] Log `DISPLAY`, `WAYLAND_DISPLAY`, `XDG_SESSION_TYPE`, `LIBGL_ALWAYS_SOFTWARE` at MCP server startup
- [ ] Add diagnostic script `scripts/diagnose_mcp_render.py`: launches MCP server in-process, calls `create_canvas`, waits 3s, reports thread health + RENDER_FRAME ACK lag (ecosystem) + env vars + last_error
- [ ] Document required env vars for systemd/supervisor launchers in script docstring

### Validation
- [ ] Integration test `tests/test_mcp_render.py`: spawn MCP server, call `create_canvas`, call `screenshot_canvas`, assert PNG bytes within 5s
- [ ] Assert `RENDER_FRAME` ACK increments (ecosystem path, skipped when no ecosystem)

## Done Definition
- `create_canvas` via MCP returns success AND the render thread is confirmed alive after 1 second
- `screenshot_canvas` via MCP returns valid PNG data (non-empty, valid header) within 5 seconds of canvas creation
- Render thread crash is surfaced via `get_render_error` (no silent failures)
- `get_render_health` returns `ack_lag_seconds` when ecosystem packages are installed, `null` otherwise
- The diagnostic script runs without error (documents skip for headless-only environments)
- All existing tests continue to pass

## Parallel work
- BE: error surfacing + health check method can run alongside INFRA: env logging + diagnostic script
- BE: `get_render_health` tool can be written alongside RENDER_FRAME signal emission (they share the struct definition but are otherwise independent)
- BE: integration test can be written in parallel with the fix (test defines acceptance gate, fix makes it pass)

## Phase dependencies
- Requires: Phase: IPC Prerequisite (ecosystem extras in pyproject.toml, HAS_ECOSYSTEM guard pattern)

## Complexity
- Backend: M
- Frontend: N/A
- Infra: S

## Risks
- Root cause may be deeper than environment variables (e.g., OpenGL context cannot be created on a daemon thread in some drivers) — may require spawning the render in a subprocess instead of a thread
- Wayland sessions may not support `glfw.get_x11_window()` at all, requiring an alternative screenshot path (already partially addressed by the OpenGL screenshot fallback)
- CI environments are headless — the integration test may need Xvfb or a virtual framebuffer, adding infra complexity
- RENDER_FRAME emission adds per-frame overhead; must be lightweight (single shm write, no allocation)
