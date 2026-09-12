VERDICT: APPROVED

## Blocking Issues

None.

All five blocking issues from the prior review have been resolved:

1. `SamplingResult.text` nullability -- Section 5.1 now falls back to `str(result.result)`.
2. `applied_seq` undefined -- Section 1.3 defines `_host_applied: threading.Event` with clear/set semantics; Section 1.6 makes `configure_host_window` async via `await asyncio.to_thread(_host_applied.wait, 1.0)`.
3. GIL reliance undocumented -- Section 2.2 adds an explicit thread-safety note.
4. `create_canvas` extension underspecified -- Section 1.5 now has the full tool signature, validation before creation, and `properties["window_flags"]` storage path.
5. `_flags_from_names` validation location -- Section 1.5 calls it in the tool handler for validation and caches the result on the Canvas instance for the render thread.

## Non-Blocking Issues

1. **`_submit()` calls `trigger_callback("prompt", request.to_dict())` on the render thread** -- `trigger_callback` pushes into `EventQueue`, which holds a `threading.Lock`. The lock is also acquired by `poll_events` on the MCP thread. Contention is low (bounded deque, fast append), but under rapid submit + poll the render thread could stall for the duration of one lock acquisition. Acceptable for the MVP; note for profiling later.

2. **`update_prompt_button` tool excludes `position`, `size`, `parent_id`** -- Section 4.2 says "no position/size/parent_id". The existing generic `update_widget_properties` tool can handle those, but this means there is no single tool to fully reconfigure a prompt button. Consistent with how other widgets work (e.g. `add_button` has no `update_button`), but worth noting if users ask.

3. **`run_prompt_bridge` holds a tool call open for up to 3600 seconds** -- The spec documents this and recommends `timeout_seconds` <= client tool timeout. Stdio clients with short timeouts will silently disconnect. The `report_progress` call each iteration helps keep Streamable HTTP alive, but stdio has no progress channel. Consider adding a note that stdio clients should prefer the long-poll path.

4. **No structured error type on `broker.respond()` exceptions** -- `respond()` raises `KeyError` for unknown IDs and `ValueError` for terminal states. The tool handler catches `Exception` generically. If the broker adds new exception types later, they will be caught by the same blanket handler. Fine for now; just a maintenance note.

5. **`_window_flags_cache` invalidation** -- Section 1.5 says the cache is invalidated "when `properties['window_flags']` changes via `update_canvas_state`". The existing `update_canvas_state` tool only handles `title` and `width/height` via shared memory commands. If `window_flags` is changed via a future `update_canvas_state` extension, the invalidation must be wired in at that point. Not a problem today since no tool currently mutates `window_flags` after creation.

6. **`PromptButtonWidget.__init__` auto-subscribes to `["prompt", "response"]` events** -- If the event queue is not installed yet (e.g. widget created before `set_event_queue` is called), the subscription silently does nothing. In practice `create_mcp_app()` calls `set_event_queue()` before any tool can create widgets, so this is safe. But the guard "when an event queue is installed" (Section 3.3) should be an `if _event_queue is not None:` check, which the implementer needs to remember.

## API Contract Diff

```
-- Host Window --
[new] configure_host_window  -- both specs aligned; params, return shape, async behaviour match
[new] get_host_window        -- both specs aligned

-- Canvas (extended) --
[mod] create_canvas          -- both specs add position + window_flags; backend fully specifies validation and storage
[mod] get_canvas_info        -- both specs add prompt_bridge + host_window keys; backend confirms additive-only

-- Prompt Bridge --
[new] add_prompt_button      -- both specs aligned; frontend updated to include busy_label, submit_on_enter, clear_input_on_submit, response_max_height
[new] update_prompt_button   -- both specs aligned
[new] wait_for_prompt        -- both specs aligned
[new] respond_to_prompt      -- both specs aligned
[new] list_prompt_requests   -- both specs aligned
[new] cancel_prompt_request  -- both specs aligned
[new] run_prompt_bridge      -- both specs aligned
[new] stop_prompt_bridge     -- both specs aligned
[new] ui_prompt_loop (prompt)-- both specs aligned
```

## Data Model Review

No database. In-memory dataclasses only:

```
[ok]  CanvasState        -- position field exists; window_flags in properties dict; round-trips via to_dict/from_dict
[ok]  WidgetState        -- unchanged
[new] HostWindowConfig   -- well-defined dataclass with to_dict(); partial-update merge documented
[new] PromptRequest      -- well-defined dataclass with to_dict(); all 5 statuses have clear transitions
[new] PromptStatus       -- enum with terminal states (ANSWERED, CANCELLED, EXPIRED) explicitly guarded
[new] PromptBroker       -- bounded history, per-widget pending cap, TTL sweep in wait() and submit()
```

## Frontend Architecture Notes

N/A -- no web frontend. The frontend spec correctly describes:
- Visual state table covers all 5 PromptStatus values
- TTL behaviour documented as server-wide broker config, not per-widget
- Flood protection ("Too many pending requests") matches backend `max_pending_per_widget`
- Tool contract table now includes all create-time params for `add_prompt_button`
- `poll_events` visibility via auto-subscription documented

## Backend Architecture Notes

- **Thread model is sound**: render thread owns ImGui/GLFW; MCP tools use `asyncio.to_thread` for blocking broker calls; `configure_host_window` is properly async. No event loop blocking.
- **`_host_applied: threading.Event`** is the correct primitive: simple, no spurious wakeup concerns, and `asyncio.to_thread(event.wait, timeout)` integrates cleanly with the event loop.
- **`_flags_from_names` dual-call pattern** (validate in tool, cache in render) avoids both bad-input-reaching-render-thread and repeated string-to-flag conversion. Clean.
- **`PromptBroker` lifecycle hooks** (`cancel_for_widget`, `cancel_for_canvas`) are wired into `remove_widget` and `shutdown_canvas`. Covers widget removal, canvas shutdown, and full cleanup.
- **`sweep_expired()` in `wait()`** closes the gap where a stale request could be claimed after TTL.
- **`max_pending_per_widget` cap** prevents render-thread flooding from rapid clicks. `submit()` returning `False` with a UI status message is the right feedback path.
- **Sampling bridge `result.text` fallback** to `str(result.result)` handles structured output and None cases.
- **`get_canvas_info` additive extension** preserves backward compatibility for existing callers.

## Recommended Edits

No blocking edits required.
