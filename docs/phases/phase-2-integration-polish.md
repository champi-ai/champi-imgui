# Phase 2: Integration and Polish

## Goal
Image widget emits events through the event queue, and both features are documented and release-ready.

## Deliverables

### Backend
- [ ] ImageWidget emits `load`, `error`, and `click` events through EventQueue
- [ ] `on_click` support for ImageWidget (detect click via `imgui.is_item_clicked()`)
- [ ] Error handling: invalid file path, unsupported format, missing file — emits error event + returns error in MCP response
- [ ] Event payload includes image-specific data (file_path, dimensions)

### Frontend
- [ ] N/A

### Infrastructure
- [ ] End-to-end test: add image, subscribe to click event, simulate click, poll event
- [ ] MCP tool docstrings reviewed for LLM clarity
- [ ] Version bump via `feat:` commit

## Done Definition
- An MCP client can: create an image widget, subscribe to its click events, and poll to detect when a user clicked the image
- Invalid image paths return clear error messages (not crashes)
- All quality gates pass: pytest, ruff check, ruff format

## Parallel work
- Error handling can be done alongside event integration
- Documentation review is independent of code changes

## Phase dependencies
- Requires: Phase 0 (ImageWidget exists) and Phase 1 (EventQueue exists)

## Complexity
- Backend: S
- Frontend: N/A
- Infra: S

## Risks
- Click detection on images requires the image to be rendered as a button-like element or explicit `is_item_clicked()` check — need to verify imgui behavior
