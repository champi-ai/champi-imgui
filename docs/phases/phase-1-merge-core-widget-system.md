# Phase 1: Merge Core Widget System

## Goal
Merge `origin/feat/core-widget-system` into main so the widget infrastructure, 4 widget modules, and 10 test files become the new baseline for all subsequent phases.

## Deliverables

### Backend
- [ ] Merge branch `origin/feat/core-widget-system` into `main` via PR or direct merge
- [ ] Confirm `src/champi_imgui/core/widget.py` (Widget ABC, WidgetFactory, WidgetRegistry — 255 lines) is present on main
- [ ] Confirm `src/champi_imgui/core/state.py` extended WidgetState and blinker signals are present
- [ ] Confirm `src/champi_imgui/widgets/__init__.py` factory registrations are present
- [ ] Confirm the 4 widget modules are present on main:
  - `src/champi_imgui/widgets/basic.py` — Button, Text, Checkbox, RadioButton, Combo, ListBox
  - `src/champi_imgui/widgets/color.py` — ColorPicker, ColorEdit, ColorButton
  - `src/champi_imgui/widgets/input.py` — InputText, InputInt, InputFloat, MultiInput variants
  - `src/champi_imgui/widgets/progress.py` — ProgressBar, LoadingIndicator

### Frontend
- N/A — library project, no frontend

### Infrastructure
- [ ] All 10 test files from the branch land on main:
  - `tests/test_widget_infrastructure.py`
  - `tests/test_basic_widgets.py`
  - `tests/test_basic_widgets_render.py`
  - `tests/test_color_widgets.py`
  - `tests/test_color_widgets_render.py`
  - `tests/test_input_widgets.py`
  - `tests/test_input_widgets_render.py`
  - `tests/test_progress_widgets.py`
  - `tests/test_progress_widgets_render.py`
- [ ] `pyproject.toml` updated with any new dependencies added in the branch (imgui-bundle extras, blinker)
- [ ] `uv.lock` updated

## Done Definition
- `git log --oneline main | head -5` shows the merge commit
- `ls src/champi_imgui/widgets/` shows: `__init__.py basic.py color.py input.py progress.py`
- `uv run pytest tests/` passes with 0 failures
- `uv run ruff check src/` exits 0
- `uv run mypy src/` exits 0

## Parallel work
- No parallelism: this is a single merge operation. All subsequent phases depend on it.

## Phase dependencies
- Requires: none (this is the starting point)

## Complexity
- Backend: S
- Frontend: N/A
- Infra: S

## Risks
- The branch was developed against a potentially older main. Run the full quality gate after merge and fix any conflicts before proceeding to Phase 2.
- The branch does NOT add widget MCP tools to `server/main.py` (only the 6 canvas tools remain). Phase 2 adds those.
