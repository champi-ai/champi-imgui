# Champi-ImGui

> **Generative UI for LLMs through ImGui and Python**

An MCP (Model Context Protocol) server that enables Large Language Models to create sophisticated user interfaces using ImGui through natural language commands.

[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.0+-green.svg)](https://github.com/jlowin/fastmcp)
[![ImGui Bundle](https://img.shields.io/badge/ImGui-Bundle-red.svg)](https://github.com/pthom/imgui_bundle)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Coverage](badges/coverage.svg)](badges/coverage.svg)

---

## Features

- **200+ MCP tools** across 20 categories for comprehensive UI creation
- **150+ widget types** — buttons, sliders, charts, menus, containers, color pickers, and more
- **Plotting** via ImPlot: line charts, bar charts, scatter plots, pie charts, heatmaps, histograms
- **Keyframe animation system** with easing functions
- **Reactive data binding** (DataStore + BindingManager)
- **9 built-in themes** — dark, light, cherry, nord, dracula, gruvbox, solarized_dark, monokai, material
- **Layout manager** — horizontal, vertical, grid, stack, free modes
- **Notifications** — toast overlays (info, success, warning, error)
- **File dialogs** and message dialogs
- **JSON serialization** — export and import full canvas state
- **Python code generation** — export standalone scripts from any canvas
- **Template system** — save, load, list, and delete reusable UI templates

---

## Quick Start

### MCP Client Configuration (recommended)

The easiest way to use champi-imgui is via the `.mcp.json` config — no installation required. Copy [`.mcp.json.example`](.mcp.json.example) to `.mcp.json` in your project root, or add this to your existing config:

```json
{
  "mcpServers": {
    "champi-imgui": {
      "command": "uvx",
      "args": [
        "--from",
        "https://github.com/champi-ai/champi-imgui/releases/download/v1.15.0/champi_imgui-1.15.0-py3-none-any.whl",
        "champi-imgui",
        "serve"
      ]
    }
  }
}
```

`uvx` downloads and runs the wheel directly from the GitHub release — no PyPI, no manual install step.

### Manual Installation

Install from the GitHub release:

```bash
# Run without installing (ephemeral)
uvx --from https://github.com/champi-ai/champi-imgui/releases/download/v1.15.0/champi_imgui-1.15.0-py3-none-any.whl champi-imgui serve

# Install as a persistent tool
uv tool install https://github.com/champi-ai/champi-imgui/releases/download/v1.15.0/champi_imgui-1.15.0-py3-none-any.whl
champi-imgui serve

# Add to a project
uv add https://github.com/champi-ai/champi-imgui/releases/download/v1.15.0/champi_imgui-1.15.0-py3-none-any.whl
```

---

## Usage Examples

### Example 1: Simple Button

```
LLM: "Create a canvas with a button that says 'Click Me'"

MCP executes:
- create_canvas(canvas_id="main")
- add_button(canvas_id="main", widget_id="btn1", label="Click Me")
```

### Example 2: Data Dashboard

```
LLM: "Create a dashboard with a line chart showing sales data"

MCP executes:
- create_canvas(canvas_id="dashboard")
- add_line_chart(canvas_id="dashboard", widget_id="sales_chart", ...)
- set_layout_mode(mode="vertical")
```

### Example 3: Themed Form

```
LLM: "Create a dark-themed form with name and email inputs"

MCP executes:
- create_canvas(canvas_id="form")
- apply_theme(theme_name="dark")
- add_input_text(canvas_id="form", widget_id="name", label="Name")
- add_input_text(canvas_id="form", widget_id="email", label="Email")
```

### Example 4: Export to JSON

```
LLM: "Save this UI to a file"

MCP executes:
- export_canvas_json(canvas_id="form", filepath="my_form.json")

# Later, restore it:
- import_canvas_json(filepath="my_form.json")
```

### Example 5: Generate Python Code

```
LLM: "Generate a Python script for this canvas"

MCP executes:
- export_canvas_python(canvas_id="form", filepath="my_form.py")
# or, return as string:
- generate_canvas_code(canvas_id="form")
```

---

## MCP Tool Categories

| # | Category | Tools |
|---|---|---|
| 1 | Canvas Management | `create_canvas`, `get_canvas_state`, `clear_canvas`, `list_canvases`, `update_canvas_state`, `shutdown_canvas` |
| 2 | Basic Widgets | `add_button`, `add_small_button`, `add_arrow_button`, `add_invisible_button`, `add_text`, `add_colored_text`, `add_wrapped_text`, `add_bullet_text`, `add_label_text`, `add_input_text`, `add_checkbox`, `add_radio_button`, `add_combo`, `add_list_box`, `add_selectable` |
| 3 | Input Widgets | `add_input_int`, `add_input_float`, `add_input_double`, `add_input_scalar`, `add_checkbox_flags` |
| 4 | Color Widgets | `add_color_picker`, `add_color_picker3`, `add_color_edit3`, `add_color_edit4`, `add_color_button` |
| 5 | Sliders & Drag | `add_slider_int`, `add_slider_float`, `add_drag_int`, `add_drag_float` |
| 6 | Progress & Status | `add_progress_bar`, `add_loading_indicator`, `add_status_bar` |
| 7 | Container Widgets | `add_window`, `add_child_window`, `add_group`, `add_collapsing_header`, `add_tab_bar`, `add_tab_item`, `add_separator`, `add_spacing`, `add_dummy` |
| 8 | Menu Widgets | `add_menu_bar`, `add_menu`, `add_menu_item`, `add_tree_node`, `add_tooltip`, `add_popup`, `add_context_menu` |
| 9 | Display Widgets | `add_plot_lines`, `add_help_marker`, `add_bullet` |
| 10 | Plotting (ImPlot) | `add_line_chart`, `add_bar_chart`, `add_scatter_plot`, `add_pie_chart`, `add_heatmap`, `add_histogram`, `add_realtime_plot`, `add_error_bars` |
| 11 | Themes | `apply_theme`, `list_themes` |
| 12 | Layout | `set_layout_mode`, `set_layout_spacing` |
| 13 | Notifications | `show_notification`, `clear_notifications` |
| 14 | Animation | `create_animation`, `start_animation`, `stop_animation`, `get_animation_value` |
| 15 | Data Binding | `set_data`, `get_data`, `bind_data`, `unbind_data` |
| 16 | File & Message Dialogs | `add_file_dialog`, `show_message_dialog` |
| 17 | Export / Import | `export_canvas_json`, `export_canvas_python`, `import_canvas_json`, `get_canvas_json` |
| 18 | Code Generation | `generate_canvas_code`, `generate_widget_snippet`, `generate_component_template` |
| 19 | Templates | `save_template`, `load_template`, `list_templates`, `delete_template` |

---

## Architecture

```
LLM ──► MCP Client ──► FastMCP Server (200+ tools)
                              │
                       CanvasManager
                              │
              ┌───────────────┼───────────────┐
              │               │               │
        WidgetSystem    ExtensionLayer    Serialization
        ├── Factory      ├── Themes        ├── UIExporter
        ├── Registry     ├── Layouts       ├── UIImporter
        └── 150+ types   ├── Animation     ├── CodeGenerator
                         ├── Binding       └── TemplateManager
                         ├── Notifications
                         └── FileDialogs
                              │
                        ImGui Bundle
                        ├── ImGui Core
                        └── ImPlot
```

### Threading Model

- Each canvas runs its render loop on a **background daemon thread**
- MCP tools communicate with the render thread via a **command queue**
- All ImGui API calls are made on the render thread; MCP tools enqueue lambdas

---

## Development

### Setup

```bash
git clone https://github.com/champi-ai/champi-imgui.git
cd champi-imgui
uv sync --all-extras --dev
pre-commit install
pre-commit install --hook-type commit-msg
```

### Running Tests

```bash
uv run python -m pytest
uv run python -m pytest --cov=champi_imgui
```

### Code Quality

```bash
uv run ruff format .
uv run ruff check .
uv run python -m mypy src
uv run bandit -r src
```

### Project Structure

```
champi-imgui/
├── src/champi_imgui/
│   ├── server/        # FastMCP server — all MCP tool definitions
│   ├── core/          # Canvas, state, widget ABC, data binding, serialization, codegen
│   ├── widgets/       # Widget implementations (basic, slider, menu, display, container, plotting)
│   ├── extensions/    # Animation, notifications, file dialogs
│   ├── themes/        # ThemeManager + 9 preset themes
│   ├── layout/        # LayoutManager
│   ├── ipc/           # Shared memory IPC bridge
│   └── cli.py         # Entry point: champi-imgui serve
├── tests/             # pytest test suite (641 tests, 66%+ coverage)
├── docs/              # Architecture, widget catalog, MCP API reference
├── .github/workflows/ # CI, release, pre-commit
└── pyproject.toml
```

---

## Contributing

The project uses:
- **Conventional Commits** — `feat:`, `fix:`, `chore:` (triggers semantic versioning)
- **Semantic Versioning** — automated via commitizen
- **Pre-commit hooks** — ruff, mypy, bandit, detect-secrets
- **GitHub Actions** — CI on every PR, PyPI release on tag

---

## Requirements

- Python 3.12+
- imgui-bundle >= 1.5.0
- fastmcp >= 2.12.0
- pyglm, blinker, loguru, pydantic

See [pyproject.toml](pyproject.toml) for the complete dependency list.

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

## Related Projects

Part of the Champi ecosystem:
- **champi-signals** — Signal management and event processing
- **champi-stt** — Multi-provider speech-to-text
- **champi-tts** — Multi-provider text-to-speech
