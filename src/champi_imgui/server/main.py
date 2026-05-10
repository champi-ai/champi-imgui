"""FastMCP server for champi-imgui.

Provides MCP tools for creating and managing Canvas windows and widgets
through shared memory IPC.
"""

from typing import Any

from fastmcp import FastMCP
from loguru import logger

from champi_imgui.core.canvas import CanvasManager
from champi_imgui.ipc.command_types import CommandType
from champi_imgui.ipc.shared_memory_manager import SharedMemoryManager
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
            widget_id, value=value, overlay=overlay, size=(width, height)
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
