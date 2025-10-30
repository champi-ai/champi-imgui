# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**champi-imgui** is an ImGui-based UI framework for MCP (Model Context Protocol) servers, enabling LLM-driven UI generation and manipulation through natural language commands.

**Status**: Migration in progress from `champi-gen-ui` to `champi-imgui`. The source repository at `/mnt/raid_0_drive/mcp_projs/libraries/champi-gen-ui` contains a fully-implemented system with 200+ MCP tools and 150+ widgets.

## Migration Instructions

This repository is being migrated from `champi-gen-ui` → `champi-imgui` with the following key changes:
- **Package name**: `champi-gen-ui` → `champi-imgui`
- **Module name**: `champi_gen_ui` → `champi_imgui`
- **Versioning**: Now uses semantic versioning with `v` prefix (v0.1.0, v1.0.0)
- **Repository**: Clean git history with meaningful commits

### Source Location
The original implementation is at: `/mnt/raid_0_drive/mcp_projs/libraries/champi-gen-ui`

### Migration Execution Protocol

When working on this migration, **ALWAYS**:

1. **Review Before Implementing**
   - Read reference code from `/mnt/raid_0_drive/mcp_projs/libraries/champi-gen-ui/src/champi_gen_ui/`
   - Understand the pattern and architecture
   - Check MIGRATION_PLAN.md for the specific stage you're implementing

2. **Rename Packages Everywhere**
   ```python
   # OLD (champi-gen-ui)
   from champi_gen_ui.core.canvas import Canvas

   # NEW (champi-imgui)
   from champi_imgui.core.canvas import Canvas
   ```

3. **Run Quality Gates After Every Change**
   ```bash
   uv run ruff check src/
   uv run ruff format --check src/
   uv run mypy src/
   uv run pytest tests/
   ```

4. **Never Proceed with Failing Validations**
   - All linters must pass
   - All type checks must pass
   - All tests must pass

5. **Follow Conventional Commits**
   - `feat:` - Triggers minor version bump (0.1.0 → 0.2.0)
   - `fix:` - Triggers patch version bump (0.1.0 → 0.1.1)
   - `chore:` - No version bump
   - `BREAKING CHANGE:` in body - Triggers major version bump

### Migration Stages

The migration follows an 8-stage plan (see MIGRATION_PLAN.md):

1. **Stage 1-3 (Combined)**: Repository foundation, versioning, release workflow → v0.0.1
2. **Stage 4**: Documentation update (chore commit, stays v0.0.1)
3. **Stage 5**: MCP server + Canvas + IPC → v0.1.0
4. **Stage 6**: Core widget system → v0.2.0
5. **Stage 7**: Advanced features (themes, layouts, animations, binding) → v0.3.0
6. **Stage 8**: Export, serialization, templates → v0.4.0

**Current stage**: Check git history or ask the user

## Development Commands

### Environment Setup
```bash
# Install uv package manager (if not already installed)
pip install uv

# Sync dependencies (once pyproject.toml is properly configured)
uv sync --all-extras --dev
```

### Code Quality
```bash
# Linting
uv run ruff check .
uv run ruff format .

# Type checking
uv run mypy src

# Security scanning
uv run bandit -r src
```

### Testing
```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_canvas.py

# Run with coverage
uv run pytest --cov=src --cov-report=html
```

## Architecture

Based on the actual champi-gen-ui implementation:

### Core Components

1. **MCP Server** (`src/champi_imgui/server/main.py`)
   - FastMCP server with 200+ tools
   - Global managers instantiated at module level:
     ```python
     canvas_manager = CanvasManager()
     theme_manager = ThemeManager()
     layout_manager = LayoutManager()
     notification_manager = NotificationManager()
     animation_manager = AnimationManager()
     data_store = DataStore()
     binding_manager = BindingManager(data_store)
     validation_manager = ValidationManager()
     template_manager = TemplateManager()
     ```
   - Returns consistent format: `{"success": bool, "data": dict, "error": str}`

2. **State Management** (`src/champi_imgui/core/state.py`)
   - Uses Python dataclasses for state
   - **CanvasState**: canvas_id, mode, size, position, theme, title, widgets, fps_idle, fps_active
   - **WidgetState**: widget_id, widget_type, visible, enabled, position, size, properties, callbacks
   - **CanvasMode enum**: STANDARD, DOCKING, MULTI_VIEWPORT, FULLSCREEN, OVERLAY
   - **Signal system** (blinker): canvas_updated, widget_created, widget_updated

3. **Canvas System** (`src/champi_imgui/core/canvas.py`)
   - **Canvas class**:
     - Holds CanvasState and WidgetRegistry
     - `_running`: bool flag for render thread status
     - `_render_thread`: daemon thread for non-blocking rendering
     - `_command_queue`: Queue for IPC from MCP tools → render thread
     - `_needs_render`: flag to signal UI updates
   - **Threading pattern**:
     ```python
     def run_async(self):
         self._running = True
         self._render_thread = threading.Thread(
             target=render_loop,
             daemon=True
         )
         self._render_thread.start()
     ```
   - **IPC pattern**:
     ```python
     def queue_command(self, command: Callable[[], Any]):
         self._command_queue.put(command)
         self._needs_render = True

     def process_commands(self):  # Called in render loop
         while not self._command_queue.empty():
             command = self._command_queue.get_nowait()
             command()
     ```
   - **CanvasManager**: Manages multiple canvases, auto-start feature

4. **Widget System** (`src/champi_imgui/core/widget.py`, `src/champi_imgui/widgets/`)
   - **Widget ABC**:
     - `widget_id`: str
     - `state`: WidgetState (dataclass)
     - `_callbacks`: dict[str, Callable]
     - `render()`: abstract method (must implement)
     - `update(**props)`: Update properties and emit signal
     - `serialize()`: Convert to dict
   - **WidgetFactory**: Register and create widgets by type string
   - **WidgetRegistry**: Manages widget instances lifecycle
   - **Widget Types** (150+ total):
     - **Basic**: Button, Text, InputText, Checkbox, RadioButton, ColorPicker, Combo, ListBox
     - **Sliders**: SliderFloat, SliderInt, DragFloat, DragInt, ProgressBar
     - **Display**: TextColored, BulletText, HelpMarker, ProgressBar, PlotLines
     - **Container**: Window, CollapsingHeader, Separator
     - **Menu**: MenuBar, Menu, MenuItem, Selectable, TreeNode
     - **Plotting** (ImPlot): LineChart, BarChart, ScatterPlot, PieChart, Heatmap

5. **Extensions**
   - **Themes** (`themes/`): ThemeManager, 9 THEME_PRESETS (dark, light, cherry, nord, dracula, gruvbox, solarized_dark, monokai, material)
   - **Layouts** (`layout/`): LayoutManager, LayoutMode (horizontal, vertical, grid, stack, free)
   - **Animation** (`extensions/animation.py`): AnimationManager, EasingFunction enum, keyframe system
   - **Data Binding** (`core/binding.py`): DataStore (path-based reactive data), BindingManager, ValidationManager
   - **File Dialogs** (`extensions/file_dialog.py`): FileDialogWidget, MessageDialog
   - **Notifications** (`extensions/notification.py`): NotificationManager, NotificationType enum

6. **Serialization & Code Gen** (`src/champi_imgui/core/`)
   - **UIExporter**: Export canvas to JSON (file or string)
   - **UIImporter**: Import canvas from JSON
   - **CodeGenerator**: Generate standalone Python scripts
   - **TemplateCodeGenerator**: Generate reusable component templates
   - **TemplateManager**: Save/load/list/delete UI templates

### Threading Model

Critical for non-blocking MCP server operation:

```python
# Canvas runs in background thread
canvas._render_thread = threading.Thread(
    target=render_loop,
    daemon=True  # Dies when main thread exits
)

# IPC via command queue
canvas._command_queue = Queue()

# MCP tools queue commands
canvas.queue_command(lambda: canvas.add_widget(widget))

# Render thread processes commands
canvas.process_commands()  # Called in render loop
```

### MCP Tool Pattern

All MCP tools follow this pattern:

```python
@mcp.tool()
def add_button(canvas_id: str, widget_id: str, label: str = "Button", ...) -> dict:
    """Tool docstring describes functionality for LLM."""
    try:
        # 1. Get canvas
        canvas = canvas_manager.get_canvas(canvas_id)
        if not canvas:
            return {"success": False, "error": f"Canvas {canvas_id} not found"}

        # 2. Ensure canvas is running
        canvas_manager.ensure_canvas_running(canvas_id)

        # 3. Create widget via factory
        widget = canvas.widget_registry.factory.create("button", widget_id, label=label)

        # 4. Add to canvas (thread-safe via IPC)
        canvas.add_widget(widget)

        return {"success": True, "data": widget.serialize()}
    except Exception as e:
        logger.error(f"Error adding button: {e}")
        return {"success": False, "error": str(e)}
```

## Migration Context

This repository was created as a clean migration from `champi-gen-ui`. Key differences:

- **Package name**: `champi-gen-ui` → `champi-imgui`
- **Module name**: `champi_gen_ui` → `champi_imgui`
- **Versioning**: Now uses semantic versioning with `v` prefix (v0.1.0, v1.0.0)
- **Git history**: Squashed from 40+ commits to focus on meaningful changes

### Version Bumping

- Uses Commitizen with conventional commits
- **feat:** commits bump minor version (0.1.0 → 0.2.0)
- **fix:** commits bump patch version (0.1.0 → 0.1.1)
- **chore:** commits don't trigger version bumps
- **BREAKING CHANGE:** in commit message bumps major version

## Critical Implementation Notes

### When Implementing Features

1. **Review reference materials** in MIGRATION_PLAN.md for the specific stage
2. **Understand intent**, not just code - simplify where appropriate
3. **Propose implementation plan** before writing code
4. **Update package names** from `champi_gen_ui` to `champi_imgui`
5. **Run all quality gates**:
   ```bash
   ruff check src/
   mypy src/
   pytest tests/
   ```
6. **Never proceed with failing validations**

### Threading Safety

- ImGui calls MUST happen on the render thread
- Use `queue_command()` for dynamic updates from MCP tools
- Process queued commands in render loop via `process_commands()`

### Widget Registration

Widgets must be registered with the factory:

```python
registry.factory.register("button", ButtonWidget)
registry.factory.register("text", TextWidget)
# ...
```

### Dependencies

Core dependencies (from migration plan):
- `imgui-bundle` - ImGui Python bindings
- `pyglm` - OpenGL math library
- `fastmcp` - MCP server framework
- `loguru` - Logging

## File Structure (from champi-gen-ui)

```
src/champi_imgui/                 # Will be migrated from champi_gen_ui/
├── server/
│   ├── __init__.py
│   └── main.py                   # FastMCP server, 200+ MCP tools
├── core/
│   ├── __init__.py
│   ├── state.py                  # CanvasState, WidgetState dataclasses, signals
│   ├── canvas.py                 # Canvas, CanvasManager
│   ├── widget.py                 # Widget ABC, WidgetFactory, WidgetRegistry
│   ├── binding.py                # DataStore, BindingManager, ValidationManager
│   ├── serialization.py          # UIExporter, UIImporter, TemplateManager
│   └── codegen.py                # CodeGenerator, TemplateCodeGenerator
├── widgets/
│   ├── __init__.py
│   ├── basic.py                  # Button, Text, InputText, Checkbox, RadioButton, ColorPicker, Combo, ListBox
│   ├── slider.py                 # SliderFloat, SliderInt, DragFloat, DragInt, ProgressBar
│   ├── menu.py                   # MenuBar, Menu, MenuItem, Selectable, TreeNode
│   ├── display.py                # TextColored, BulletText, HelpMarker, ProgressBar, PlotLines
│   ├── container.py              # Window, CollapsingHeader, Separator
│   └── plotting.py               # LineChart, BarChart, ScatterPlot, PieChart, Heatmap
├── themes/
│   ├── __init__.py
│   ├── manager.py                # ThemeManager
│   └── presets.py                # THEME_PRESETS dict (9 themes)
├── layout/
│   ├── __init__.py
│   └── manager.py                # LayoutManager, LayoutMode enum
├── extensions/
│   ├── __init__.py
│   ├── animation.py              # AnimationManager, EasingFunction enum
│   ├── file_dialog.py            # FileDialogWidget, MessageDialog
│   └── notification.py           # NotificationManager, NotificationType enum
├── cli.py                        # CLI entry point (champi-imgui serve)
└── __init__.py                   # Package version
```

## MCP Server Configuration

The project includes MCP server configurations (`.mcp.json`) for:
- memory
- sequential-thinking
- filesystem
- fetch
- interactive

These servers can be used during development for testing integrations.

## CLI Usage

The migrated package will have a CLI entry point:

```bash
# Start the MCP server
champi-imgui serve

# Or with uv
uv run champi-imgui serve
```

The CLI (`cli.py`) handles:
- Logger configuration (loguru → stderr, INFO level)
- Cleanup handlers (atexit, SIGINT, SIGTERM)
- Canvas manager cleanup on shutdown
- FastMCP server execution via `mcp.run()`

## Critical Implementation Patterns

### MCP Tool Pattern

Every MCP tool follows this exact pattern:

```python
@mcp.tool()
def add_button(
    canvas_id: str,
    widget_id: str,
    label: str = "Button",
    position: list[float] | None = None,
    size: list[float] | None = None,
) -> dict[str, Any]:
    """Add a button widget to the canvas."""  # Docstring for LLM
    try:
        # 1. Get canvas
        canvas = canvas_manager.get_canvas(canvas_id)
        if not canvas:
            return {"success": False, "error": f"Canvas {canvas_id} not found"}

        # 2. Ensure canvas is running
        canvas_manager.ensure_canvas_running(canvas_id)

        # 3. Create widget via factory
        widget = canvas.widget_registry.factory.create(
            "button", widget_id, label=label, size=tuple(size) if size else None
        )

        # 4. Set position if specified
        if position:
            widget.set_position(*position)

        # 5. Add to canvas (thread-safe)
        canvas.add_widget(widget)

        return {"success": True, "data": widget.serialize()}
    except Exception as e:
        logger.error(f"Error adding button: {e}")
        return {"success": False, "error": str(e)}
```

### Widget Implementation Pattern

Every widget extends the Widget ABC:

```python
from champi_imgui.core.widget import Widget
from imgui_bundle import imgui

class ButtonWidget(Widget):
    """Button widget."""

    def __init__(self, widget_id: str, label: str = "Button", size: tuple[float, float] | None = None, **props):
        super().__init__(widget_id, label=label, size=size, **props)
        self.label = self.state.properties.get("label", label)
        self.size = self.state.properties.get("size", size or (0, 0))
        self.clicked = False

    def render(self) -> bool:
        """Render button and return click state."""
        if not self.state.visible:
            return False

        self.clicked = imgui.button(self.label, self.size)
        return self.clicked
```

### Signal/Event Pattern

Uses blinker for event emission:

```python
from blinker import signal

# Define signals
canvas_updated = signal("canvas_updated")
widget_created = signal("widget_created")
widget_updated = signal("widget_updated")

# Emit signal
widget_updated.send(self, widget=self)

# Connect to signal (optional)
widget_updated.connect(on_widget_updated)
```

### State Serialization Pattern

All state objects have `to_dict()`:

```python
@dataclass
class CanvasState:
    canvas_id: str
    mode: CanvasMode = CanvasMode.STANDARD
    # ... other fields

    def to_dict(self) -> dict[str, Any]:
        return {
            "canvas_id": self.canvas_id,
            "mode": self.mode.value,
            "widgets": {wid: wstate.to_dict() for wid, wstate in self.widgets.items()},
            # ... other fields
        }
```

## Important References

- **MIGRATION_PLAN.md**: Comprehensive 8-stage implementation guide with code patterns
- **MIGRATION_SYSTEM_PROMPT.md**: Execution methodology for LLM assistants
- **Source codebase**: `/mnt/raid_0_drive/mcp_projs/libraries/champi-gen-ui/src/champi_gen_ui/`
- Original codebase patterns are referenced as: `src/champi_gen_ui/path/file.py:line-range`

## Next Steps

1. Review this CLAUDE.md file
2. Read MIGRATION_PLAN.md to understand the 8-stage migration
3. Read MIGRATION_SYSTEM_PROMPT.md for execution protocol
4. Ask user which stage to begin (usually Stage 1: Repository Foundation)
5. Execute migration step-by-step with validation at each step