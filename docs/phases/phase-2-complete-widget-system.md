# Phase 2: Complete Widget System (Stage 6)

## Goal
Add the 5 remaining widget modules (slider, container, display, menu, plotting), register them with the factory, expose MCP tools for every widget type, and add tests — completing Stage 6.

## Deliverables

### Backend

#### New widget files (migrate from champi-gen-ui, rename all imports)
- [ ] `src/champi_imgui/widgets/slider.py`
  - Source: `/home/diva/git/champi-gen-ui/src/champi_gen_ui/widgets/slider.py` (~209 lines)
  - Classes: SliderFloatWidget, SliderIntWidget, DragFloatWidget, DragIntWidget
- [ ] `src/champi_imgui/widgets/container.py`
  - Source: `/home/diva/git/champi-gen-ui/src/champi_gen_ui/widgets/container.py` (~233 lines)
  - Classes: WindowWidget, CollapsingHeaderWidget, ChildWindowWidget, GroupWidget
- [ ] `src/champi_imgui/widgets/display.py`
  - Source: `/home/diva/git/champi-gen-ui/src/champi_gen_ui/widgets/display.py` (~354 lines)
  - Classes: PlotLinesWidget, TextColoredWidget, BulletTextWidget, HelpMarkerWidget
- [ ] `src/champi_imgui/widgets/menu.py`
  - Source: `/home/diva/git/champi-gen-ui/src/champi_gen_ui/widgets/menu.py` (~226 lines)
  - Classes: MenuBarWidget, MenuWidget, MenuItemWidget, TreeNodeWidget, SelectableWidget
- [ ] `src/champi_imgui/widgets/plotting.py`
  - Source: `/home/diva/git/champi-gen-ui/src/champi_gen_ui/widgets/plotting.py` (~402 lines)
  - Classes: LineChartWidget, BarChartWidget, ScatterPlotWidget, PieChartWidget, HeatmapWidget
  - Uses: `from imgui_bundle import implot`

#### Update factory registrations
- [ ] `src/champi_imgui/widgets/__init__.py` — add imports and `factory.register()` calls for all 5 new modules

#### MCP tools (add to `src/champi_imgui/server/main.py`)
Source reference for all tool signatures: `/home/diva/git/champi-gen-ui/src/champi_gen_ui/server/main.py`

Slider tools:
- [ ] `add_slider_float(canvas_id, widget_id, label, value, v_min, v_max, position)`
- [ ] `add_slider_int(canvas_id, widget_id, label, value, v_min, v_max, position)`
- [ ] `add_drag_float(canvas_id, widget_id, label, value, v_speed, v_min, v_max, position)`
- [ ] `add_drag_int(canvas_id, widget_id, label, value, v_speed, v_min, v_max, position)`

Container tools:
- [ ] `add_window(canvas_id, widget_id, title, width, height, position)`
- [ ] `add_collapsing_header(canvas_id, widget_id, label, open)`
- [ ] `add_separator(canvas_id, widget_id)`

Display tools:
- [ ] `add_plot_lines(canvas_id, widget_id, label, values, overlay_text, scale_min, scale_max)`
- [ ] `add_colored_text(canvas_id, widget_id, text, color, position)`
- [ ] `add_bullet_text(canvas_id, widget_id, text, position)`
- [ ] `add_help_marker(canvas_id, widget_id, description, position)`

Menu tools:
- [ ] `add_menu_bar(canvas_id, widget_id)`
- [ ] `add_menu(canvas_id, widget_id, label, enabled)`
- [ ] `add_menu_item(canvas_id, widget_id, label, shortcut, selected, enabled)`
- [ ] `add_tree_node(canvas_id, widget_id, label, open)`
- [ ] `add_selectable(canvas_id, widget_id, label, selected, size)`

Plotting tools (ImPlot):
- [ ] `add_line_chart(canvas_id, widget_id, title, x_data, y_data, width, height)`
- [ ] `add_bar_chart(canvas_id, widget_id, title, x_data, y_data, bar_size, width, height)`
- [ ] `add_scatter_plot(canvas_id, widget_id, title, x_data, y_data, width, height)`
- [ ] `add_pie_chart(canvas_id, widget_id, title, labels, values, x, y, radius)`
- [ ] `add_heatmap(canvas_id, widget_id, title, values, rows, cols, width, height)`

Also add remaining basic widget MCP tools not yet in server/main.py (check against source):
- [ ] `add_button`, `add_text`, `add_input_text`, `add_checkbox`, `add_color_picker` (from source server/main.py lines 107–300)

### Infrastructure
- [ ] Tests for slider widgets: `tests/test_slider_widgets.py`, `tests/test_slider_widgets_render.py`
- [ ] Tests for container widgets: `tests/test_container_widgets.py`
- [ ] Tests for display widgets: `tests/test_display_widgets.py`
- [ ] Tests for menu widgets: `tests/test_menu_widgets.py`
- [ ] Tests for plotting widgets: `tests/test_plotting_widgets.py`
- [ ] Tests for new MCP tools: `tests/test_widget_mcp_tools.py`

## Migration rules
1. Replace every `from champi_gen_ui.` with `from champi_imgui.`
2. Replace every `champi_gen_ui` string literal with `champi_imgui`
3. Widget additions to a running canvas MUST go through `canvas.queue_command()`, not direct mutation — see IPC pattern in `src/champi_imgui/core/canvas.py`
4. The MCP tool pattern is: get canvas → ensure running → create widget via factory → set position → `canvas.add_widget(widget)` → return `{"success": True, "data": widget.serialize()}`
5. `register_widgets()` in `server/main.py` must be updated to include all new widget types

## Verification steps
```bash
uv run ruff check src/
uv run ruff format --check src/
uv run mypy src/
uv run pytest tests/
```

Run after each new widget file is complete, not only at the end.

## Parallel work
- Slider, container, display, menu, plotting widget files can be written in parallel by different developers.
- MCP tools and tests for each widget module can be written in parallel with the widget implementation itself.
- All work must converge before the quality gate run.

## Phase dependencies
- Requires: Phase 1 merged (Widget ABC, WidgetFactory, WidgetRegistry on main)

## Complexity
- Backend: L
- Frontend: N/A
- Infra: M

## Risks
- `implot` (plotting) integration: verify `imgui_bundle` version in `pyproject.toml` exposes `implot` before implementing plotting widgets
- Drag widgets may not exist in imgui-bundle under those exact API names — check `imgui_bundle.imgui` API against source implementation
- Container widgets (Window, ChildWindow) require begin/end pairs in the render loop; ensure render order is correct and exceptions from imgui are caught
