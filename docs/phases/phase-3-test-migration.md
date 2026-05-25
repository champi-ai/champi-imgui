# Phase 3: Test Migration to Factory Injection

## Goal
Migrate all 11 test files from `monkeypatch.setattr` global patching to `create_mcp_app(manager=mock)` factory injection, making tests faster and more reliable.

## Deliverables

### Backend
- [ ] Identify all test files using `monkeypatch.setattr` on module-level managers
- [ ] Create shared test fixture `mcp_app` that calls `create_mcp_app(**mocks)`
- [ ] Migrate `test_server_tools.py` to factory injection
- [ ] Migrate `test_basic_widgets.py` to factory injection
- [ ] Migrate `test_color_widgets.py` to factory injection
- [ ] Migrate `test_container_widgets.py` to factory injection
- [ ] Migrate `test_display_widgets.py` to factory injection
- [ ] Migrate `test_input_widgets.py` to factory injection
- [ ] Migrate `test_menu_widgets.py` to factory injection
- [ ] Migrate `test_plotting_widgets.py` to factory injection
- [ ] Migrate `test_progress_widgets.py` to factory injection
- [ ] Migrate `test_slider_widgets.py` to factory injection
- [ ] Migrate `test_serialization_mcp_tools.py` to factory injection
- [ ] Remove all `monkeypatch.setattr` calls targeting old server globals

### Frontend
- [ ] N/A

### Infrastructure
- [ ] N/A

## Done Definition
- Zero `monkeypatch.setattr` calls targeting `champi_imgui.api` or `champi_imgui.server` globals remain
- All 11 migrated test files use `create_mcp_app()` with injected mocks
- `uv run pytest` passes with no warnings about patched globals
- No test depends on import-time side effects from `api/server.py`
- `ruff check tests/` passes

## Parallel work
- Individual test file migrations are independent and can be parallelized across developers

## Phase dependencies
- Requires: Phase 1 `create_mcp_app(**overrides)` factory with injection support

## Complexity
- Backend: M
- Frontend: N/A
- Infra: N/A

## Risks
- Some tests may implicitly depend on shared global state between test functions (hidden coupling)
- Mock signatures must match manager interfaces exactly or tests will silently pass incorrectly
