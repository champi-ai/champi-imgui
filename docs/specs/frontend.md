# Frontend Specification: Prompt Bridge

champi-imgui has no web frontend. The "frontend" is (a) the ImGui canvas rendered inside the
shared host window on the user's desktop and (b) the MCP tool surface consumed by the model
client. This document fixes the user-facing behaviour and the tool contract; implementation
detail is in `docs/specs/backend.md`.

## 1. User-facing behaviour

### 1.1 Corner launcher

- The host window can be placed in a screen corner, borderless, always on top, at a small
  fixed size. It stays above other application windows and does not steal focus when the
  model updates it.
- Inside it, a canvas with no title bar shows a **prompt button** and optionally a single-line
  text field.
- Pressing the button (or Enter in the field) sends a prompt. The button shows a busy label
  and is disabled until a response arrives or the request is cancelled.
- The response appears under the button as wrapped text with a small **Clear** control.
  If the response is longer than the configured height, the area scrolls.
- If the model never answers, the request expires after a server-wide TTL (broker
  `ttl_seconds`, default 10 minutes) and the button re-enables. Nothing is lost silently:
  the request is still listed as `expired`.
- Rapid repeated presses are capped at a few pending requests per widget; beyond that the
  widget shows "Too many pending requests" until one is answered or expires.

### 1.2 Inside a normal canvas

The same widget works inside any existing canvas (dashboards, forms), with `input_mode`
`none`, `inline`, or `multiline`. It can be a child of container widgets like every other
widget (`parent_id`).

### 1.3 Visual states

| state | button label | button enabled | response area |
|---|---|---|---|
| idle | `label` | yes | last response or hidden |
| pending / claimed | `busy_label` | no (unless `allow_concurrent`) | unchanged |
| answered | `label` | yes | new response |
| cancelled / expired | `label` | yes | status line "Request cancelled" / "Request expired" (disabled text colour) |

## 2. Model-facing workflow

Two ways to receive prompts; both always available.

1. **Long poll** — call `wait_for_prompt` in a loop, act, call `respond_to_prompt`.
2. **Sampling bridge** — call `run_prompt_bridge` once; the server forwards each prompt to
   the client via MCP sampling and writes the answer back. Only on clients that advertise
   the sampling capability; otherwise the tool returns an error pointing to option 1.

`poll_events` also sees `prompt` and `response` events for `prompt_button` widgets without
an explicit `subscribe_events` call.

## 3. Tool contract (Section 7 — API Contract)

| tool | params | returns (`data`) |
|---|---|---|
| `configure_host_window` | title?, width?, height?, x?, y?, anchor?, margin?, always_on_top?, decorated?, opacity?, resizable? | host window status dict, `applied`, `position_supported` |
| `get_host_window` | — | host window status dict |
| `create_canvas` (extended) | + `position: [x,y]?`, `window_flags: [str]?` | canvas state |
| `add_prompt_button` | canvas_id, widget_id, label, prompt, input_mode, input_hint, show_response, allow_concurrent, busy_label, submit_on_enter, clear_input_on_submit, response_max_height, metadata?, position?, size?, parent_id? | widget dict |
| `update_prompt_button` | canvas_id, widget_id, any prop?, response? | widget dict |
| `wait_for_prompt` | timeout_seconds=25, canvas_id? | `{request}` or `{request: null, timed_out: true}` |
| `respond_to_prompt` | request_id, response, status="answered" | request dict |
| `list_prompt_requests` | status?, canvas_id?, limit=50 | `{requests, count, pending}` |
| `cancel_prompt_request` | request_id | request dict |
| `run_prompt_bridge` | max_requests=0, timeout_seconds=300, system_prompt?, canvas_id?, max_tokens=1024 | `{handled, stopped_by}` |
| `stop_prompt_bridge` | session_id? | `{stopped: n}` |
| `get_canvas_info` (extended) | canvas_id | + `prompt_bridge`, `host_window` |
| prompt `ui_prompt_loop` | — | instruction text for the loop |

`PromptRequest` dict shape (used by `wait_for_prompt`, `respond_to_prompt`,
`list_prompt_requests`, `cancel_prompt_request`):

```json
{
  "request_id": "hex",
  "canvas_id": "launcher",
  "widget_id": "ask",
  "prompt": "The user pressed the launcher and typed: fix my build",
  "user_input": "fix my build",
  "created_at": 1757548800.0,
  "status": "claimed",
  "claimed_at": 1757548801.2,
  "response": null,
  "responded_at": null,
  "metadata": {}
}
```

All tools use the existing envelope `{"success": true, "data": {...}}` /
`{"success": false, "error": "..."}`.

## 4. Documentation deliverables

- README: "Corner launcher" quick start (the exact 4-step example from backend spec §8).
- `docs/MCP_TOOLS_API.md`: new sections for Host Window and Prompt Bridge tools.
- `docs/WIDGET_CATALOG.md`: `prompt_button` entry with the visual state table above.
