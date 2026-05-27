# Phase: Drawing & SHM Bug Spike

## Goal
Confirm the root cause of both #181 (DrawingWidget renders nothing) and #182 (SharedMemory leak crashes macOS) and document the fix approach for each.

## Deliverables

### Backend
- [ ] Instrument DrawingWidget.render() with diagnostic logging: log draw_list channel count, clipping rect, stroke/shape/annotation counts, and canvas_updated signal receiver count per frame
- [ ] Reproduce #181 in a minimal script (create canvas, add DrawingWidget, add_shape via MCP tool, screenshot) and capture draw_list state
- [ ] Reproduce #182 on macOS (Apple Silicon, Python 3.13): create_canvas, observe resource_tracker warnings, capture traceback and shm region lifecycle
- [ ] Write diagnosis document for #181: confirmed root cause, draw_list ordering diagram, proposed fix
- [ ] Write diagnosis document for #182: confirmed root cause, SharedMemory lifecycle diagram on macOS vs Linux, proposed fix

### Frontend
- [ ] N/A (no web frontend)

### Infrastructure
- [ ] N/A

## Done Definition
- Root cause for #181 is confirmed with evidence (draw_list state dump or equivalent)
- Root cause for #182 is confirmed with evidence (resource_tracker traceback + shm lifecycle trace)
- Each diagnosis document includes: symptom, root cause, affected code paths, and proposed fix approach
- No code fixes in this phase -- investigation only

## Parallel work
- #181 investigation (DrawingWidget render pipeline) can run in parallel with #182 investigation (SharedMemory macOS lifecycle) -- they are independent subsystems

## Phase dependencies
- Requires: none (both issues are in existing shipped code)

## Complexity
- Backend: S (investigation, no production code changes)
- Frontend: N/A
- Infra: N/A

## Risks
- #182 may not reproduce on Linux-only CI -- needs macOS access or macOS CI runner for validation
- #181 root cause may be in imgui-bundle's draw list implementation rather than champi-imgui code, which would change the fix approach
- If the DrawingWidget issue turns out to be a clipping rect problem, the fix may require changes to the Canvas render loop, not just the widget
