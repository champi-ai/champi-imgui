# Phase: Prompt Bridge 2 -- Host Window Overlay and Canvas Placement

## Goal
The host window can be configured as a borderless, always-on-top overlay at any screen corner, and canvases respect position and window flags -- enabling the corner-launcher use case from the spec.

## Deliverables

### Backend
- [ ] `core/host_window.py`: `Anchor` enum, `HostWindowConfig` dataclass (title, size, position, anchor, margin, always_on_top, decorated, opacity, resizable), `resolve_position()` against monitor work area, `flags_from_names()` whitelist mapper
- [ ] `core/canvas.py` (`CanvasManager`): `_host_config`, `_host_commands` queue, `_host_applied` event, `configure_host_window()`, `_apply_host_config()` (GLFW calls), `get_host_window_status()` snapshot, `_post_init` applies config before `hello_imgui.run()`
- [ ] `core/canvas.py` (`Canvas._render_frame`): apply `state.position` via `set_next_window_pos`, apply `window_flags` from properties via cached `_flags_from_names`
- [ ] `api/server.py`: `configure_host_window` (async, partial update, waits on `_host_applied`), `get_host_window`
- [ ] `api/server.py`: extend `create_canvas` with `position` and `window_flags` params (validate flags before creation)
- [ ] `api/server.py`: extend `get_canvas_info` to include `host_window` status

### Frontend
- [ ] Canvas renders at specified position with specified window flags (no_title_bar, no_resize, no_move, etc.)
- [ ] Host window appears as configured overlay (tested manually on X11; Wayland limitations documented)

### Infrastructure
- [ ] `tests/test_host_window.py`: `HostWindowConfig` partial update merge, anchor resolution math against fake work area, `flags_from_names` whitelist (valid + unknown raises ValueError), `create_canvas(position, window_flags)` round-trip via to_dict/from_dict
- [ ] Platform notes documented in tool docstrings (Wayland position no-op, macOS floating, shared host window constraint)

## Done Definition
- `configure_host_window(anchor="top_left", margin=8, width=260, height=120, always_on_top=True, decorated=False)` applies without error and `get_host_window` returns matching status
- `create_canvas(..., position=[8,8], window_flags=["no_title_bar","no_resize","no_move"])` creates a canvas that renders at the specified position with flags applied
- Invalid window flag names return a clear error envelope listing allowed flags
- `flags_from_names` unit tests pass for all whitelisted names plus unknown-name rejection
- Wayland: `position_supported=False` reported gracefully, no crash
- All quality gates pass

## Parallel work
- BE: `HostWindowConfig` + `resolve_position` + `flags_from_names` can run alongside BE: `CanvasManager` host command queue integration
- Tests for config math vs. GLFW integration tests are independent

## Phase dependencies
- Requires: Phase Prompt Bridge 1 deliverables (broker wiring in canvas shutdown hooks, server.py structure)

## Complexity
- Backend: L
- Frontend: S
- Infra: M

## Risks
- Wayland: `glfw.set_window_pos` is a no-op; always-on-top is compositor-dependent. Documented, not fixable server-side.
- Shared host window means launcher-sized window hides other canvases. Deliberate MVP constraint.
- GLFW calls must happen on render thread only; command queue pattern enforces this but bugs here cause crashes not exceptions.
