# Phase: MCP System State Reporter

## Goal
A single MCP tool call returns the full internal state of all champi-imgui subsystems, with ecosystem-aligned IPC for cross-process state queries.

## Deliverables

### Backend
- [ ] New file `src/champi_imgui/signals/manager.py`: `ImgUISignalManager(BaseSignalManager)` wiring blinker signals to ImgUIEventTypes lanes via SignalProcessor (ecosystem path only)
  - `widget_created` -> `WIDGET_CREATE = 120`
  - `widget_updated` -> `WIDGET_CREATE = 120` (update path)
  - `widget_deleted` -> `WIDGET_DELETE = 121`
  - `canvas_updated` -> `CANVAS_UPDATE = 110`
- [ ] Add `QUERY_STATE = 140` and `STATE_RESPONSE = 141` to ImgUIEventTypes in champi-signals (PR to champi-signals repo)
- [ ] Canvas SignalReader subscribes to QUERY_STATE; on receipt serializes `canvas.state.to_dict()` + render diagnostics -> writes to STATE_RESPONSE lane (ecosystem path)
- [ ] `get_canvas_diagnostics(canvas_id)` MCP tool: writes QUERY_STATE, blocks on STATE_RESPONSE (2s timeout); fallback to direct Python attribute reads (standalone)
- [ ] Add `to_diagnostics() -> dict` to each manager (use enum `.value`, no string literals):
  - AnimationManager: `AnimationState.value`, `EasingFunction.value`
  - NotificationManager: `NotificationType.value`
  - LayoutManager: `LayoutMode.value`
  - DataStore: key count, signal path count, per-path receiver counts
  - BindingManager: binding count, paths list
  - TemplateManager: saved template names
  - ThemeManager: current theme name, available theme names
  - EventQueue: `pending_count`, `subscription_count` (direct from internal state)
- [ ] Add `get_system_state` MCP tool with structured response: version, uptime_seconds, canvas_count, canvases, managers, ipc_health (ecosystem only), signals (blinker receiver counts)
- [ ] Add server uptime tracking (start time recorded at module load)
- [ ] Apply `@EventProcessor.emits_event` decorator to high-value manager methods (AnimationManager.start_animation, etc.) when ecosystem is available

### Validation
- [ ] Unit tests for `to_diagnostics()` on each manager with real instances
- [ ] Unit tests for `get_system_state` tool with mocked managers
- [ ] Unit tests for `get_canvas_diagnostics` tool with mocked STATE_RESPONSE
- [ ] Unit tests for ImgUISignalManager wiring (verify `connect_signal` calls)
- [ ] All existing tests continue to pass
- [ ] mypy, ruff check, and ruff format pass

## Done Definition
- `get_system_state` returns a dict with keys: `version`, `uptime_seconds`, `canvas_count`, `canvases`, `managers`, `ipc_health` (ecosystem), `signals`
- `get_canvas_diagnostics(canvas_id)` returns: `canvas_id`, `title`, `size`, `running`, `window_id`, `render_thread_alive`, `widget_count`, `widget_count_by_type`, `pending_screenshot`, `pending_measure_text`, `pending_canvas_info`
- Both tools return `{"success": False, "error": ...}` on invalid input
- `to_diagnostics()` methods use enum `.value` for all enum fields (no string literals)
- ImgUISignalManager correctly bridges blinker signals to champi-signals lanes (verified by unit test)

## Parallel work
- BE: `to_diagnostics()` helpers on AnimationManager, NotificationManager, DataStore, BindingManager, EventQueue can all be written in parallel (independent modules)
- BE: `ImgUISignalManager` can be written in parallel with `to_diagnostics()` helpers
- BE: Unit tests can start as soon as tool signatures are defined (stubs first)

## Phase dependencies
- Requires: Phase: IPC Prerequisite (ecosystem extras, HAS_ECOSYSTEM guard)
- Requires: Phase: MCP Render Fix (RENDER_FRAME heartbeat for ipc_health reporting, `_render_error` for canvas diagnostics)

## Complexity
- Backend: M
- Frontend: N/A
- Infra: N/A

## Risks
- Thread safety: reading `_running`, `_render_thread.is_alive()`, and pending request slots from the MCP thread while the render thread may be mutating them. Mitigation: simple attribute reads on immutable/atomic Python objects; no locking needed for read-only diagnostics.
- AnimationManager.animations dict could be mutated during iteration if an animation completes mid-read. Mitigation: snapshot with `dict(self.animations)` before summarizing.
- QUERY_STATE / STATE_RESPONSE lanes require a champi-signals PR. If that PR is delayed, the standalone fallback (direct Python reads) still delivers full functionality.
- `@EventProcessor.emits_event` decorator may have import-time side effects if ecosystem is not installed. Guard with `HAS_ECOSYSTEM` check.
