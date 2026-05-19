# Senior Review

## VERDICT: APPROVED

## Summary

Both specs are well-scoped and internally consistent. The approach is sound for the champi ecosystem.

## Phase A: MCP Render Fix — no blocking issues

- Splitting UPDATE_STATE into UPDATE_TITLE + UPDATE_SIZE is the correct fix for the silent size-reset bug. Enum renumbering (SHUTDOWN 4→5) is safe since this is internal IPC.
- RENDER_FRAME heartbeat via champi-ipc lane is the correct health check. `_render_thread.is_alive()` was insufficient and this replaces it properly.
- `HAS_ECOSYSTEM` fallback pattern ensures standalone usage is not broken.
- 2s timeout for RENDER_FRAME ACK on `create_canvas` is reasonable; will surface the DISPLAY propagation root cause clearly.

## Phase B: MCP System State Reporter — no blocking issues

- `to_diagnostics()` helpers are straightforward and appropriately scoped (5-15 lines each).
- QUERY_STATE/STATE_RESPONSE lane pattern is the correct actor-boundary approach — reading Canvas state directly from the MCP thread would violate the lane model.
- Adding QUERY_STATE=140 and STATE_RESPONSE=141 to champi-signals is a cross-repo change; must be done first as a prerequisite.
- `@EventProcessor.emits_event` decoration is additive and non-breaking.

## Phase C: champi-ai-cli Foundation — no blocking issues

- Scope is appropriately narrow for a foundation phase: CLI, orchestrator, one working adapter, Jarvis demo.
- `ModelAdapter` ABC is the right abstraction for model-agnostic operation.
- The Jarvis demo is a concrete acceptance gate for the whole phase.
- champi-ai-cli depends on champi-imgui phases A and B being done first (health lanes must exist for orchestrator to query).

## Non-blocking notes

- Phase C depends on phases A and B being complete — schedule accordingly.
- champi-signals QUERY_STATE/STATE_RESPONSE must be PR'd and merged before phase B can implement the Canvas lane handler.
- The ecosystem optional extras in pyproject.toml use path references (`../champi-signals`) which work locally but will need PyPI references for production. Acceptable for this foundation phase.

## Labels to apply

- champi-imgui: `enhancement`, `ipc`, `mcp`
- champi-ai-cli: `new-package`, `ecosystem`
