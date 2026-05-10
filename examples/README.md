# Champi-Gen-UI Examples

This directory contains example applications demonstrating the capabilities of Champi-Gen-UI.

## Available Examples

### 1. Basic Demo (`basic_demo.py`)
A simple demonstration of basic widgets including buttons, text inputs, checkboxes, sliders, and color pickers.

**Features:**
- Basic widgets showcase
- Simple layout
- Widget callbacks
- Color customization

**Run it:**
```bash
python examples/basic_demo.py
```

### 2. Dashboard Demo (`dashboard_demo.py`)
A comprehensive interactive dashboard showcasing advanced features and multiple widget types.

**Features:**
- ✓ Real-time statistics display
- ✓ Performance metrics with progress bars
- ✓ Interactive controls (checkboxes, sliders)
- ✓ Data visualization (line & bar charts)
- ✓ Theme customization
- ✓ Docking layout support
- ✓ Multiple windows
- ✓ Collapsing sections
- ✓ Settings panel
- ✓ Tree views and selectables

**Run it:**
```bash
python examples/dashboard_demo.py
```

**What you'll see:**
1. **Main Dashboard Window** - Statistics, performance metrics, control panel
2. **Performance Charts Window** - Line chart and bar chart for data visualization
3. **Settings Window** - Theme selection, color customization, user preferences

### 3. MCP Tools Demo (`mcp_tools_demo.md`)
Documentation showing how to use the MCP server tools to create UIs through natural language.

**This is a reference guide for:**
- LLMs using the MCP server
- Understanding available MCP tools
- Common UI patterns
- Example interactions

## Running the MCP Server

To use Champi-Gen-UI as an MCP server:

```bash
# Start the server
champi-gen-ui serve

# Or with UV
uv run champi-gen-ui serve
```

Then configure your MCP client to connect to it.

## Widget Gallery

The examples demonstrate these widget types:

### Basic Widgets
- `TextWidget` - Display text
- `ButtonWidget` - Interactive buttons
- `InputTextWidget` - Text input fields
- `CheckboxWidget` - Checkboxes
- `SliderFloatWidget` / `SliderIntWidget` - Value sliders
- `ColorPickerWidget` - Color selection
- `ComboWidget` - Dropdown lists
- `ListBoxWidget` - List selection

### Display Widgets
- `TextColoredWidget` - Colored text
- `BulletTextWidget` - Bullet point lists
- `HelpMarkerWidget` - Tooltip markers
- `ProgressBarWidget` - Progress indicators
- `PlotLinesWidget` - Simple line plots

### Container Widgets
- `WindowWidget` - Sub-windows
- `CollapsingHeaderWidget` - Collapsible sections
- `SeparatorWidget` - Visual separators

### Menu Widgets
- `MenuBarWidget` - Menu bars
- `MenuWidget` - Menus
- `MenuItemWidget` - Menu items
- `SelectableWidget` - Selectable items
- `TreeNodeWidget` - Tree structures

### Plotting Widgets
- `LineChartWidget` - Line charts
- `BarChartWidget` - Bar charts
- `ScatterPlotWidget` - Scatter plots
- `PieChartWidget` - Pie charts
- `HeatmapWidget` - Heatmaps

## Themes

All examples support multiple themes:

- **Dark** - Default dark theme
- **Light** - Light theme
- **Cherry** - Cherry red theme
- **Nord** - Nord color scheme (used in dashboard_demo)
- **Dracula** - Dracula theme
- **Gruvbox** - Gruvbox theme
- **Solarized Dark** - Solarized dark theme
- **Monokai** - Monokai theme
- **Material** - Material design theme

Change themes programmatically:
```python
theme_manager.apply_theme_by_name("nord")
```

## Canvas Modes

Examples demonstrate different canvas modes:

1. **Standard** (`basic_demo.py`) - Traditional window-based UI
2. **Docking** (`dashboard_demo.py`) - Dockable window layout for complex UIs
3. **Multi-Viewport** - Multiple windows across screens
4. **Fullscreen** - Immersive full-screen mode
5. **Overlay** - Transparent overlay mode

## Creating Your Own UI

### Method 1: Direct Python Code

```python
from champi_gen_ui.core.canvas import CanvasManager
from champi_gen_ui.core.state import CanvasMode
from champi_gen_ui.widgets.basic import ButtonWidget, TextWidget

# Create manager
manager = CanvasManager()

# Create canvas
canvas = manager.create_canvas(
    canvas_id="my_app",
    width=800,
    height=600,
    mode=CanvasMode.STANDARD,
    title="My Application"
)

# Register widgets
registry = canvas.widget_registry
registry.factory.register("button", ButtonWidget)
registry.factory.register("text", TextWidget)

# Add widgets
title = registry.factory.create("text", "title", text="Hello World!")
canvas.add_widget(title)

button = registry.factory.create("button", "btn1", label="Click Me", size=[120, 40])
button.set_position(10, 40)
canvas.add_widget(button)

# Run
canvas.run()
```

### Method 2: Using MCP Tools (via LLM)

1. Start the MCP server: `champi-gen-ui serve`
2. Connect your LLM client
3. Ask the LLM to create UIs using natural language
4. The LLM will use MCP tools like `create_canvas`, `add_button`, etc.

See `mcp_tools_demo.md` for detailed examples.

## Tips for Development

1. **Start Simple**: Begin with `basic_demo.py` to understand the basics
2. **Use Docking Mode**: For complex UIs with multiple windows
3. **Apply Themes Early**: Set your theme before adding widgets
4. **Widget Registration**: Remember to register widget types before using them
5. **Callbacks**: Use `register_callback()` for interactive widgets
6. **Position Widgets**: Use `set_position(x, y)` for manual layout
7. **Organize with Sections**: Use collapsing headers to group related widgets
8. **Visual Separation**: Add separators between sections
9. **Data Binding**: Use the binding system for reactive UIs
10. **Export Your Work**: Use `export_canvas_json()` or `export_canvas_python()` to save your UIs

## Keyboard Shortcuts

When running the examples:
- **Ctrl+C** - Exit the application
- **Mouse Drag** - Move windows (in docking mode)
- **Window Close Button** - Close individual windows (if `closable=True`)

## Troubleshooting

### Issue: Window doesn't appear
**Solution**: Ensure you're calling `canvas.run()` at the end of your script

### Issue: Widgets not showing
**Solution**:
1. Check widget registration with `registry.factory.register()`
2. Verify widgets are added with `canvas.add_widget()`
3. Ensure widget visibility: `widget.state.visible = True`

### Issue: Theme not applying
**Solution**:
1. Check theme is registered: `theme_manager.list_themes()`
2. Use correct theme name (case-sensitive)
3. Apply theme before creating canvas

### Issue: Charts not rendering
**Solution**:
1. Ensure data is provided as lists: `x_data=[...]`, `y_data=[...]`
2. Check data lengths match for paired data (x/y coordinates)
3. Verify ImPlot is installed (should come with imgui-bundle)

## Further Reading

- [Main README](../README.md) - Project overview
- [MCP Tools API](../docs/MCP_TOOLS_API.md) - Complete API reference
- [Widget Catalog](../docs/WIDGET_CATALOG.md) - All available widgets
- [Architecture](../docs/ARCHITECTURE.md) - System architecture

## Contributing Examples

Have a cool example to share? We'd love to see it!

1. Create your example in this directory
2. Follow the existing naming pattern: `{name}_demo.py`
3. Add documentation at the top of the file
4. Update this README with your example
5. Submit a pull request

## License

These examples are part of the Champi-Gen-UI project and are licensed under the MIT License.
