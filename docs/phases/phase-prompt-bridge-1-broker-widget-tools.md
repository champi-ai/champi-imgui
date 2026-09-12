# Phase: Prompt Bridge 1 -- Broker, Widget, and Long-Poll Tools

## Goal
A prompt button widget inside any canvas can collect user input, deliver it to the model via long-poll tools, and display the response -- the core request/response loop works end-to-end except for host window placement.

## Deliverables

### Backend
- [ ] `core/prompt_bridge.py`: `PromptStatus`, `PromptRequest`, `PromptBroker` (submit, wait, respond, cancel, list, sweep, diagnostics, response callbacks)
- [ ] `core/widget.py`: `set_prompt_broker()` module-level hook (mirrors existing `set_event_queue`)
- [ ] `api/server.py`: broker instantiation, `set_prompt_broker` wiring, factory registration of `prompt_button`
- [ ] `api/server.py`: `add_prompt_button`, `update_prompt_button`, `wait_for_prompt` (async long-poll via `asyncio.to_thread`), `respond_to_prompt`, `list_prompt_requests`, `cancel_prompt_request`
- [ ] `api/server.py`: `ui_prompt_loop` MCP prompt
- [ ] `Canvas.remove_widget` / `CanvasManager.shutdown_canvas`: cancel hooks into broker

### Frontend
- [ ] `widgets/prompt.py`: `PromptButtonWidget` with all visual states (idle, pending, answered, cancelled, expired), input modes (none/inline/multiline), response area with scroll and Clear button
- [ ] `widgets/__init__.py`: export `PromptButtonWidget`
- [ ] `PromptButtonWidget.serialize()` includes `runtime` key; importer ignores it

### Infrastructure
- [ ] `tests/test_prompt_broker.py`: submit/wait ordering, concurrent waiters, timeout, terminal-state errors, cancel_for_widget/canvas, TTL expiry, max_pending_per_widget cap, diagnostics
- [ ] `tests/test_prompt_widget_render.py`: mocked imgui -- click submits, Enter submits, disabled while pending, response rendered, Clear resets, brace-safe template replace
- [ ] `tests/test_prompt_tools.py`: add_prompt_button -> simulate submit -> wait_for_prompt(0) -> respond_to_prompt -> list shows answered; error envelopes for unknown/terminal IDs

## Done Definition
- `PromptBroker` passes all concurrency tests (4 waiters + 1 submit = exactly 1 claimed)
- `PromptButtonWidget` renders in all 5 visual states with mocked imgui
- Full tool round-trip: `add_prompt_button` -> widget submit -> `wait_for_prompt` -> `respond_to_prompt` -> widget shows response
- `poll_events` sees `prompt` and `response` events without explicit `subscribe_events`
- All quality gates pass: `ruff check`, `mypy`, `pytest`

## Parallel work
- BE: `PromptBroker` implementation can run alongside FE: `PromptButtonWidget` render logic (they share only the `PromptRequest` dataclass)
- Tests for broker vs. widget render can be written in parallel

## Phase dependencies
- Requires: none (builds on existing widget/canvas/event infrastructure)

## Complexity
- Backend: M
- Frontend: M
- Infra: M

## Risks
- `wait_for_prompt` timeout must stay under client tool-call timeout (25 s default chosen for safety)
- Response callback runs on MCP thread and must never call ImGui; enforced by convention and test
- `max_pending_per_widget` cap (default 3) may need tuning for real usage patterns
