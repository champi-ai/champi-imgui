# Backend Specification: Finish champi-imgui + Ecosystem Integration

## Project Overview

champi-imgui (v1.16.1) is an ImGui-based MCP server and UI framework for LLM-driven UI generation. It is part of the champi-ai ecosystem:

- **champi-ipc** (v0.1.0) — generic POSIX shared-memory IPC, one shm lane per `IntEnum` value
- **champi-signals** (v0.1.0) — blinker wrapper, `BaseSignalManager`, `EventProcessor` decorators, `ImgUIEventTypes(IntEnum)`
- **champi-stt** — multi-provider STT, already uses champi-signals
- **champi-tts** — multi-provider TTS, already uses champi-signals
- **champi-imgui** — NOT yet using champi-ipc/champi-signals (uses hand-rolled single-channel IPC)

Existing open milestones: Phase: MCP Render Fix (#15) and Phase: MCP System State Reporter (#16).

---

## Section 1: Prerequisite — IPC Internal Cleanup

### 1.1 Split UPDATE_STATE command

**Problem**: `CommandType.UPDATE_STATE = 3` encodes title + width + height in a single struct with defaults `width=800, height=600`. A title-only update silently resets canvas size.

**Fix**: Split into two minimal commands:
- `UPDATE_TITLE = 3` — struct: `seq_num + cmd_type + canvas_id + title`
- `UPDATE_SIZE = 4` — struct: `seq_num + cmd_type + canvas_id + width + height`
- `SHUTDOWN` moves from 4 → 5

**Files**: `ipc/command_types.py`, `ipc/structs.py`, `core/canvas.py`, `server/main.py`

### 1.2 Add optional ecosystem extras

```toml
[project.optional-dependencies]
ecosystem = [
    "champi-signals @ ../champi-signals",
    "champi-ipc @ ../champi-ipc",
]
```

Standalone fallback pattern in all ecosystem-aware modules:
```python
try:
    from champi_signals import BaseSignalManager
    from champi_ipc.core.signal_processor import SignalProcessor
    HAS_ECOSYSTEM = True
except ImportError:
    HAS_ECOSYSTEM = False
```

---

## Section 2: Phase A — MCP Render Fix (Ecosystem-Aligned)

### Problem
Canvas windows created via the MCP server never render. The render thread starts but `hello_imgui.run()` silently fails because `DISPLAY` / `XAUTHORITY` env vars are not propagated to the MCP server process. The existing `_render_thread.is_alive()` check does not detect a non-rendering render thread.

### 2.1 RENDER_FRAME heartbeat lane

`ImgUIEventTypes.RENDER_FRAME = 130` is already defined in champi-signals.

- In `core/canvas.py`, `_render_frame()` (the hello_imgui show_gui callback): emit `RENDER_FRAME` via `SignalProcessor` after each rendered frame (when `HAS_ECOSYSTEM`)
- Struct for RENDER_FRAME lane: `seq_num (Q) + canvas_id (64s)`
- MCP server's `SignalReader` subscribes to RENDER_FRAME per canvas; ACK lag > 2s threshold → render dead
- `create_canvas` polls RENDER_FRAME ACK region (2s timeout) before returning success

Standalone fallback (no ecosystem): `create_canvas` returns after 0.5s sleep (existing behavior).

### 2.2 Env var propagation

- Log `DISPLAY`, `WAYLAND_DISPLAY`, `XDG_SESSION_TYPE`, `LIBGL_ALWAYS_SOFTWARE` at MCP server startup
- Document required env vars for systemd/supervisor launchers

### 2.3 Error surfacing

- Store last render-thread exception on Canvas instance (`_render_error: Exception | None`)
- `get_render_error(canvas_id)` MCP tool returns stored exception for a given canvas
- `get_render_health(canvas_id)` MCP tool reports: `thread_alive`, `ack_lag_seconds` (ecosystem), `last_error`

### 2.4 Diagnostic script

`scripts/diagnose_mcp_render.py`:
- Launches MCP server in-process
- Calls `create_canvas`, waits 3s
- Reports: thread health, RENDER_FRAME ACK lag (ecosystem), env vars, last_error

### 2.5 Integration test

`tests/test_mcp_render.py`:
- Spawn MCP server, call `create_canvas`, call `screenshot_canvas`, assert PNG bytes within 5s
- Assert `RENDER_FRAME` ACK increments (ecosystem path)

---

## Section 3: Phase B — MCP System State Reporter (Ecosystem-Aligned)

### 3.1 ImgUISignalManager

New file: `src/champi_imgui/signals/manager.py`

```python
from champi_signals import BaseSignalManager
from champi_signals.enums import ImgUIEventTypes

class ImgUISignalManager(BaseSignalManager):
    ...
```

Wire existing blinker signals to ImgUIEventTypes lanes via SignalProcessor:
- `widget_created` → `WIDGET_CREATE = 120`
- `widget_updated` → `WIDGET_CREATE = 120` (update path)
- `widget_deleted` → `WIDGET_DELETE = 121`
- `canvas_updated` → `CANVAS_UPDATE = 110`

### 3.2 QUERY_STATE / STATE_RESPONSE lanes

Add to `ImgUIEventTypes` in `../champi-signals/src/champi_signals/enums.py`:
```python
QUERY_STATE    = 140   # MCP → Canvas: request state snapshot
STATE_RESPONSE = 141   # Canvas → MCP: deliver state snapshot
```

- Canvas `SignalReader` subscribes to `QUERY_STATE`; on receipt serialises `canvas.state.to_dict()` + render diagnostics → writes to `STATE_RESPONSE` lane
- `get_canvas_diagnostics(canvas_id)` writes QUERY_STATE, blocks on STATE_RESPONSE (2s timeout)
- Fallback (no ecosystem): direct Python attribute reads on Canvas (existing behavior)

### 3.3 Manager `to_diagnostics()` helpers

Add `to_diagnostics() -> dict` to each manager. Must use enum `.value` (no string literals):
- `AnimationManager`: `AnimationState.value`, `EasingFunction.value`
- `NotificationManager`: `NotificationType.value`
- `LayoutManager`: `LayoutMode.value`
- `DataStore`: key count, signal path count, per-path receiver counts
- `BindingManager`: binding count, paths list
- `TemplateManager`: saved template names
- `ThemeManager`: current theme name, available theme names
- `EventQueue`: `pending_count`, `subscription_count` (direct from internal state)

### 3.4 `get_system_state` MCP tool

Response shape:
```python
{
    "success": True,
    "data": {
        "version": "1.16.1",
        "uptime_seconds": 142.7,
        "canvas_count": 2,
        "canvases": [...],           # from STATE_RESPONSE lanes (ecosystem) or Python reads
        "managers": {
            "animations": {...},
            "data_store": {"key_count": N, "signal_paths": [...]},
            "bindings": {"binding_count": N, "paths": [...]},
            "notifications": {"queued_count": N, "recent": [...]},
            "layout": {"mode": "free"},
            "templates": {"saved": [...]},
            "themes": {"current": "dark", "available": [...]}
        },
        "ipc_health": {              # only when HAS_ECOSYSTEM
            "render_frame_ack_lag": {...},
            "widget_create_queue_depth": N
        },
        "signals": {                 # blinker receiver counts
            "widget_created": N,
            "widget_updated": N,
            "canvas_updated": N
        }
    }
}
```

### 3.5 `get_canvas_diagnostics` MCP tool

Response shape:
```python
{
    "success": True,
    "data": {
        "canvas_id": "main",
        "title": "Main Canvas",
        "size": [800, 600],
        "running": True,
        "window_id": 12345678,
        "render_thread_alive": True,
        "widget_count": 12,
        "widget_count_by_type": {"ButtonWidget": 3, "TextWidget": 5},
        "pending_screenshot": False,
        "pending_measure_text": False,
        "pending_canvas_info": False
    }
}
```

### 3.6 `@EventProcessor.emits_event` on manager methods

Apply to high-value manager methods:
```python
from champi_signals.processors import EventProcessor

class AnimationManager:
    @EventProcessor.emits_event(data=["animations"])
    def start_animation(self, ...): ...
```

### 3.7 Unit tests

- `to_diagnostics()` on each manager with mocked/real instances
- `get_system_state` tool with mocked managers
- `get_canvas_diagnostics` tool with mocked STATE_RESPONSE
- ImgUISignalManager wiring (verify `connect_signal` calls)

---

## Section 4: Phase C — champi-ai-cli Foundation

### Vision

champi-ai-cli is the agnostic AI orchestration layer that ties the champi ecosystem together. It is NOT an MCP wrapper — it is an edge-first, model-agnostic framework that removes the constraints of current LLM systems:

- **Programs as persistent actors**: A running champi-imgui canvas IS the program. Identity (canvas_id) survives sessions. The meta-system definition (lane topology, widget schemas, data bindings) is the durable artifact.
- **Interface discovery over interface description**: Actors publish their capabilities via lanes. The orchestrator discovers what's running, not what was described.
- **No context-window-as-only-state-store**: State lives in POSIX shm, in running processes, in canvas widget registries — not in LLM memory.
- **MCP as compatibility adaptor**: champi-imgui's MCP server exists to show integration with existing LLM tooling, not as the primary integration path.

### 4.1 CLI entry point

Package: `champi-ai-cli`
Module: `champi_ai_cli`

```
champi-cli start      # Start all champi services (imgui, stt, tts) with shared signal manager
champi-cli status     # Query all running actors via their RENDER_FRAME / health lanes
champi-cli discover   # Print all active lane registrations
champi-cli canvas     # Open an imgui canvas with champi-signals wired
```

### 4.2 Orchestrator actor

`champi_ai_cli/orchestrator.py`:
- `ChampiOrchestrator`: subscribes to all ImgUIEventTypes lanes, all STT event lanes, all TTS event lanes
- Dispatches events to registered handlers (model adapters)
- Maintains session state: which canvases are open, which STT/TTS streams are active
- Exposes a simple `on_event(event_type, handler)` API for model adapters

### 4.3 Model adapter interface

```python
class ModelAdapter(ABC):
    async def on_tool_call_start(self, event: ToolCallEvent) -> None: ...
    async def on_canvas_update(self, event: CanvasUpdateEvent) -> None: ...
    async def on_speech(self, text: str) -> None: ...
    async def respond(self, text: str) -> None: ...
```

Built-in adapters: `ClaudeAdapter` (uses Anthropic SDK), `OpenAIAdapter`.

### 4.4 Jarvis demo

`examples/jarvis_demo.py`:
- Starts champi-imgui canvas with a chat UI
- Starts champi-stt with WhisperLive backend
- Starts champi-tts with Kokoro backend
- Wires everything via ChampiOrchestrator + ClaudeAdapter
- Wake word "hey champi" → STT active → LLM response → TTS speaks + canvas updates

### 4.5 Package structure

```
src/champi_ai_cli/
├── __init__.py
├── cli.py                   # Click CLI entry points
├── orchestrator.py          # ChampiOrchestrator
├── adapters/
│   ├── __init__.py
│   ├── base.py              # ModelAdapter ABC
│   ├── claude.py            # ClaudeAdapter
│   └── openai.py            # OpenAIAdapter (stub)
└── examples/
    └── jarvis_demo.py
```

---

## API Contracts (Section 7 — for spec-backend alignment)

### New MCP tools

| Tool | Input | Output |
|------|-------|--------|
| `get_render_health(canvas_id)` | `canvas_id: str` | `{thread_alive, ack_lag_seconds, last_error}` |
| `get_render_error(canvas_id)` | `canvas_id: str` | `{error: str \| null}` |
| `get_system_state()` | none | structured dict (see §3.4) |
| `get_canvas_diagnostics(canvas_id)` | `canvas_id: str` | structured dict (see §3.5) |

### Modified MCP tools

| Tool | Change |
|------|--------|
| `update_canvas_state` | Uses UPDATE_TITLE or UPDATE_SIZE command, never combined |
| `create_canvas` | Waits for RENDER_FRAME ACK before returning success (ecosystem path) |

### New signals (champi-signals)

| Signal | Value | Direction |
|--------|-------|-----------|
| `QUERY_STATE` | 140 | MCP → Canvas |
| `STATE_RESPONSE` | 141 | Canvas → MCP |
