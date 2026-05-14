"""Drawing widgets for whiteboard functionality.

This module provides widgets for freehand drawing and whiteboard interaction:
- DrawingWidget: Main drawing canvas with mouse input
- BrushWidget: Brush controls sidebar (color, size)
- CanvasMenuWidget: Context menu for canvas actions
"""

from typing import Any

from imgui_bundle import imgui

from champi_imgui.core.widget import Widget


class DrawingWidget(Widget):
    """Freehand drawing widget with undo/redo support.

    A drawing canvas that accepts mouse input for freehand sketching,
    with brush size/color controls and undo/redo history.

    This widget renders directly into its available content region,
    capturing mouse movement to draw strokes.
    """

    def __init__(
        self,
        widget_id: str,
        color: tuple[float, float, float, float] = (1.0, 0.0, 0.0, 1.0),
        brush_size: float = 5.0,
        line_width: float = 1.0,
        is_clear: bool = False,
        is_eraser: bool = False,
        brush_style: str = "solid",
        history_size: int = 10,
        history: list[dict[str, Any]] | None = None,
        history_index: int = -1,
        **props: Any,
    ):
        """Initialize drawing widget.

        Args:
            widget_id: Unique widget identifier
            color: Brush color as (r, g, b, a) tuple, 0.0-1.0 range
            brush_size: Brush radius in pixels
            line_width: Line width for text/annotation
            is_clear: Whether canvas should be cleared on render
            is_eraser: Whether brush is in eraser mode
            brush_style: "solid", "dashed", or "dots"
            history_size: Maximum undo history size
            history: Pre-populated undo history (list of snapshots)
            history_index: Current history index for undo/redo
            **props: Additional properties (size, visible, etc.)
        """
        props["color"] = color
        props["brush_size"] = brush_size
        props["line_width"] = line_width
        props["is_clear"] = is_clear
        props["is_eraser"] = is_eraser
        props["brush_style"] = brush_style
        props["history_size"] = history_size
        props["history"] = history or []
        props["history_index"] = history_index
        super().__init__(widget_id, **props)

    def render(self) -> None:
        """Render the drawing canvas and handle mouse input.

        This method captures mouse input during rendering to enable
        freehand drawing. The canvas is redrawn each frame based on
        the last history snapshot.

        Returns:
            None (rendering handled via ImGui)
        """
        if not self.state.visible:
            return

        color = self.state.properties.get("color", (1.0, 0.0, 0.0, 1.0))
        brush_size = self.state.properties.get("brush_size", 5.0)
        is_eraser = self.state.properties.get("is_eraser", False)
        brush_style = self.state.properties.get("brush_style", "solid")
        history = self.state.properties.get("history", [])
        history_index = self.state.properties.get("history_index", -1)

        # Get available render region
        visible, width, height = imgui.get_content_region_avail()

        if not visible:
            return

        # Determine drawing color
        draw_color = (1.0, 1.0, 1.0, 1.0) if is_eraser else color

        # Handle canvas clear command
        if self.state.properties.get("is_clear", False):
            self.state.properties["is_clear"] = False
            self._clear_canvas(width, height)

        # Restore last canvas state from history
        self._restore_canvas(history, history_index, draw_color, width, height)

        # Handle mouse input for drawing
        self._handle_mouse_input(width, height, draw_color, brush_size, brush_style)

    def _clear_canvas(self, width: float, height: float) -> None:
        """Clear the canvas by resetting history.

        Args:
            width: Canvas width in pixels
            height: Canvas height in pixels
        """
        self.state.properties["history"] = [
            {"data": [(0.0, 0.0)] * int(width * height)},
        ]
        self.state.properties["history_index"] = 0

    def _restore_canvas(
        self,
        history: list[dict[str, Any]],
        index: int,
        color: tuple[float, ...],
        width: float,
        height: float,
    ) -> None:
        """Restore canvas from a history snapshot.

        Args:
            history: List of history snapshots
            index: History index to restore
            color: Current drawing color
            width: Canvas width
            height: Canvas height
        """
        if not history:
            return

        if index < 0 or index >= len(history):
            return

        snapshot = history[index].get("data", [])
        if not snapshot:
            return

        # Convert snapshot data to ImGui-compatible format
        # For simplicity, we render a simple solid color fill
        # A full bitmap approach would require OpenGL textures
        self._render_from_snapshot(snapshot, color, width, height)

    def _render_from_snapshot(
        self,
        snapshot: list[tuple],
        color: tuple[float, ...],
        width: float,
        height: float,
    ) -> None:
        """Render canvas from snapshot data.

        For a simple implementation, we use ImGui primitives
        to approximate the snapshot. For full functionality,
        OpenGL textures would be needed.

        Args:
            snapshot: Snapshot pixel data
            color: Color to use
            width: Canvas width
            height: Canvas height
        """
        # Simple implementation: just draw a filled rectangle
        # representing the canvas area
        imgui.push_style_color(imgui.ColMod_.frame_bg, (*color[:3], 1.0))
        imgui.push_style_color(imgui.ColMod_.frame_border, (0.0, 0.0, 0.0, 0.0))
        imgui.push_style_color(imgui.ColMod_.frame_bg_hover, (*color[:3], 1.0))
        imgui.push_style_color(imgui.ColMod_.frame_border_hover, (0.0, 0.0, 0.0, 0.0))

        # Draw canvas background
        imgui.get_window_draw_list().add_rect(
            imgui.ImVec2(0, 0),
            imgui.ImVec2(width, height),
            imgui.ImCol((*color[:3], 1.0)),
            1.0,  # rounding
            0,  # border rounding
            2,  # thickness
        )

        imgui.pop_style_color(3)

    def _handle_mouse_input(
        self,
        width: float,
        height: float,
        color: tuple[float, ...],
        brush_size: float,
        brush_style: str,
    ) -> None:
        """Handle mouse input for drawing.

        Captures mouse position during render and draws strokes
        when the mouse is moving.

        Args:
            width: Canvas width
            height: Canvas height
            color: Drawing color
            brush_size: Brush radius
            brush_style: Brush style (solid/dashed/dots)
        """
        # Get mouse position relative to canvas
        mouse_pos = imgui.get_mouse_pos()
        canvas_x = mouse_pos[0]
        canvas_y = mouse_pos[1]

        # Check if mouse is over the canvas
        is_mouse_over = imgui.is_item_hoverable()

        # Set mouse cursor to hand when hovering
        if is_mouse_over:
            imgui.set_mouse_cursor(imgui.MouseCursor_.Hand)

        # Handle left mouse button for drawing
        if is_mouse_over:
            # Check mouse button states
            mouse_down = imgui.is_mouse_button_down(imgui.MouseButton_.Left)

            # Draw line segment if mouse is moving and button is held
            if mouse_down and is_mouse_over:
                # Get last mouse position for line drawing
                last_mouse_x = self.state.properties.get("last_mouse_x", canvas_x)
                last_mouse_y = self.state.properties.get("last_mouse_y", canvas_y)

                if last_mouse_x is not None and last_mouse_y is not None:
                    # Draw a line segment
                    start_pos = imgui.ImVec2(last_mouse_x, last_mouse_y)
                    end_pos = imgui.ImVec2(canvas_x, canvas_y)

                    self._draw_line(start_pos, end_pos, color, brush_size, brush_style)

                    # Update last position
                    self.state.properties["last_mouse_x"] = canvas_x
                    self.state.properties["last_mouse_y"] = canvas_y

        # Clear temporary state when not hovering
        if not is_mouse_over:
            self.state.properties["last_mouse_x"] = None
            self.state.properties["last_mouse_y"] = None

    def _draw_line(
        self,
        start: imgui.ImVec2,
        end: imgui.ImVec2,
        color: tuple[float, ...],
        brush_size: float,
        brush_style: str,
    ) -> None:
        """Draw a line segment with the given style.

        Args:
            start: Starting point (x, y)
            end: Ending point (x, y)
            color: Line color (r, g, b, a)
            brush_size: Radius of brush
            brush_style: "solid", "dashed", or "dots"
        """
        draw_list = imgui.get_window_draw_list()

        if brush_style == "dashed":
            # Draw dashed line with gaps
            gap = 4.0
            seg = brush_size * 2

            dx = end[0] - start[0]
            dy = end[1] - start[1]
            length = (dx**2 + dy**2) ** 0.5

            if length > 0:
                # Draw segments with gaps
                num_segments = int(length / (seg + gap))
                for i in range(num_segments):
                    t = float(i) / num_segments
                    p1 = start + (end - start) * t
                    p2 = start + (end - start) * min(t + seg / length, 1.0)
                    draw_list.add_line(p1, p2, imgui.ImCol(color), brush_size)

        elif brush_style == "dots":
            # Draw dots along the line
            dx = end[0] - start[0]
            dy = end[1] - start[1]
            length = (dx**2 + dy**2) ** 0.5

            if length > 0:
                num_dots = max(1, int(length / (brush_size * 3)))
                for i in range(num_dots):
                    t = float(i) / num_dots
                    p = start + (end - start) * t
                    draw_list.add_circle(
                        p, brush_size, imgui.ImCol(color), brush_size, 32
                    )

        else:
            # Solid line with anti-aliasing
            draw_list.add_line(start, end, imgui.ImCol(color), brush_size)


class BrushWidget(Widget):
    """Brush controls sidebar for the drawing widget.

    Provides UI controls for brush color, size, and style.
    Should be positioned adjacent to the DrawingWidget.
    """

    def __init__(
        self,
        widget_id: str,
        color: tuple[float, float, float, float] = (1.0, 0.0, 0.0, 1.0),
        brush_size: float = 5.0,
        line_width: float = 1.0,
        is_eraser: bool = False,
        brush_style: str = "solid",
        **props: Any,
    ):
        """Initialize brush controls widget.

        Args:
            widget_id: Unique widget identifier
            color: Current brush color
            brush_size: Current brush size
            line_width: Current line width
            is_eraser: Whether eraser mode is active
            brush_style: Current brush style
            **props: Additional properties (size, visible, etc.)
        """
        props["color"] = color
        props["brush_size"] = brush_size
        props["line_width"] = line_width
        props["is_eraser"] = is_eraser
        props["brush_style"] = brush_style
        super().__init__(widget_id, **props)

    def render(self) -> None:
        """Render brush controls.

        Args:
            width: Unused (available via ImGui)
            height: Unused (available via ImGui)
        """
        if not self.state.visible:
            return

        color = self.state.properties.get("color", (1.0, 0.0, 0.0, 1.0))
        brush_size = self.state.properties.get("brush_size", 5.0)
        line_width = self.state.properties.get("line_width", 1.0)
        is_eraser = self.state.properties.get("is_eraser", False)
        brush_style = self.state.properties.get("brush_style", "solid")

        # Title
        imgui.text("Brush Settings")
        imgui.separator()

        # Color picker
        imgui.push_item_width(160)
        imgui.set_next_item_width(160)
        imgui.color_picker4("##color", color)
        imgui.pop_item_width()

        # Eraser toggle
        imgui.push_item_width(150)
        imgui.set_next_item_width(150)
        checked = imgui.checkbox("Eraser", is_eraser)
        self.state.properties["is_eraser"] = checked
        imgui.pop_item_width()

        # Brush style options
        style_options = [
            ("Solid", "solid"),
            ("Dashed", "dashed"),
            ("Dotted", "dots"),
        ]
        style_names, style_values = zip(*style_options, strict=True)
        current_style_idx = style_names.index(brush_style)
        selected_style = imgui.combo("##brush_style", current_style_idx, style_names, 0)
        if selected_style != current_style_idx:
            brush_style = style_values[selected_style]
            self.state.properties["brush_style"] = brush_style

        # Brush size slider
        imgui.push_item_width(150)
        imgui.set_next_item_width(150)
        imgui.slider_float("##brush_size", brush_size, 1.0, 50.0)
        imgui.pop_item_width()

        # Line width slider
        imgui.text("Line Width")
        imgui.slider_float("##line_width", line_width, 0.1, 10.0)
        self.state.properties["line_width"] = line_width

        # Preview dot
        imgui.separator()
        imgui.text("Preview")
        preview_dot_color = color if not is_eraser else (1.0, 1.0, 1.0, 1.0)
        preview_size = brush_size * 1.5
        draw_list = imgui.get_window_draw_list()
        draw_list.add_circle(
            imgui.ImVec2(100, 15),  # Fixed position for preview
            preview_size,
            imgui.ImCol(preview_dot_color),
            20,  # segments
        )


class CanvasMenuWidget(Widget):
    """Context menu for canvas actions.

    Provides a right-click menu with commands like:
    - Undo
    - Redo
    - Clear Canvas
    - Invert Colors
    """

    def __init__(
        self,
        widget_id: str,
        can_undo: bool = True,
        can_redo: bool = True,
        history_size: int = 10,
        **props: Any,
    ):
        """Initialize canvas menu widget.

        Args:
            widget_id: Unique widget identifier
            can_undo: Whether undo is available
            can_redo: Whether redo is available
            history_size: Maximum history size for commands
            **props: Additional properties (visible, etc.)
        """
        props["can_undo"] = can_undo
        props["can_redo"] = can_redo
        props["history_size"] = history_size
        super().__init__(widget_id, **props)
        self._menu_open = False

    def render(self) -> None:
        """Render the canvas menu (if open).

        The menu is typically triggered by right-click on the
        DrawingWidget. Use imgui.open_context_menu() to open.

        Returns:
            True if menu is open and rendered
        """
        if not self.state.visible:
            return

        can_undo = self.state.properties.get("can_undo", True)
        can_redo = self.state.properties.get("can_redo", True)
        history_size = self.state.properties.get("history_size", 10)

        # Check if menu should be open (via context menu trigger)
        menu_open = self.state.properties.get("menu_open", False)

        if menu_open:
            # Build menu items
            if can_undo:
                clicked, _ = imgui.menu_item("Undo")
                if clicked:
                    self.trigger_callback("on_undo")

            if can_redo:
                clicked, _ = imgui.menu_item("Redo")
                if clicked:
                    self.trigger_callback("on_redo")

            if self.state.properties.get("is_eraser", False):
                clicked, _ = imgui.menu_item("Clear (Eraser)")
                if clicked:
                    self.state.properties["is_eraser"] = False
                    self.trigger_callback("on_clear_eraser")
            else:
                clicked, _ = imgui.menu_item("Clear Canvas")
                if clicked:
                    self.state.properties["is_clear"] = True
                    self.trigger_callback("on_clear")

            clicked, _ = imgui.menu_item("Invert Colors")
            if clicked:
                self.trigger_callback("on_invert")

            clicked, _ = imgui.menu_item("Save as PNG...")
            if clicked:
                self.trigger_callback("on_save_png")

            clicked, _ = imgui.menu_item("Export Commands...")
            if clicked:
                self.trigger_callback("on_export_commands")

            clicked, _ = imgui.menu_item("Properties...")
            if clicked:
                self.trigger_callback("on_properties")

            clicked, _ = imgui.menu_item("Close Menu")
            if clicked:
                self.state.properties["menu_open"] = False

            imgui.separator()
            imgui.text(f"History: {history_size}")

            imgui.end()
            return

        self.state.properties["menu_open"] = False
        return
