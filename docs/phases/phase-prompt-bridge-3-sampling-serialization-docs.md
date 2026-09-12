# Phase: Prompt Bridge 3 -- Sampling Bridge, Serialization, and Docs

## Goal
The sampling bridge removes the need for polling on capable clients, prompt_button round-trips through serialization/codegen, and all documentation is updated -- the Prompt Bridge initiative is complete.

## Deliverables

### Backend
- [ ] `api/server.py`: `run_prompt_bridge` (async, uses `ctx.sample()`, progress reporting, session tracking in broker)
- [ ] `api/server.py`: `stop_prompt_bridge` (stops one or all running bridges)
- [ ] `core/prompt_bridge.py`: `bridges` dict for session tracking, stop flag per session
- [ ] `api/server.py`: extend `get_canvas_info` to include `prompt_bridge` diagnostics
- [ ] `core/codegen.py`: `PromptButtonWidget` branch in `generate_widget_code`

### Frontend
- [ ] Serialization: `UIExporter`/`UIImporter` round-trip for `prompt_button` (runtime key dropped on import)
- [ ] `CanvasState.to_dict()` includes `window_flags` from properties (already covered by properties serialization, verify)

### Infrastructure
- [ ] `tests/test_sampling_bridge.py`: fake Context with sampling unsupported -> error; supported -> one request sampled and answered; stop flag ends loop
- [ ] `tests/test_serialization.py` (extend): export/import canvas containing a `prompt_button`
- [ ] `docs/MCP_TOOLS_API.md`: new sections "Host Window (2 tools)" and "Prompt Bridge (9 tools)"
- [ ] `docs/WIDGET_CATALOG.md`: `prompt_button` entry with visual state table and properties
- [ ] `README.md`: "Corner launcher" quick-start example (the 4-step sequence from spec Section 8)
- [ ] `docs/ARCHITECTURE.md`: broker threading diagram (submit -> wait -> respond flow)

## Done Definition
- `run_prompt_bridge` with a fake Context that supports sampling: one request is submitted, sampled, and answered automatically
- `run_prompt_bridge` with sampling unsupported: returns clear error pointing to `wait_for_prompt`
- `stop_prompt_bridge` terminates a running bridge within one wait cycle
- Export a canvas with `prompt_button` -> import -> widget properties match, runtime key absent
- `CodeGenerator` produces valid `PromptButtonWidget(...)` constructor call
- All doc files updated with accurate tool signatures and examples
- All quality gates pass; full test suite green

## Parallel work
- BE: sampling bridge implementation can run alongside Infra: doc updates
- BE: codegen branch can run alongside Infra: serialization test extension

## Phase dependencies
- Requires: Phase Prompt Bridge 1 (broker, widget, tools) and Phase Prompt Bridge 2 (host window, canvas placement)

## Complexity
- Backend: M
- Frontend: S
- Infra: M

## Risks
- Sampling support varies by client; capability check makes this explicit but user experience depends on client implementation
- `ctx.sample()` holds a request open for up to an hour; stdio clients need matching timeout configuration
- `run_prompt_bridge` is a long-running tool call; Streamable HTTP handles this natively, stdio requires client tolerance
