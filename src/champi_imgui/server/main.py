"""FastMCP server for champi-imgui.

Provides MCP tools for creating and managing Canvas windows and widgets
through shared memory IPC.
"""

from typing import Any

from fastmcp import FastMCP
from loguru import logger

from champi_imgui.core.binding import BindingManager, DataStore
from champi_imgui.core.canvas import CanvasManager
from champi_imgui.core.codegen import CodeGenerator, TemplateCodeGenerator
from champi_imgui.core.serialization import TemplateManager, UIExporter, UIImporter
from champi_imgui.extensions.animation import AnimationManager, EasingFunction
from champi_imgui.extensions.file_dialog import (
    FileDialogMode,
    FileDialogWidget,
    MessageDialog,
)
from champi_imgui.extensions.notification import NotificationManager, NotificationType
from champi_imgui.ipc.command_types import CommandType
from champi_imgui.ipc.shared_memory_manager import SharedMemoryManager
from champi_imgui.layout.manager import LayoutManager, LayoutMode
from champi_imgui.themes.manager import ThemeManager
from champi_imgui.themes.presets import THEME_PRESETS
from champi_imgui.widgets.basic import (
    ArrowButtonWidget,
    BulletTextWidget,
    BulletWidget,
    ButtonWidget,
    CheckboxWidget,
    InputTextWidget,
    InvisibleButtonWidget,
    LabelTextWidget,
    SmallButtonWidget,
    TextColoredWidget,
    TextDisabledWidget,
    TextWidget,
    TextWrappedWidget,
)
from champi_imgui.widgets.color import (
    ColorButtonWidget,
    ColorEdit3Widget,
    ColorEdit4Widget,
    ColorPicker3Widget,
    ColorPickerWidget,
)
from champi_imgui.widgets.container import (
    ChildWindowWidget,
    CollapsingHeaderWidget,
    DummyWidget,
    GroupWidget,
    SeparatorWidget,
    SpacingWidget,
    TabBarWidget,
    TabItemWidget,
    WindowWidget,
)
from champi_imgui.widgets.display import (
    HelpMarkerWidget,
    ImageWidget,
    PlotLinesWidget,
)
from champi_imgui.widgets.input import (
    CheckboxFlagsWidget,
    ComboWidget,
    InputDoubleWidget,
    InputFloatWidget,
    InputIntWidget,
    InputScalarWidget,
    ListBoxWidget,
    RadioButtonWidget,
    SelectableWidget,
)
from champi_imgui.widgets.menu import (
    ContextMenuWidget,
    MenuBarWidget,
    MenuItemWidget,
    MenuWidget,
    PopupWidget,
    TooltipWidget,
    TreeNodeWidget,
)
from champi_imgui.widgets.plotting import (
    BarChartWidget,
    ErrorBarsWidget,
    HeatmapWidget,
    HistogramWidget,
    LineChartWidget,
    PieChartWidget,
    RealtimePlotWidget,
    ScatterPlotWidget,
)
from champi_imgui.widgets.progress import (
    LoadingIndicatorWidget,
    ProgressBarWidget,
    StatusBarWidget,
)
from champi_imgui.widgets.slider import (
    DragFloatWidget,
    DragIntWidget,
    SliderFloatWidget,
    SliderIntWidget,
)

# Global canvas manager (single instance for all MCP tool calls)
canvas_manager = CanvasManager()

# Phase 3: Advanced feature managers
theme_manager = ThemeManager()
layout_manager = LayoutManager()
data_store = DataStore()
binding_manager = BindingManager(data_store)
animation_manager = AnimationManager()
notification_manager = NotificationManager()
template_manager = TemplateManager()


# Wire binding manager to widget registry so data-store changes propagate to
# state.properties before the next render frame.
def _resolve_widget(widget_id: str) -> Any:
    for canvas in canvas_manager.canvases.values():
        widget = canvas.widget_registry.get(widget_id)
        if widget is not None:
            return widget
    return None


binding_manager.set_widget_lookup(_resolve_widget)

# Register preset themes at startup
for _theme in THEME_PRESETS.values():
    theme_manager.register_theme(_theme)

# FastMCP server instance
mcp = FastMCP("champi-imgui")


def _create_widget_in_canvas(canvas_id: str, widget: Any) -> dict[str, Any]:
    """Add a pre-constructed widget to the canvas.

    Args:
        canvas_id: Target canvas identifier
        widget: Widget instance to add

    Returns:
        Success/error dict with serialized widget data
    """
    canvas = canvas_manager.get_canvas(canvas_id)
    if canvas is None:
        return {"success": False, "error": f"Canvas '{canvas_id}' not found"}
    canvas_manager.ensure_canvas_running(canvas_id)
    canvas.add_widget(widget)
    return {"success": True, "data": widget.serialize()}


# ==============================================================================
# Canvas management tools
# ==============================================================================


@mcp.tool()
def create_canvas(
    canvas_id: str,
    title: str = "Canvas",
    width: int = 800,
    height: int = 600,
    auto_start: bool = True,
) -> dict[str, Any]:
    """Create a new canvas window.

    The canvas window will appear immediately and run in a background thread.
    Commands can be sent to the canvas via other MCP tools.

    Args:
        canvas_id: Unique identifier for the canvas
        title: Window title
        width: Window width in pixels
        height: Window height in pixels
        auto_start: Whether to automatically start rendering (default: True)

    Returns:
        Success status and canvas state data
    """
    try:
        # Check if canvas already exists
        existing = canvas_manager.get_canvas(canvas_id)
        if existing is not None:
            return {
                "success": False,
                "error": f"Canvas '{canvas_id}' already exists",
            }

        # Create canvas (window appears immediately if auto_start=True)
        canvas = canvas_manager.create_canvas(
            canvas_id=canvas_id,
            title=title,
            size=(width, height),
            auto_start=auto_start,
        )

        logger.info(f"Created canvas '{canvas_id}' via MCP tool")

        return {
            "success": True,
            "data": canvas.state.to_dict(),
        }

    except Exception as e:
        logger.error(f"Error creating canvas '{canvas_id}': {e}")
        return {
            "success": False,
            "error": str(e),
        }


@mcp.tool()
def get_canvas_state(canvas_id: str) -> dict[str, Any]:
    """Get the current state of a canvas.

    Args:
        canvas_id: Canvas identifier

    Returns:
        Success status and canvas state data
    """
    try:
        canvas = canvas_manager.get_canvas(canvas_id)
        if canvas is None:
            return {
                "success": False,
                "error": f"Canvas '{canvas_id}' not found",
            }

        return {
            "success": True,
            "data": canvas.state.to_dict(),
        }

    except Exception as e:
        logger.error(f"Error getting canvas state for '{canvas_id}': {e}")
        return {
            "success": False,
            "error": str(e),
        }


@mcp.tool()
def clear_canvas(canvas_id: str) -> dict[str, Any]:
    """Clear all widgets from a canvas.

    Sends a CLEAR_CANVAS command via shared memory to the canvas render thread.
    The command is processed asynchronously (fire-and-forget).

    Args:
        canvas_id: Canvas identifier

    Returns:
        Success status
    """
    try:
        canvas = canvas_manager.get_canvas(canvas_id)
        if canvas is None:
            return {
                "success": False,
                "error": f"Canvas '{canvas_id}' not found",
            }

        # Ensure canvas is running
        if not canvas._running:
            canvas.run_async()

        # Send command via shared memory (MCP server attaches to Canvas's memory)
        shm_manager = SharedMemoryManager(name_prefix=f"canvas_{canvas_id}")
        try:
            shm_manager.attach_regions()

            # Write command (fire-and-forget)
            seq_num = shm_manager.write_command(
                CommandType.CLEAR_CANVAS, canvas_id=canvas_id
            )

            logger.info(f"Sent CLEAR_CANVAS command to '{canvas_id}' (seq={seq_num})")

            return {
                "success": True,
                "data": {
                    "canvas_id": canvas_id,
                    "command": "CLEAR_CANVAS",
                    "seq_num": seq_num,
                },
            }

        finally:
            # Clean up shared memory handle (Canvas owns the memory)
            shm_manager.cleanup()

    except Exception as e:
        logger.error(f"Error clearing canvas '{canvas_id}': {e}")
        return {
            "success": False,
            "error": str(e),
        }


@mcp.tool()
def list_canvases() -> dict[str, Any]:
    """List all active canvas IDs.

    Returns:
        Success status and list of canvas IDs
    """
    try:
        canvas_ids = canvas_manager.list_canvases()

        return {
            "success": True,
            "data": {
                "canvas_ids": canvas_ids,
                "count": len(canvas_ids),
            },
        }

    except Exception as e:
        logger.error(f"Error listing canvases: {e}")
        return {
            "success": False,
            "error": str(e),
        }


@mcp.tool()
def update_canvas_state(
    canvas_id: str,
    title: str | None = None,
    width: int | None = None,
    height: int | None = None,
) -> dict[str, Any]:
    """Update canvas state (title, size).

    Sends an UPDATE_STATE command via shared memory to the canvas render thread.

    Args:
        canvas_id: Canvas identifier
        title: New window title (optional)
        width: New window width in pixels (optional)
        height: New window height in pixels (optional)

    Returns:
        Success status
    """
    try:
        canvas = canvas_manager.get_canvas(canvas_id)
        if canvas is None:
            return {
                "success": False,
                "error": f"Canvas '{canvas_id}' not found",
            }

        # Ensure canvas is running
        if not canvas._running:
            canvas.run_async()

        # Prepare command data
        cmd_data: dict[str, Any] = {"canvas_id": canvas_id}
        if title is not None:
            cmd_data["title"] = title
        if width is not None:
            cmd_data["width"] = width
        if height is not None:
            cmd_data["height"] = height

        # Send command via shared memory
        shm_manager = SharedMemoryManager(name_prefix=f"canvas_{canvas_id}")
        try:
            shm_manager.attach_regions()

            seq_num = shm_manager.write_command(CommandType.UPDATE_STATE, **cmd_data)

            logger.info(f"Sent UPDATE_STATE command to '{canvas_id}' (seq={seq_num})")

            return {
                "success": True,
                "data": {
                    "canvas_id": canvas_id,
                    "command": "UPDATE_STATE",
                    "seq_num": seq_num,
                    "updates": cmd_data,
                },
            }

        finally:
            shm_manager.cleanup()

    except Exception as e:
        logger.error(f"Error updating canvas state for '{canvas_id}': {e}")
        return {
            "success": False,
            "error": str(e),
        }


@mcp.tool()
def shutdown_canvas(canvas_id: str) -> dict[str, Any]:
    """Shutdown a canvas window gracefully.

    Sends a SHUTDOWN command via shared memory and removes canvas from manager.

    Args:
        canvas_id: Canvas identifier

    Returns:
        Success status
    """
    try:
        canvas = canvas_manager.get_canvas(canvas_id)
        if canvas is None:
            return {
                "success": False,
                "error": f"Canvas '{canvas_id}' not found",
            }

        # Send shutdown command via shared memory
        if canvas._running:
            shm_manager = SharedMemoryManager(name_prefix=f"canvas_{canvas_id}")
            try:
                shm_manager.attach_regions()
                seq_num = shm_manager.write_command(
                    CommandType.SHUTDOWN, canvas_id=canvas_id
                )
                logger.info(f"Sent SHUTDOWN command to '{canvas_id}' (seq={seq_num})")
            finally:
                shm_manager.cleanup()

        # Stop canvas and cleanup
        canvas.stop()

        # Remove from manager
        del canvas_manager.canvases[canvas_id]

        logger.info(f"Shutdown canvas '{canvas_id}'")

        return {
            "success": True,
            "data": {"canvas_id": canvas_id, "shutdown": True},
        }

    except Exception as e:
        logger.error(f"Error shutting down canvas '{canvas_id}': {e}")
        return {
            "success": False,
            "error": str(e),
        }


# ==============================================================================
# Basic widget tools
# ==============================================================================


@mcp.tool()
def add_button(
    canvas_id: str,
    widget_id: str,
    label: str = "Button",
) -> dict[str, Any]:
    """Add a button widget to the canvas.

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        label: Button label text

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = ButtonWidget(widget_id, label=label)
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding button '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def add_small_button(
    canvas_id: str,
    widget_id: str,
    label: str = "Button",
) -> dict[str, Any]:
    """Add a small button widget to the canvas.

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        label: Button label text

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = SmallButtonWidget(widget_id, label=label)
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding small button '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def add_arrow_button(
    canvas_id: str,
    widget_id: str,
    direction: int = 0,
) -> dict[str, Any]:
    """Add an arrow button widget to the canvas.

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        direction: Arrow direction (0=left, 1=right, 2=up, 3=down)

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = ArrowButtonWidget(widget_id, direction=direction)
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding arrow button '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def add_invisible_button(
    canvas_id: str,
    widget_id: str,
    width: float = 100.0,
    height: float = 100.0,
) -> dict[str, Any]:
    """Add an invisible button widget to the canvas.

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        width: Button width in pixels
        height: Button height in pixels

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = InvisibleButtonWidget(widget_id, size=(width, height))
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding invisible button '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def add_text(
    canvas_id: str,
    widget_id: str,
    text: str = "",
) -> dict[str, Any]:
    """Add a text widget to the canvas.

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        text: Text to display

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = TextWidget(widget_id, text=text)
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding text '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def add_colored_text(
    canvas_id: str,
    widget_id: str,
    text: str = "",
    r: float = 1.0,
    g: float = 1.0,
    b: float = 1.0,
    a: float = 1.0,
) -> dict[str, Any]:
    """Add a colored text widget to the canvas.

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        text: Text to display
        r: Red channel (0.0-1.0)
        g: Green channel (0.0-1.0)
        b: Blue channel (0.0-1.0)
        a: Alpha channel (0.0-1.0)

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = TextColoredWidget(widget_id, text=text, color=(r, g, b, a))
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding colored text '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def add_disabled_text(
    canvas_id: str,
    widget_id: str,
    text: str = "",
) -> dict[str, Any]:
    """Add a disabled (grayed-out) text widget to the canvas.

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        text: Text to display

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = TextDisabledWidget(widget_id, text=text)
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding disabled text '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def add_wrapped_text(
    canvas_id: str,
    widget_id: str,
    text: str = "",
) -> dict[str, Any]:
    """Add a word-wrapped text widget to the canvas.

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        text: Text to display (wraps at window edge)

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = TextWrappedWidget(widget_id, text=text)
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding wrapped text '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def add_bullet_text(
    canvas_id: str,
    widget_id: str,
    text: str = "",
) -> dict[str, Any]:
    """Add a bullet-point text widget to the canvas.

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        text: Text to display after the bullet

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = BulletTextWidget(widget_id, text=text)
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding bullet text '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def add_bullet(
    canvas_id: str,
    widget_id: str,
) -> dict[str, Any]:
    """Add a bullet point widget to the canvas.

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = BulletWidget(widget_id)
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding bullet '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def add_label_text(
    canvas_id: str,
    widget_id: str,
    label: str = "Label",
    text: str = "",
) -> dict[str, Any]:
    """Add a label + value text widget to the canvas.

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        label: Label name shown on the left
        text: Value text shown on the right

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = LabelTextWidget(widget_id, label=label, text=text)
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding label text '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def add_input_text(
    canvas_id: str,
    widget_id: str,
    label: str = "Input",
    value: str = "",
) -> dict[str, Any]:
    """Add a text input widget to the canvas.

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        label: Input field label
        value: Initial text value

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = InputTextWidget(widget_id, label=label, value=value)
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding input text '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def add_checkbox(
    canvas_id: str,
    widget_id: str,
    label: str = "Checkbox",
    checked: bool = False,
) -> dict[str, Any]:
    """Add a checkbox widget to the canvas.

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        label: Checkbox label text
        checked: Initial checked state

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = CheckboxWidget(widget_id, label=label, checked=checked)
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding checkbox '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


# ==============================================================================
# Input widget tools
# ==============================================================================


@mcp.tool()
def add_input_int(
    canvas_id: str,
    widget_id: str,
    label: str = "Int",
    value: int = 0,
) -> dict[str, Any]:
    """Add an integer input widget to the canvas.

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        label: Input field label
        value: Initial integer value

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = InputIntWidget(widget_id, label=label, value=value)
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding input int '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def add_input_float(
    canvas_id: str,
    widget_id: str,
    label: str = "Float",
    value: float = 0.0,
) -> dict[str, Any]:
    """Add a float input widget to the canvas.

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        label: Input field label
        value: Initial float value

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = InputFloatWidget(widget_id, label=label, value=value)
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding input float '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def add_input_double(
    canvas_id: str,
    widget_id: str,
    label: str = "Double",
    value: float = 0.0,
) -> dict[str, Any]:
    """Add a double-precision float input widget to the canvas.

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        label: Input field label
        value: Initial double value

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = InputDoubleWidget(widget_id, label=label, value=value)
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding input double '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def add_input_scalar(
    canvas_id: str,
    widget_id: str,
    label: str = "Scalar",
    value: float = 0.0,
) -> dict[str, Any]:
    """Add a generic scalar input widget to the canvas.

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        label: Input field label
        value: Initial scalar value

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = InputScalarWidget(widget_id, label=label, value=value)
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding input scalar '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def add_radio_button(
    canvas_id: str,
    widget_id: str,
    label: str = "Option",
    active: bool = False,
) -> dict[str, Any]:
    """Add a radio button widget to the canvas.

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        label: Radio button label
        active: Whether this button is initially selected

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = RadioButtonWidget(widget_id, label=label, active=active)
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding radio button '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def add_combo(
    canvas_id: str,
    widget_id: str,
    label: str = "Combo",
    items: list[str] | None = None,
    current_item: int = 0,
) -> dict[str, Any]:
    """Add a combo box (dropdown) widget to the canvas.

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        label: Combo box label
        items: List of selectable items
        current_item: Index of the initially selected item

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = ComboWidget(
            widget_id, label=label, items=items or [], current_item=current_item
        )
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding combo '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def add_list_box(
    canvas_id: str,
    widget_id: str,
    label: str = "List",
    items: list[str] | None = None,
    current_item: int = 0,
) -> dict[str, Any]:
    """Add a list box widget to the canvas.

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        label: List box label
        items: List of selectable items
        current_item: Index of the initially selected item

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = ListBoxWidget(
            widget_id, label=label, items=items or [], current_item=current_item
        )
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding list box '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def add_selectable(
    canvas_id: str,
    widget_id: str,
    label: str = "Item",
    selected: bool = False,
) -> dict[str, Any]:
    """Add a selectable item widget to the canvas.

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        label: Item label text
        selected: Whether the item is initially selected

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = SelectableWidget(widget_id, label=label, selected=selected)
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding selectable '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def add_checkbox_flags(
    canvas_id: str,
    widget_id: str,
    label: str = "Flag",
    flags: int = 0,
    flags_value: int = 0,
) -> dict[str, Any]:
    """Add a checkbox-flags widget to the canvas.

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        label: Checkbox label text
        flags: Current flags bitmask
        flags_value: Bit flag this checkbox controls

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = CheckboxFlagsWidget(
            widget_id, label=label, flags=flags, flags_value=flags_value
        )
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding checkbox flags '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


# ==============================================================================
# Color widget tools
# ==============================================================================


@mcp.tool()
def add_color_picker(
    canvas_id: str,
    widget_id: str,
    label: str = "Color",
    r: float = 1.0,
    g: float = 0.0,
    b: float = 0.0,
    a: float = 1.0,
) -> dict[str, Any]:
    """Add a color picker widget (RGBA) to the canvas.

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        label: Color picker label
        r: Initial red channel (0.0-1.0)
        g: Initial green channel (0.0-1.0)
        b: Initial blue channel (0.0-1.0)
        a: Initial alpha channel (0.0-1.0)

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = ColorPickerWidget(widget_id, label=label, color=(r, g, b, a))
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding color picker '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def add_color_picker3(
    canvas_id: str,
    widget_id: str,
    label: str = "Color",
    r: float = 1.0,
    g: float = 0.0,
    b: float = 0.0,
) -> dict[str, Any]:
    """Add a color picker widget (RGB) to the canvas.

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        label: Color picker label
        r: Initial red channel (0.0-1.0)
        g: Initial green channel (0.0-1.0)
        b: Initial blue channel (0.0-1.0)

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = ColorPicker3Widget(widget_id, label=label, color=(r, g, b))
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding color picker3 '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def add_color_edit3(
    canvas_id: str,
    widget_id: str,
    label: str = "Color",
    r: float = 1.0,
    g: float = 0.0,
    b: float = 0.0,
) -> dict[str, Any]:
    """Add a compact color editor widget (RGB) to the canvas.

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        label: Color editor label
        r: Initial red channel (0.0-1.0)
        g: Initial green channel (0.0-1.0)
        b: Initial blue channel (0.0-1.0)

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = ColorEdit3Widget(widget_id, label=label, color=(r, g, b))
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding color edit3 '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def add_color_edit4(
    canvas_id: str,
    widget_id: str,
    label: str = "Color",
    r: float = 1.0,
    g: float = 0.0,
    b: float = 0.0,
    a: float = 1.0,
) -> dict[str, Any]:
    """Add a compact color editor widget (RGBA) to the canvas.

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        label: Color editor label
        r: Initial red channel (0.0-1.0)
        g: Initial green channel (0.0-1.0)
        b: Initial blue channel (0.0-1.0)
        a: Initial alpha channel (0.0-1.0)

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = ColorEdit4Widget(widget_id, label=label, color=(r, g, b, a))
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding color edit4 '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def add_color_button(
    canvas_id: str,
    widget_id: str,
    r: float = 1.0,
    g: float = 0.0,
    b: float = 0.0,
    a: float = 1.0,
) -> dict[str, Any]:
    """Add a color button widget to the canvas.

    A color button displays a solid color swatch that can be clicked.

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        r: Red channel (0.0-1.0)
        g: Green channel (0.0-1.0)
        b: Blue channel (0.0-1.0)
        a: Alpha channel (0.0-1.0)

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = ColorButtonWidget(widget_id, color=(r, g, b, a))
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding color button '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


# ==============================================================================
# Progress widget tools
# ==============================================================================


@mcp.tool()
def add_progress_bar(
    canvas_id: str,
    widget_id: str,
    value: float = 0.0,
    overlay: str = "",
    width: float = -1.0,
    height: float = 0.0,
) -> dict[str, Any]:
    """Add a progress bar widget to the canvas.

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        value: Progress value from 0.0 to 1.0
        overlay: Optional overlay text shown on the bar
        width: Bar width (-1 for full width)
        height: Bar height (0 for default)

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = ProgressBarWidget(
            widget_id, fraction=value, overlay=overlay, size=(width, height)
        )
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding progress bar '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def add_loading_indicator(
    canvas_id: str,
    widget_id: str,
    radius: float = 15.0,
    speed: float = 1.5,
    thickness: float = 3.5,
) -> dict[str, Any]:
    """Add a circular loading indicator widget to the canvas.

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        radius: Indicator radius in pixels
        speed: Animation speed multiplier
        thickness: Ring thickness in pixels

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = LoadingIndicatorWidget(
            widget_id, radius=radius, speed=speed, thickness=thickness
        )
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding loading indicator '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def add_status_bar(
    canvas_id: str,
    widget_id: str,
    text: str = "",
    progress: float = -1.0,
) -> dict[str, Any]:
    """Add a status bar widget to the canvas.

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        text: Status message text
        progress: Optional progress value 0.0-1.0, or -1 to hide

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = StatusBarWidget(widget_id, text=text, progress=progress)
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding status bar '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


# ==============================================================================
# Slider widget tools
# ==============================================================================


@mcp.tool()
def add_slider_int(
    canvas_id: str,
    widget_id: str,
    label: str = "Slider",
    value: int = 0,
    v_min: int = 0,
    v_max: int = 100,
) -> dict[str, Any]:
    """Add an integer slider widget to the canvas.

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        label: Slider label
        value: Initial integer value
        v_min: Minimum slider value
        v_max: Maximum slider value

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = SliderIntWidget(
            widget_id, label=label, value=value, v_min=v_min, v_max=v_max
        )
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding slider int '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def add_slider_float(
    canvas_id: str,
    widget_id: str,
    label: str = "Slider",
    value: float = 0.0,
    v_min: float = 0.0,
    v_max: float = 1.0,
) -> dict[str, Any]:
    """Add a float slider widget to the canvas.

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        label: Slider label
        value: Initial float value
        v_min: Minimum slider value
        v_max: Maximum slider value

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = SliderFloatWidget(
            widget_id, label=label, value=value, v_min=v_min, v_max=v_max
        )
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding slider float '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def add_drag_int(
    canvas_id: str,
    widget_id: str,
    label: str = "Drag",
    value: int = 0,
    v_speed: float = 1.0,
    v_min: int = 0,
    v_max: int = 0,
) -> dict[str, Any]:
    """Add a draggable integer input widget to the canvas.

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        label: Widget label
        value: Initial integer value
        v_speed: Drag speed multiplier
        v_min: Minimum value (0 for no limit)
        v_max: Maximum value (0 for no limit)

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = DragIntWidget(
            widget_id,
            label=label,
            value=value,
            v_speed=v_speed,
            v_min=v_min,
            v_max=v_max,
        )
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding drag int '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def add_drag_float(
    canvas_id: str,
    widget_id: str,
    label: str = "Drag",
    value: float = 0.0,
    v_speed: float = 0.01,
    v_min: float = 0.0,
    v_max: float = 0.0,
) -> dict[str, Any]:
    """Add a draggable float input widget to the canvas.

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        label: Widget label
        value: Initial float value
        v_speed: Drag speed multiplier
        v_min: Minimum value (0.0 for no limit)
        v_max: Maximum value (0.0 for no limit)

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = DragFloatWidget(
            widget_id,
            label=label,
            value=value,
            v_speed=v_speed,
            v_min=v_min,
            v_max=v_max,
        )
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding drag float '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


# ==============================================================================
# Container widget tools
# ==============================================================================


@mcp.tool()
def add_window(
    canvas_id: str,
    widget_id: str,
    title: str = "Window",
    closable: bool = True,
) -> dict[str, Any]:
    """Add a child window widget to the canvas.

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        title: Window title bar text
        closable: Whether to show a close button

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = WindowWidget(widget_id, title=title, closable=closable)
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding window '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def add_child_window(
    canvas_id: str,
    widget_id: str,
    width: float = 0.0,
    height: float = 0.0,
    border: bool = False,
) -> dict[str, Any]:
    """Add a child window container widget to the canvas.

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        width: Child window width (0 for auto)
        height: Child window height (0 for auto)
        border: Whether to draw a border

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = ChildWindowWidget(widget_id, size=(width, height), border=border)
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding child window '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def add_group(
    canvas_id: str,
    widget_id: str,
) -> dict[str, Any]:
    """Add a group container widget to the canvas.

    Groups allow treating multiple widgets as a single unit.

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = GroupWidget(widget_id)
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding group '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def add_collapsing_header(
    canvas_id: str,
    widget_id: str,
    label: str = "Header",
    default_open: bool = False,
) -> dict[str, Any]:
    """Add a collapsing header widget to the canvas.

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        label: Header label text
        default_open: Whether the header is expanded by default

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = CollapsingHeaderWidget(
            widget_id, label=label, default_open=default_open
        )
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding collapsing header '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def add_tab_bar(
    canvas_id: str,
    widget_id: str,
) -> dict[str, Any]:
    """Add a tab bar container widget to the canvas.

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = TabBarWidget(widget_id)
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding tab bar '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def add_tab_item(
    canvas_id: str,
    widget_id: str,
    label: str = "Tab",
    closable: bool = False,
) -> dict[str, Any]:
    """Add a tab item to a tab bar widget on the canvas.

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        label: Tab label text
        closable: Whether the tab shows a close button

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = TabItemWidget(widget_id, label=label, closable=closable)
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding tab item '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def add_separator(
    canvas_id: str,
    widget_id: str,
    vertical: bool = False,
) -> dict[str, Any]:
    """Add a separator line widget to the canvas.

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        vertical: If True, renders a vertical separator line

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = SeparatorWidget(widget_id, vertical=vertical)
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding separator '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def add_spacing(
    canvas_id: str,
    widget_id: str,
    count: int = 1,
) -> dict[str, Any]:
    """Add vertical spacing widget to the canvas.

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        count: Number of blank lines to insert

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = SpacingWidget(widget_id, count=count)
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding spacing '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def add_dummy(
    canvas_id: str,
    widget_id: str,
    width: float = 0.0,
    height: float = 0.0,
) -> dict[str, Any]:
    """Add a dummy invisible placeholder widget to the canvas.

    Useful for reserving space in layouts.

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        width: Placeholder width in pixels
        height: Placeholder height in pixels

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = DummyWidget(widget_id, size=(width, height))
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding dummy '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


# ==============================================================================
# Display widget tools
# ==============================================================================


@mcp.tool()
def add_plot_lines(
    canvas_id: str,
    widget_id: str,
    label: str = "Plot",
    values: list[float] | None = None,
    overlay_text: str = "",
    scale_min: float | None = None,
    scale_max: float | None = None,
    graph_width: float = 0.0,
    graph_height: float = 0.0,
) -> dict[str, Any]:
    """Add a sparkline plot widget to the canvas.

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        label: Plot label
        values: List of float values to plot
        overlay_text: Text overlaid on the plot
        scale_min: Minimum Y scale (None for auto)
        scale_max: Maximum Y scale (None for auto)
        graph_width: Graph width (0 for auto)
        graph_height: Graph height (0 for default)

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = PlotLinesWidget(
            widget_id,
            label=label,
            values=values or [],
            overlay_text=overlay_text,
            scale_min=scale_min,
            scale_max=scale_max,
            graph_size=(graph_width, graph_height),
        )
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding plot lines '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def add_help_marker(
    canvas_id: str,
    widget_id: str,
    description: str = "",
    marker: str = "(?)",
) -> dict[str, Any]:
    """Add a help marker widget to the canvas.

    Displays a small marker that shows a tooltip on hover.

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        description: Tooltip text shown on hover
        marker: The marker symbol to display (default: '(?)')

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = HelpMarkerWidget(widget_id, description=description, marker=marker)
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding help marker '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


# ==============================================================================
# Menu widget tools
# ==============================================================================


@mcp.tool()
def add_menu_bar(
    canvas_id: str,
    widget_id: str,
) -> dict[str, Any]:
    """Add a menu bar widget to the canvas.

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = MenuBarWidget(widget_id)
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding menu bar '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def add_menu(
    canvas_id: str,
    widget_id: str,
    label: str = "Menu",
    enabled: bool = True,
) -> dict[str, Any]:
    """Add a menu widget to the canvas.

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        label: Menu label text
        enabled: Whether the menu is interactive

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = MenuWidget(widget_id, label=label, enabled=enabled)
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding menu '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def add_menu_item(
    canvas_id: str,
    widget_id: str,
    label: str = "Item",
    shortcut: str | None = None,
    selected: bool = False,
    enabled: bool = True,
) -> dict[str, Any]:
    """Add a menu item widget to the canvas.

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        label: Item label text
        shortcut: Optional keyboard shortcut hint (e.g. 'Ctrl+S')
        selected: Whether the item shows a checkmark
        enabled: Whether the item is interactive

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = MenuItemWidget(
            widget_id,
            label=label,
            shortcut=shortcut,
            selected=selected,
            enabled=enabled,
        )
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding menu item '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def add_tree_node(
    canvas_id: str,
    widget_id: str,
    label: str = "Node",
    default_open: bool = False,
) -> dict[str, Any]:
    """Add a tree node widget to the canvas.

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        label: Node label text
        default_open: Whether the node is expanded by default

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = TreeNodeWidget(widget_id, label=label, default_open=default_open)
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding tree node '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def add_tooltip(
    canvas_id: str,
    widget_id: str,
    text: str = "",
) -> dict[str, Any]:
    """Add a tooltip widget to the canvas.

    The tooltip is shown when the preceding widget is hovered.

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        text: Tooltip text to display

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = TooltipWidget(widget_id, text=text)
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding tooltip '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def add_popup(
    canvas_id: str,
    widget_id: str,
    title: str = "Popup",
    modal: bool = False,
) -> dict[str, Any]:
    """Add a popup window widget to the canvas.

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        title: Popup title text
        modal: If True, the popup blocks input to the rest of the UI

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = PopupWidget(widget_id, title=title, modal=modal)
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding popup '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def add_context_menu(
    canvas_id: str,
    widget_id: str,
) -> dict[str, Any]:
    """Add a right-click context menu widget to the canvas.

    The context menu opens when the user right-clicks the preceding widget.

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = ContextMenuWidget(widget_id)
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding context menu '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


# ==============================================================================
# Plotting widget tools (ImPlot)
# ==============================================================================


@mcp.tool()
def add_line_chart(
    canvas_id: str,
    widget_id: str,
    title: str = "Line Chart",
    x_data: list[float] | None = None,
    y_data: list[float] | None = None,
    width: float = -1.0,
    height: float = -1.0,
) -> dict[str, Any]:
    """Add a line chart widget to the canvas (requires ImPlot).

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        title: Chart title
        x_data: X-axis data points
        y_data: Y-axis data points
        width: Plot width (-1 for full width)
        height: Plot height (-1 for auto)

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = LineChartWidget(
            widget_id,
            title=title,
            x_data=x_data or [],
            y_data=y_data or [],
            size=(width, height),
        )
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding line chart '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def add_bar_chart(
    canvas_id: str,
    widget_id: str,
    title: str = "Bar Chart",
    values: list[float] | None = None,
    labels: list[str] | None = None,
    width: float = -1.0,
    height: float = -1.0,
) -> dict[str, Any]:
    """Add a bar chart widget to the canvas (requires ImPlot).

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        title: Chart title
        values: Bar height values
        labels: Labels for each bar
        width: Plot width (-1 for full width)
        height: Plot height (-1 for auto)

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = BarChartWidget(
            widget_id,
            title=title,
            values=values or [],
            labels=labels or [],
            size=(width, height),
        )
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding bar chart '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def add_scatter_plot(
    canvas_id: str,
    widget_id: str,
    title: str = "Scatter Plot",
    x_data: list[float] | None = None,
    y_data: list[float] | None = None,
    width: float = -1.0,
    height: float = -1.0,
) -> dict[str, Any]:
    """Add a scatter plot widget to the canvas (requires ImPlot).

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        title: Chart title
        x_data: X-axis data points
        y_data: Y-axis data points
        width: Plot width (-1 for full width)
        height: Plot height (-1 for auto)

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = ScatterPlotWidget(
            widget_id,
            title=title,
            x_data=x_data or [],
            y_data=y_data or [],
            size=(width, height),
        )
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding scatter plot '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def add_pie_chart(
    canvas_id: str,
    widget_id: str,
    values: list[float] | None = None,
    labels: list[str] | None = None,
    center_x: float = 0.5,
    center_y: float = 0.5,
    radius: float = 0.4,
) -> dict[str, Any]:
    """Add a pie chart widget to the canvas (requires ImPlot).

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        values: Slice values
        labels: Labels for each slice
        center_x: X position of chart center (normalized 0-1)
        center_y: Y position of chart center (normalized 0-1)
        radius: Chart radius (normalized 0-1)

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = PieChartWidget(
            widget_id,
            values=values or [],
            labels=labels or [],
            center=(center_x, center_y),
            radius=radius,
        )
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding pie chart '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def add_heatmap(
    canvas_id: str,
    widget_id: str,
    title: str = "Heatmap",
    values: list[list[float]] | None = None,
    width: float = -1.0,
    height: float = -1.0,
) -> dict[str, Any]:
    """Add a heatmap widget to the canvas (requires ImPlot).

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        title: Heatmap title
        values: 2D list of float values (rows x cols)
        width: Plot width (-1 for full width)
        height: Plot height (-1 for auto)

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = HeatmapWidget(
            widget_id,
            title=title,
            values=values or [],
            size=(width, height),
        )
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding heatmap '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def add_histogram(
    canvas_id: str,
    widget_id: str,
    title: str = "Histogram",
    values: list[float] | None = None,
    bins: int = 10,
    width: float = -1.0,
    height: float = -1.0,
) -> dict[str, Any]:
    """Add a histogram widget to the canvas (requires ImPlot).

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        title: Chart title
        values: Raw data values to bin
        bins: Number of histogram bins
        width: Plot width (-1 for full width)
        height: Plot height (-1 for auto)

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = HistogramWidget(
            widget_id,
            title=title,
            values=values or [],
            bins=bins,
            size=(width, height),
        )
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding histogram '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def add_realtime_plot(
    canvas_id: str,
    widget_id: str,
    title: str = "Realtime Plot",
    max_points: int = 1000,
    width: float = -1.0,
    height: float = -1.0,
) -> dict[str, Any]:
    """Add a realtime scrolling plot widget to the canvas (requires ImPlot).

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        title: Plot title
        max_points: Maximum number of data points to keep in the buffer
        width: Plot width (-1 for full width)
        height: Plot height (-1 for auto)

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = RealtimePlotWidget(
            widget_id,
            title=title,
            max_points=max_points,
            size=(width, height),
        )
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding realtime plot '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def add_error_bars(
    canvas_id: str,
    widget_id: str,
    title: str = "Error Bars",
    x_data: list[float] | None = None,
    y_data: list[float] | None = None,
    errors: list[float] | None = None,
    width: float = -1.0,
    height: float = -1.0,
) -> dict[str, Any]:
    """Add an error bar chart widget to the canvas (requires ImPlot).

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        title: Chart title
        x_data: X-axis data points
        y_data: Y-axis data points (centers)
        errors: Error magnitude for each point
        width: Plot width (-1 for full width)
        height: Plot height (-1 for auto)

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = ErrorBarsWidget(
            widget_id,
            title=title,
            x_data=x_data or [],
            y_data=y_data or [],
            errors=errors or [],
            size=(width, height),
        )
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding error bars '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


# ==============================================================================
# Phase 3: Theme tools
# ==============================================================================


@mcp.tool()
def apply_theme(theme_name: str) -> dict[str, Any]:
    """Apply a named theme to the ImGui style.

    Theme must be applied from the render thread — if a canvas is running this
    enqueues the call; otherwise it is applied immediately (no canvas context).

    Args:
        theme_name: One of: dark, light, cherry, nord, dracula, gruvbox,
                    solarized_dark, monokai, material (case-insensitive)

    Returns:
        Success status and applied theme name
    """
    try:
        key = theme_name.lower()
        if not theme_manager.apply_theme_by_name(key):
            available = theme_manager.list_themes()
            return {
                "success": False,
                "error": f"Theme '{theme_name}' not found. Available: {available}",
            }
        return {"success": True, "data": {"theme": key}}
    except Exception as e:
        logger.error(f"Error applying theme '{theme_name}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def list_themes() -> dict[str, Any]:
    """List all registered theme names.

    Returns:
        Success status and list of theme name strings
    """
    try:
        return {"success": True, "data": {"themes": theme_manager.list_themes()}}
    except Exception as e:
        logger.error(f"Error listing themes: {e}")
        return {"success": False, "error": str(e)}


# ==============================================================================
# Phase 3: Layout tools
# ==============================================================================


@mcp.tool()
def set_layout_mode(mode: str) -> dict[str, Any]:
    """Set the global layout mode for widget arrangement.

    Args:
        mode: One of: horizontal, vertical, grid, stack, free

    Returns:
        Success status and applied mode
    """
    try:
        try:
            layout_mode = LayoutMode(mode.lower())
        except ValueError:
            valid = [m.value for m in LayoutMode]
            return {"success": False, "error": f"Invalid mode '{mode}'. Valid: {valid}"}
        layout_manager.set_mode(layout_mode)
        return {"success": True, "data": {"mode": mode}}
    except Exception as e:
        logger.error(f"Error setting layout mode '{mode}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def set_layout_spacing(spacing: float) -> dict[str, Any]:
    """Set the spacing between widgets in the current layout.

    Args:
        spacing: Spacing in pixels (>= 0)

    Returns:
        Success status and applied spacing
    """
    try:
        layout_manager.set_spacing(max(0.0, spacing))
        return {"success": True, "data": {"spacing": spacing}}
    except Exception as e:
        logger.error(f"Error setting layout spacing: {e}")
        return {"success": False, "error": str(e)}


# ==============================================================================
# Phase 3: Notification tools
# ==============================================================================


@mcp.tool()
def show_notification(
    title: str,
    message: str,
    type: str = "info",
    duration: float = 3.0,
) -> dict[str, Any]:
    """Show a toast notification overlay.

    Args:
        title: Notification title
        message: Notification body text
        type: One of: info, success, warning, error
        duration: Display duration in seconds (0 for persistent)

    Returns:
        Success status
    """
    try:
        try:
            ntype = NotificationType(type.lower())
        except ValueError:
            valid = [t.value for t in NotificationType]
            return {"success": False, "error": f"Invalid type '{type}'. Valid: {valid}"}
        notification_manager.add(title, message, ntype, duration)
        return {"success": True, "data": {"title": title, "type": type}}
    except Exception as e:
        logger.error(f"Error showing notification: {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def clear_notifications() -> dict[str, Any]:
    """Clear all active notifications.

    Returns:
        Success status
    """
    try:
        notification_manager.clear_all()
        return {"success": True, "data": {}}
    except Exception as e:
        logger.error(f"Error clearing notifications: {e}")
        return {"success": False, "error": str(e)}


# ==============================================================================
# Phase 3: Animation tools
# ==============================================================================


@mcp.tool()
def create_animation(
    name: str,
    start_value: float,
    end_value: float,
    duration: float,
    easing: str = "linear",
    loop: bool = False,
) -> dict[str, Any]:
    """Create a named animation for smooth value interpolation.

    Args:
        name: Unique animation name
        start_value: Starting numeric value
        end_value: Ending numeric value
        duration: Animation duration in seconds
        easing: Easing function name (linear, ease_in_quad, ease_out_quad,
                ease_in_out_quad, ease_in_cubic, ease_out_cubic, ease_in_out_cubic,
                ease_in_sine, ease_out_sine, ease_in_out_sine, ease_in_expo,
                ease_out_expo, ease_in_out_expo, bounce, elastic)
        loop: Whether the animation should loop

    Returns:
        Success status and animation name
    """
    try:
        try:
            easing_fn = EasingFunction(easing.lower())
        except ValueError:
            valid = [e.value for e in EasingFunction]
            return {
                "success": False,
                "error": f"Invalid easing '{easing}'. Valid: {valid}",
            }
        animation_manager.create(
            name=name,
            start_value=start_value,
            end_value=end_value,
            duration=duration,
            easing=easing_fn,
            loop=loop,
        )
        return {"success": True, "data": {"name": name}}
    except Exception as e:
        logger.error(f"Error creating animation '{name}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def start_animation(name: str) -> dict[str, Any]:
    """Start a previously created animation.

    Args:
        name: Animation name

    Returns:
        Success status
    """
    try:
        if not animation_manager.start(name):
            return {"success": False, "error": f"Animation '{name}' not found"}
        return {"success": True, "data": {"name": name}}
    except Exception as e:
        logger.error(f"Error starting animation '{name}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def stop_animation(name: str) -> dict[str, Any]:
    """Stop a running animation, jumping it to its end value.

    Args:
        name: Animation name

    Returns:
        Success status
    """
    try:
        if not animation_manager.stop(name):
            return {"success": False, "error": f"Animation '{name}' not found"}
        return {"success": True, "data": {"name": name}}
    except Exception as e:
        logger.error(f"Error stopping animation '{name}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def get_animation_value(name: str) -> dict[str, Any]:
    """Get the current interpolated value of an animation.

    Args:
        name: Animation name

    Returns:
        Success status and current value
    """
    try:
        value = animation_manager.get_value(name)
        if value is None:
            return {"success": False, "error": f"Animation '{name}' not found"}
        return {"success": True, "data": {"name": name, "value": value}}
    except Exception as e:
        logger.error(f"Error getting animation value '{name}': {e}")
        return {"success": False, "error": str(e)}


# ==============================================================================
# Phase 3: Data binding tools
# ==============================================================================


@mcp.tool()
def set_data(path: str, value: Any) -> dict[str, Any]:
    """Set a value in the reactive data store.

    Args:
        path: Dot-notation path (e.g. "user.name", "settings.theme")
        value: Value to store

    Returns:
        Success status
    """
    try:
        data_store.set(path, value)
        return {"success": True, "data": {"path": path, "value": value}}
    except Exception as e:
        logger.error(f"Error setting data '{path}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def get_data(path: str, default: Any = None) -> dict[str, Any]:
    """Get a value from the reactive data store.

    Args:
        path: Dot-notation path (e.g. "user.name")
        default: Value to return if path not found

    Returns:
        Success status and value
    """
    try:
        value = data_store.get(path, default)
        return {"success": True, "data": {"path": path, "value": value}}
    except Exception as e:
        logger.error(f"Error getting data '{path}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def bind_data(
    source_path: str,
    target_widget: str,
    target_property: str,
    bidirectional: bool = False,
) -> dict[str, Any]:
    """Bind a data store path to a widget property.

    When the data at source_path changes, the widget property is updated
    automatically.

    Args:
        source_path: Dot-notation data path (e.g. "user.name")
        target_widget: Widget ID to bind to
        target_property: Widget property name (e.g. "text", "value")
        bidirectional: Enable two-way binding

    Returns:
        Success status
    """
    try:
        binding_manager.bind(
            source_path, target_widget, target_property, bidirectional=bidirectional
        )
        return {
            "success": True,
            "data": {
                "source": source_path,
                "target": f"{target_widget}.{target_property}",
            },
        }
    except Exception as e:
        logger.error(f"Error binding data '{source_path}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def unbind_data(source_path: str, target_widget: str | None = None) -> dict[str, Any]:
    """Remove data bindings for a store path.

    Args:
        source_path: Data path to unbind
        target_widget: If provided, removes only the binding for this widget;
                       otherwise removes all bindings for the path

    Returns:
        Success status
    """
    try:
        binding_manager.unbind(source_path, target_widget)
        return {"success": True, "data": {"source": source_path}}
    except Exception as e:
        logger.error(f"Error unbinding data '{source_path}': {e}")
        return {"success": False, "error": str(e)}


# ==============================================================================
# Phase 3: File dialog tools
# ==============================================================================


@mcp.tool()
def add_file_dialog(
    canvas_id: str,
    widget_id: str,
    button_label: str = "Browse...",
    mode: str = "open_file",
    title: str = "Select File",
    filters: list[str] | None = None,
) -> dict[str, Any]:
    """Add a file dialog widget to the canvas.

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        button_label: Label shown on the browse button
        mode: One of: open_file, open_folder, save_file
        title: Dialog window title
        filters: File type filters (e.g. ["*.py", "*.txt"])

    Returns:
        Success status and serialized widget data
    """
    try:
        valid_modes = [
            FileDialogMode.OPEN_FILE,
            FileDialogMode.OPEN_FOLDER,
            FileDialogMode.SAVE_FILE,
        ]
        if mode not in valid_modes:
            return {
                "success": False,
                "error": f"Invalid mode '{mode}'. Valid: {valid_modes}",
            }
        widget = FileDialogWidget(
            widget_id,
            button_label=button_label,
            mode=mode,
            title=title,
            filters=filters,
        )
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding file dialog '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def show_message_dialog(
    title: str,
    message: str,
    dialog_type: str = "info",
) -> dict[str, Any]:
    """Show a native OS message dialog.

    Args:
        title: Dialog title
        message: Dialog message body
        dialog_type: One of: info, warning, error

    Returns:
        Success status
    """
    try:
        match dialog_type.lower():
            case "info":
                MessageDialog.info(title, message)
            case "warning":
                MessageDialog.warning(title, message)
            case "error":
                MessageDialog.error(title, message)
            case _:
                return {
                    "success": False,
                    "error": f"Invalid dialog_type '{dialog_type}'. Valid: info, warning, error",
                }
        return {"success": True, "data": {"title": title, "type": dialog_type}}
    except Exception as e:
        logger.error(f"Error showing message dialog: {e}")
        return {"success": False, "error": str(e)}


# ---------------------------------------------------------------------------
# Phase 4: Serialization, Code Generation, Templates
# ---------------------------------------------------------------------------


@mcp.tool()
def export_canvas_json(canvas_id: str, filepath: str) -> dict[str, Any]:
    """Export a canvas to a JSON file.

    Args:
        canvas_id: Canvas identifier
        filepath: Destination file path (absolute or relative to cwd)

    Returns:
        Success status
    """
    try:
        canvas = canvas_manager.get_canvas(canvas_id)
        if not canvas:
            return {"success": False, "error": f"Canvas '{canvas_id}' not found"}
        ok = UIExporter.export_to_json(canvas, filepath)
        return {"success": ok, "data": {"filepath": filepath}}
    except Exception as e:
        logger.error(f"Error exporting canvas '{canvas_id}' to JSON: {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def export_canvas_python(canvas_id: str, filepath: str) -> dict[str, Any]:
    """Export a canvas as a standalone Python script.

    Args:
        canvas_id: Canvas identifier
        filepath: Destination .py file path (must be writable)

    Returns:
        Success status
    """
    try:
        canvas = canvas_manager.get_canvas(canvas_id)
        if not canvas:
            return {"success": False, "error": f"Canvas '{canvas_id}' not found"}
        code = CodeGenerator.generate_canvas_code(canvas)
        with open(filepath, "w") as f:
            f.write(code)
        logger.info(f"Exported canvas '{canvas_id}' Python code to {filepath}")
        return {"success": True, "data": {"filepath": filepath}}
    except OSError as e:
        logger.error(f"Cannot write to {filepath}: {e}")
        return {"success": False, "error": f"Cannot write to {filepath}: {e}"}
    except Exception as e:
        logger.error(f"Error exporting canvas '{canvas_id}' to Python: {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def import_canvas_json(filepath: str) -> dict[str, Any]:
    """Import a canvas from a JSON file.

    Args:
        filepath: Source JSON file path

    Returns:
        Newly created canvas state
    """
    try:
        canvas = UIImporter.import_from_json(filepath, canvas_manager)
        if not canvas:
            return {"success": False, "error": f"Failed to import from '{filepath}'"}
        return {"success": True, "data": canvas.state.to_dict()}
    except Exception as e:
        logger.error(f"Error importing canvas from '{filepath}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def get_canvas_json(canvas_id: str) -> dict[str, Any]:
    """Return the JSON representation of a canvas as a string (no file written).

    Args:
        canvas_id: Canvas identifier

    Returns:
        JSON string in data.json
    """
    try:
        canvas = canvas_manager.get_canvas(canvas_id)
        if not canvas:
            return {"success": False, "error": f"Canvas '{canvas_id}' not found"}
        json_str = UIExporter.export_canvas_state(canvas)
        return {"success": True, "data": {"json": json_str}}
    except Exception as e:
        logger.error(f"Error serializing canvas '{canvas_id}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def generate_canvas_code(canvas_id: str) -> dict[str, Any]:
    """Generate Python code for a canvas and return it as a string.

    Args:
        canvas_id: Canvas identifier

    Returns:
        Generated Python code in data.code
    """
    try:
        canvas = canvas_manager.get_canvas(canvas_id)
        if not canvas:
            return {"success": False, "error": f"Canvas '{canvas_id}' not found"}
        code = CodeGenerator.generate_canvas_code(canvas)
        return {"success": True, "data": {"code": code}}
    except Exception as e:
        logger.error(f"Error generating code for canvas '{canvas_id}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def generate_widget_snippet(
    widget_type: str,
    widget_id: str,
) -> dict[str, Any]:
    """Generate a single-line Python widget construction snippet.

    Args:
        widget_type: Widget class name (e.g. ButtonWidget)
        widget_id: Widget identifier

    Returns:
        Code snippet string in data.snippet
    """
    try:
        snippet = CodeGenerator.generate_widget_code_snippet(widget_type, widget_id)
        return {"success": True, "data": {"snippet": snippet}}
    except Exception as e:
        logger.error(f"Error generating widget snippet: {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def generate_component_template(name: str, widgets: list[str]) -> dict[str, Any]:
    """Generate a reusable Python component class for a set of widget types.

    Args:
        name: Component name (snake_case, e.g. my_panel)
        widgets: List of widget class names to include

    Returns:
        Generated class code in data.code
    """
    try:
        code = TemplateCodeGenerator.generate_component_template(name, widgets)
        return {"success": True, "data": {"code": code}}
    except Exception as e:
        logger.error(f"Error generating component template '{name}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def save_template(
    name: str,
    canvas_id: str,
    description: str = "",
) -> dict[str, Any]:
    """Save a canvas as a named template.

    Templates are stored in ~/.champi-imgui/templates/<name>.json.

    Args:
        name: Template name
        canvas_id: Canvas to save
        description: Optional description

    Returns:
        Success status
    """
    try:
        canvas = canvas_manager.get_canvas(canvas_id)
        if not canvas:
            return {"success": False, "error": f"Canvas '{canvas_id}' not found"}
        ok = template_manager.save_template(name, canvas, description)
        return {"success": ok, "data": {"name": name}}
    except Exception as e:
        logger.error(f"Error saving template '{name}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def load_template(name: str) -> dict[str, Any]:
    """Load a template and create a new canvas from it.

    Args:
        name: Template name

    Returns:
        Newly created canvas state
    """
    try:
        canvas = template_manager.load_template(name, canvas_manager)
        if not canvas:
            return {"success": False, "error": f"Template '{name}' not found"}
        return {"success": True, "data": canvas.state.to_dict()}
    except Exception as e:
        logger.error(f"Error loading template '{name}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def list_templates() -> dict[str, Any]:
    """List all available UI templates.

    Returns:
        List of templates with name and description
    """
    try:
        templates = template_manager.list_templates()
        return {"success": True, "data": {"templates": templates}}
    except Exception as e:
        logger.error(f"Error listing templates: {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def delete_template(name: str) -> dict[str, Any]:
    """Delete a saved template.

    Args:
        name: Template name

    Returns:
        Success status
    """
    try:
        ok = template_manager.delete_template(name)
        return {"success": ok, "data": {"name": name}}
    except Exception as e:
        logger.error(f"Error deleting template '{name}': {e}")
        return {"success": False, "error": str(e)}


# ==============================================================================
# Image widget tools
# ==============================================================================


@mcp.tool()
def add_image(
    canvas_id: str,
    widget_id: str,
    file_path: str,
    width: float = 200.0,
    height: float = 200.0,
) -> dict[str, Any]:
    """Add an image widget to the canvas. Displays a PNG or JPG image from a file path.

    The image is loaded lazily on the first render frame. If the file is not found
    or cannot be decoded, a placeholder text is shown instead of crashing.

    Args:
        canvas_id: Target canvas identifier
        widget_id: Unique identifier for the widget
        file_path: Absolute or relative path to a PNG or JPG image file
        width: Display width in pixels (default 200)
        height: Display height in pixels (default 200)

    Returns:
        Success status and serialized widget data
    """
    try:
        widget = ImageWidget(widget_id, file_path=file_path, width=width, height=height)
        return _create_widget_in_canvas(canvas_id, widget)
    except Exception as e:
        logger.error(f"Error adding image widget '{widget_id}': {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def update_image(
    canvas_id: str,
    widget_id: str,
    file_path: str | None = None,
    width: float | None = None,
    height: float | None = None,
) -> dict[str, Any]:
    """Update the file path or display dimensions of an existing image widget.

    Only the provided parameters are updated; omitted parameters are left unchanged.

    Args:
        canvas_id: Canvas containing the widget
        widget_id: Widget identifier to update
        file_path: New image file path, or None to keep current
        width: New display width in pixels, or None to keep current
        height: New display height in pixels, or None to keep current

    Returns:
        Success status and updated widget data
    """
    try:
        canvas = canvas_manager.get_canvas(canvas_id)
        if canvas is None:
            return {"success": False, "error": f"Canvas '{canvas_id}' not found"}
        widget = canvas.widget_registry.get(widget_id)
        if widget is None:
            return {"success": False, "error": f"Widget '{widget_id}' not found"}
        if not isinstance(widget, ImageWidget):
            return {
                "success": False,
                "error": f"Widget '{widget_id}' is not an ImageWidget",
            }
        if file_path is not None:
            widget.state.properties["file_path"] = file_path
        if width is not None:
            widget.state.properties["width"] = width
        if height is not None:
            widget.state.properties["height"] = height
        return {"success": True, "data": widget.serialize()}
    except Exception as e:
        logger.error(f"Error updating image widget '{widget_id}': {e}")
        return {"success": False, "error": str(e)}
