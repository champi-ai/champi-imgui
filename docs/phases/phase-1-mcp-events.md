# Phase 1: MCP Event Queue

## Goal
MCP clients can register interest in widget events and poll for them, closing the callback gap for LLM-driven UIs.

## Deliverables

### Backend
- [ ] `EventQueue` class (thread-safe, bounded deque) in new `core/events.py` — stores `WidgetEvent(widget_id, event_type, timestamp, payload)`
- [ ] Modify `Widget.trigger_callback()` to also push events to a global EventQueue
- [ ] `subscribe_events` MCP tool — register which widget+event combinations to track
- [ ] `poll_events` MCP tool — return and drain queued events (with optional `widget_id` filter)
- [ ] `get_event_subscriptions` MCP tool — list active subscriptions
- [ ] `unsubscribe_events` MCP tool — remove subscriptions
- [ ] Wire global `EventQueue` instance in `server/main.py` alongside other managers

### Frontend
- [ ] N/A

### Infrastructure
- [ ] Unit tests for EventQueue (push, poll, overflow, filtering)
- [ ] Integration test: create button, subscribe to click, simulate trigger, poll and verify event returned
- [ ] Update existing callback tests if any are affected

## Done Definition
- `subscribe_events(canvas_id, widget_id, events=["click"])` succeeds
- After a widget callback fires, `poll_events()` returns the event with correct widget_id, event_type, and timestamp
- Polling drains the queue — second poll returns empty
- Queue has a configurable max size and drops oldest events on overflow
- All existing tests still pass

## Parallel work
- EventQueue class can be built and tested independently from MCP tool wiring
- MCP tools can be stubbed while EventQueue is under development

## Phase dependencies
- Requires: none (independent of Phase 0, can run in parallel)

## Complexity
- Backend: M
- Frontend: N/A
- Infra: S

## Risks
- Thread safety: EventQueue accessed from render thread (trigger) and MCP thread (poll) — needs lock
- Event volume: rapid widget updates (e.g., slider drag) could flood queue — need throttling or configurable filtering
- Backward compatibility: modifying `trigger_callback()` must not break existing in-process callback behavior
