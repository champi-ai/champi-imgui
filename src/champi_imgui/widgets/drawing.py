"""Drawing widgets for whiteboard functionality.

This module provides widgets for freehand drawing and whiteboard interaction:
- DrawingWidget: Main drawing canvas with mouse input
- BrushWidget: Brush controls sidebar (color, size)
- CanvasMenuWidget: Context menu for canvas actions
"""

import math
from typing import Any

from imgui_bundle import imgui

from champi_imgui.core.widget import Widget


class DrawingWidget(Widget):
    """Freehand drawing widget with stroke-based undo support.

    A drawing canvas that accepts mouse input for freehand sketching.
    Strokes are stored as lists of (x, y) points and replayed each frame
    using ImGui draw list primitives. LLM-drawn shapes (rect, circle,
    arrow, line) are stored separately and rendered after strokes.
    """

    def __init__(
        self,
        widget_id: str,
        color: tuple[float, float, float, float] = (1.0, 0.0, 0.0, 1.0),
        brush_size: float = 5.0,
        is_eraser: bool = False,
        brush_style: str = "solid",
        size: tuple[float, float] = (800.0, 600.0),
        **props: Any,
    ):
        """Initialize drawing widget.

        Args:
            widget_id: Unique widget identifier
            color: Brush color as (r, g, b, a) tuple, 0.0-1.0 range
            brush_size: Brush thickness in pixels
            is_eraser: Whether brush is in eraser mode
            brush_style: "solid", "dashed", or "dots"
            size: Canvas size as (width, height) in pixels
            **props: Additional properties (visible, enabled, etc.)
        """
        props["color"] = color
        props["brush_size"] = brush_size
        props["is_eraser"] = is_eraser
        props["brush_style"] = brush_style
        props["size"] = size
        props["strokes"] = []
        props["current_stroke"] = []
        props["shapes"] = []
        super().__init__(widget_id, **props)

    def render(self) -> None:  # pragma: no cover
        """Render the drawing canvas and handle mouse input.

        Each frame: replay all stored strokes, draw shapes, then handle
        in-progress stroke from mouse input.
        """
        if not self.state.visible:
            return

        color: tuple[float, float, float, float] = self.state.properties.get(
            "color", (1.0, 0.0, 0.0, 1.0)
        )
        brush_size: float = self.state.properties.get("brush_size", 5.0)
        is_eraser: bool = self.state.properties.get("is_eraser", False)
        brush_style: str = self.state.properties.get("brush_style", "solid")
        canvas_size: tuple[float, float] = self.state.properties.get(
            "size", (800.0, 600.0)
        )
        strokes: list[list[tuple[float, float]]] = self.state.properties.get(
            "strokes", []
        )
        current_stroke: list[tuple[float, float]] = self.state.properties.get(
            "current_stroke", []
        )

        draw_color: tuple[float, float, float, float] = (
            (1.0, 1.0, 1.0, 1.0) if is_eraser else color
        )

        # Create interactable region — this is the sole source of hover/click state
        imgui.invisible_button(
            "##canvas_" + self.widget_id,
            imgui.ImVec2(canvas_size[0], canvas_size[1]),
        )
        canvas_min = imgui.get_item_rect_min()
        canvas_max = imgui.get_item_rect_max()

        draw_list = imgui.get_window_draw_list()

        # Draw canvas background
        draw_list.add_rect_filled(
            canvas_min,
            canvas_max,
            imgui.color_convert_float4_to_u32(imgui.ImVec4(0.15, 0.15, 0.15, 1.0)),
        )

        # Replay all completed strokes
        for stroke in strokes:
            if len(stroke) >= 2:
                self._draw_stroke(
                    draw_list, stroke, draw_color, brush_size, brush_style, canvas_min
                )

        # Draw in-progress stroke
        if len(current_stroke) >= 2:
            self._draw_stroke(
                draw_list,
                current_stroke,
                draw_color,
                brush_size,
                brush_style,
                canvas_min,
            )

        # Draw LLM-added shapes
        for shape in self.state.properties.get("shapes", []):
            self._draw_shape(draw_list, shape, canvas_min)

        # Handle mouse input — must come after invisible_button for is_item_hovered
        if imgui.is_item_hovered():
            imgui.set_mouse_cursor(imgui.MouseCursor_.hand)
            mouse_pos = imgui.get_mouse_pos()
            rel_x = mouse_pos.x - canvas_min.x
            rel_y = mouse_pos.y - canvas_min.y

            if imgui.is_mouse_down(0):
                current_stroke.append((rel_x, rel_y))
                self.state.properties["current_stroke"] = current_stroke
            elif imgui.is_mouse_released(0) and current_stroke:
                strokes.append(list(current_stroke))
                self.state.properties["strokes"] = strokes
                self.state.properties["current_stroke"] = []
        elif imgui.is_mouse_released(0) and current_stroke:
            # Mouse released outside canvas — commit the in-progress stroke
            strokes.append(list(current_stroke))
            self.state.properties["strokes"] = strokes
            self.state.properties["current_stroke"] = []

    def _draw_stroke(  # pragma: no cover
        self,
        draw_list: imgui.ImDrawList,
        stroke: list[tuple[float, float]],
        color: tuple[float, float, float, float],
        brush_size: float,
        brush_style: str,
        canvas_min: imgui.ImVec2,
    ) -> None:
        """Draw a single stroke using the configured style.

        Args:
            draw_list: ImGui window draw list
            stroke: List of canvas-relative (x, y) points
            color: RGBA color tuple (0.0-1.0 range)
            brush_size: Line thickness in pixels
            brush_style: "solid", "dashed", or "dots"
            canvas_min: Canvas origin in screen coordinates
        """
        color_u32 = imgui.color_convert_float4_to_u32(imgui.ImVec4(*color))
        vec2_points: list[imgui.ImVec2] = [
            imgui.ImVec2(canvas_min.x + x, canvas_min.y + y) for x, y in stroke
        ]

        if brush_style == "solid":
            draw_list.add_polyline(vec2_points, color_u32, 0, brush_size)  # type: ignore[arg-type]

        elif brush_style == "dashed":
            # Draw every other segment
            for i in range(0, len(vec2_points) - 1, 2):
                draw_list.add_line(
                    vec2_points[i], vec2_points[i + 1], color_u32, brush_size
                )

        elif brush_style == "dots":
            # Draw a filled circle at every 3rd point
            for i in range(0, len(vec2_points), 3):
                draw_list.add_circle_filled(vec2_points[i], brush_size * 0.5, color_u32)

    def _draw_shape(  # pragma: no cover
        self,
        draw_list: imgui.ImDrawList,
        shape: dict[str, Any],
        canvas_min: imgui.ImVec2,
    ) -> None:
        """Draw a single LLM-added shape.

        Args:
            draw_list: ImGui window draw list
            shape: Shape dict with type, color, thickness, and coordinates
            canvas_min: Canvas origin in screen coordinates
        """
        color_u32 = imgui.color_convert_float4_to_u32(imgui.ImVec4(*shape["color"]))
        t = shape.get("thickness", 2.0)
        ox, oy = canvas_min.x, canvas_min.y
        stype = shape["type"]

        if stype == "rect":
            draw_list.add_rect(
                imgui.ImVec2(ox + shape["x1"], oy + shape["y1"]),
                imgui.ImVec2(ox + shape["x2"], oy + shape["y2"]),
                color_u32,
                0.0,
                0,
                t,
            )
        elif stype == "circle":
            draw_list.add_circle(
                imgui.ImVec2(ox + shape["cx"], oy + shape["cy"]),
                shape["radius"],
                color_u32,
                0,
                t,
            )
        elif stype in ("line", "arrow"):
            draw_list.add_line(
                imgui.ImVec2(ox + shape["x1"], oy + shape["y1"]),
                imgui.ImVec2(ox + shape["x2"], oy + shape["y2"]),
                color_u32,
                t,
            )
            if stype == "arrow":
                dx = shape["x2"] - shape["x1"]
                dy = shape["y2"] - shape["y1"]
                length = math.hypot(dx, dy)
                if length > 0:
                    ux, uy = dx / length, dy / length
                    head = 12.0
                    p = imgui.ImVec2(ox + shape["x2"], oy + shape["y2"])
                    p1 = imgui.ImVec2(
                        p.x - ux * head + uy * head * 0.4,
                        p.y - uy * head - ux * head * 0.4,
                    )
                    p2 = imgui.ImVec2(
                        p.x - ux * head - uy * head * 0.4,
                        p.y - uy * head + ux * head * 0.4,
                    )
                    draw_list.add_triangle_filled(p, p1, p2, color_u32)

    def add_shape(
        self,
        shape_type: str,
        color: tuple[float, float, float, float] = (0.0, 0.5, 1.0, 1.0),
        thickness: float = 2.0,
        **coords: float,
    ) -> None:
        """Add a shape to the canvas.

        Args:
            shape_type: One of "rect", "circle", "arrow", "line"
            color: RGBA color tuple (0.0-1.0 range)
            thickness: Line thickness in pixels
            **coords: Coordinate arguments. rect/arrow/line use x1, y1, x2, y2;
                circle uses cx, cy, radius. All values are canvas-relative.
        """
        shape: dict[str, Any] = {
            "type": shape_type,
            "color": color,
            "thickness": thickness,
            **coords,
        }
        shapes: list[dict[str, Any]] = self.state.properties.get("shapes", [])
        shapes.append(shape)
        self.state.properties["shapes"] = shapes

    def clear_shapes(self) -> None:
        """Remove all shapes from the canvas."""
        self.state.properties["shapes"] = []

    def clear(self) -> None:
        """Clear all strokes and shapes from the canvas."""
        self.state.properties["strokes"] = []
        self.state.properties["current_stroke"] = []
        self.clear_shapes()

    def undo(self) -> None:
        """Remove the last completed stroke."""
        strokes: list[list[tuple[float, float]]] = self.state.properties.get(
            "strokes", []
        )
        if strokes:
            strokes.pop()
            self.state.properties["strokes"] = strokes


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

    def render(self) -> None:  # pragma: no cover
        """Render brush controls."""
        if not self.state.visible:
            return

        color: tuple[float, float, float, float] = self.state.properties.get(
            "color", (1.0, 0.0, 0.0, 1.0)
        )
        brush_size: float = self.state.properties.get("brush_size", 5.0)
        line_width: float = self.state.properties.get("line_width", 1.0)
        is_eraser: bool = self.state.properties.get("is_eraser", False)
        brush_style: str = self.state.properties.get("brush_style", "solid")

        imgui.text("Brush Settings")
        imgui.separator()

        imgui.push_item_width(160)
        imgui.set_next_item_width(160)
        changed, new_color = imgui.color_picker4("##color", color)
        if changed:
            self.state.properties["color"] = new_color
        imgui.pop_item_width()

        imgui.push_item_width(150)
        imgui.set_next_item_width(150)
        changed, new_eraser = imgui.checkbox("Eraser", is_eraser)
        if changed:
            self.state.properties["is_eraser"] = new_eraser
        imgui.pop_item_width()

        style_options: list[tuple[str, str]] = [
            ("Solid", "solid"),
            ("Dashed", "dashed"),
            ("Dotted", "dots"),
        ]
        style_names = [s for s, _ in style_options]
        style_values = [v for _, v in style_options]
        current_style_idx = (
            style_values.index(brush_style) if brush_style in style_values else 0
        )
        changed, new_style_idx = imgui.combo(
            "##brush_style", current_style_idx, style_names, 0
        )
        if changed:
            self.state.properties["brush_style"] = style_values[new_style_idx]

        imgui.push_item_width(150)
        imgui.set_next_item_width(150)
        changed, new_size = imgui.slider_float("##brush_size", brush_size, 1.0, 50.0)
        if changed:
            self.state.properties["brush_size"] = new_size
        imgui.pop_item_width()

        imgui.text("Line Width")
        changed, new_line_width = imgui.slider_float(
            "##line_width", line_width, 0.1, 10.0
        )
        if changed:
            self.state.properties["line_width"] = new_line_width

        imgui.separator()
        imgui.text("Preview")
        preview_dot_color: tuple[float, float, float, float] = (
            (1.0, 1.0, 1.0, 1.0) if is_eraser else color
        )
        preview_size = brush_size * 1.5
        draw_list = imgui.get_window_draw_list()
        cursor = imgui.get_cursor_screen_pos()
        draw_list.add_circle(
            imgui.ImVec2(cursor.x + preview_size + 5, cursor.y + preview_size + 5),
            preview_size,
            imgui.color_convert_float4_to_u32(imgui.ImVec4(*preview_dot_color)),
            20,
        )


class CanvasMenuWidget(Widget):
    """Context menu for canvas actions.

    Provides a right-click context menu tied to the current ImGui window.
    Opens on right-click anywhere in the window and exposes undo, redo,
    and clear actions wired to an associated DrawingWidget by ID.
    """

    def __init__(
        self,
        widget_id: str,
        drawing_widget_id: str = "",
        can_undo: bool = True,
        can_redo: bool = True,
        history_size: int = 10,
        **props: Any,
    ):
        """Initialize canvas menu widget.

        Args:
            widget_id: Unique widget identifier
            drawing_widget_id: ID of the DrawingWidget this menu controls
            can_undo: Whether undo is available
            can_redo: Whether redo is available
            history_size: Maximum history size for commands
            **props: Additional properties (visible, etc.)
        """
        props["drawing_widget_id"] = drawing_widget_id
        props["can_undo"] = can_undo
        props["can_redo"] = can_redo
        props["history_size"] = history_size
        super().__init__(widget_id, **props)

    def render(self) -> None:  # pragma: no cover
        """Render the canvas context menu.

        Opens via ImGui's named popup API on right-click anywhere in the
        current window. Menu items invoke registered callbacks.
        """
        if not self.state.visible:
            return

        popup_id = "##canvas_menu_" + self.widget_id

        if imgui.is_window_hovered() and imgui.is_mouse_clicked(
            imgui.MouseButton_.right
        ):
            imgui.open_popup(popup_id)

        if imgui.begin_popup(popup_id):
            can_undo: bool = self.state.properties.get("can_undo", True)
            can_redo: bool = self.state.properties.get("can_redo", True)
            history_size: int = self.state.properties.get("history_size", 10)

            if can_undo:
                clicked, _ = imgui.menu_item("Undo", "", False)
                if clicked:
                    self.trigger_callback("on_undo")

            if can_redo:
                clicked, _ = imgui.menu_item("Redo", "", False)
                if clicked:
                    self.trigger_callback("on_redo")

            clicked, _ = imgui.menu_item("Clear Canvas", "", False)
            if clicked:
                self.trigger_callback("on_clear")

            imgui.separator()
            imgui.text(f"History: {history_size}")
            imgui.end_popup()
