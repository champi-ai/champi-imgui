"""Drawing widgets for whiteboard functionality.

This module provides widgets for freehand drawing and whiteboard interaction:
- DrawingWidget: Main drawing canvas with mouse input
- BrushWidget: Brush controls sidebar (color, size)
- CanvasMenuWidget: Context menu for canvas actions
"""

import math
import os
import time
from typing import Any

from imgui_bundle import imgui
from loguru import logger

from champi_imgui.core.state import canvas_updated
from champi_imgui.core.widget import Widget

AUTHOR_COLORS: dict[str, tuple[float, float, float, float]] = {
    "user": (0.1, 0.1, 0.1, 1.0),
    "llm": (0.0, 0.5, 1.0, 1.0),
}

VALID_SHAPE_TYPES: frozenset[str] = frozenset(
    {"rect", "circle", "ellipse", "arrow", "line"}
)
FILL_SUPPORTED_TYPES: frozenset[str] = frozenset({"rect", "circle", "ellipse"})


class DrawingWidget(Widget):
    """Freehand drawing widget with stroke-based undo support.

    A drawing canvas that accepts mouse input for freehand sketching.
    Strokes are stored as lists of (x, y) points and replayed each frame
    using ImGui draw list primitives.
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
        props.setdefault("color", color)
        props.setdefault("brush_size", brush_size)
        props.setdefault("is_eraser", is_eraser)
        props.setdefault("brush_style", brush_style)
        props.setdefault("size", size)
        props.setdefault("strokes", [])
        props.setdefault("current_stroke", [])
        props.setdefault("shapes", [])
        props.setdefault("annotations", [])
        props.setdefault("redo_stack", [])
        super().__init__(widget_id, **props)
        # Screen position of this widget's top-left corner, updated each render frame.
        self.canvas_screen_offset: tuple[float, float] = (0.0, 0.0)

    def render(self) -> None:  # pragma: no cover
        """Render the drawing canvas and handle mouse input.

        Each frame: replay all stored strokes, then handle in-progress
        stroke from mouse input.
        """
        if not self.state.visible:
            return

        _pos = imgui.get_cursor_screen_pos()
        self.canvas_screen_offset = (_pos.x, _pos.y)

        color: tuple[float, float, float, float] = self.state.properties.get(
            "color", (1.0, 0.0, 0.0, 1.0)
        )
        brush_size: float = self.state.properties.get("brush_size", 5.0)
        is_eraser: bool = self.state.properties.get("is_eraser", False)
        brush_style: str = self.state.properties.get("brush_style", "solid")
        canvas_size: tuple[float, float] = self.state.properties.get(
            "size", (800.0, 600.0)
        )
        strokes: list[dict[str, Any]] = self.state.properties.get("strokes", [])
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

        # Clip all drawing to the canvas bounds so nothing bleeds outside the area.
        # This is the standard ImGui custom-canvas pattern and is required for draw
        # commands to render correctly inside imgui-bundle windows.
        draw_list.push_clip_rect(canvas_min, canvas_max, True)

        if os.environ.get("CHAMPI_DEBUG_DRAWING"):
            _shapes: list[dict[str, Any]] = self.state.properties.get("shapes", [])
            _annotations: list[dict[str, Any]] = self.state.properties.get(
                "annotations", []
            )
            _splitter = getattr(draw_list, "_splitter", None)
            _channel_count: int | None = (
                getattr(_splitter, "_count", None)
                if _splitter is not None
                else None
            )
            _clip_min = draw_list.get_clip_rect_min()
            _clip_max = draw_list.get_clip_rect_max()
            logger.debug(
                "DrawingWidget.render() widget={} | channels={} | "
                "clip=({:.1f},{:.1f})-({:.1f},{:.1f}) | "
                "strokes={} shapes={} annotations={} | canvas_updated_receivers={}",
                self.widget_id,
                _channel_count,
                _clip_min.x,
                _clip_min.y,
                _clip_max.x,
                _clip_max.y,
                len(strokes),
                len(_shapes),
                len(_annotations),
                len(canvas_updated.receivers),
            )

        # Draw canvas background
        draw_list.add_rect_filled(
            canvas_min,
            canvas_max,
            imgui.color_convert_float4_to_u32(imgui.ImVec4(0.15, 0.15, 0.15, 1.0)),
        )

        # Replay all completed strokes; fall back to AUTHOR_COLORS when no
        # explicit color is stored (e.g. strokes imported without a color field).
        _default_color: tuple[float, float, float, float] = (0.1, 0.1, 0.1, 1.0)
        for stroke in strokes:
            points = stroke["points"]
            if len(points) >= 2:
                stroke_color: tuple[float, float, float, float] = stroke.get(
                    "color"
                ) or AUTHOR_COLORS.get(stroke.get("author", ""), _default_color)
                self._draw_stroke(
                    draw_list,
                    points,
                    stroke_color,
                    stroke["brush_size"],
                    stroke["brush_style"],
                    canvas_min,
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

        # Draw text annotations
        self._draw_annotations(draw_list, canvas_min)

        draw_list.pop_clip_rect()

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
                strokes.append(
                    {
                        "points": list(current_stroke),
                        "author": "user",
                        "timestamp": time.time(),
                        "tool": "eraser" if is_eraser else "brush",
                        "color": draw_color,
                        "brush_size": brush_size,
                        "brush_style": brush_style,
                    }
                )
                self.state.properties["strokes"] = strokes
                self.state.properties["current_stroke"] = []
                self.state.properties["redo_stack"] = []
        elif imgui.is_mouse_released(0) and current_stroke:
            # Mouse released outside canvas — commit the in-progress stroke
            strokes.append(
                {
                    "points": list(current_stroke),
                    "author": "user",
                    "timestamp": time.time(),
                    "tool": "eraser" if is_eraser else "brush",
                    "color": draw_color,
                    "brush_size": brush_size,
                    "brush_style": brush_style,
                }
            )
            self.state.properties["strokes"] = strokes
            self.state.properties["current_stroke"] = []
            self.state.properties["redo_stack"] = []

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
        if not stroke:
            return
        color_u32 = imgui.color_convert_float4_to_u32(imgui.ImVec4(*color))
        pts: list[imgui.ImVec2] = [
            imgui.ImVec2(canvas_min.x + x, canvas_min.y + y) for x, y in stroke
        ]

        if brush_style == "dots":
            for i in range(0, len(pts), 3):
                draw_list.add_circle_filled(pts[i], brush_size * 0.5, color_u32)
        elif brush_style == "dashed":
            dash_len = brush_size * 4
            gap_len = brush_size * 2
            for i in range(len(pts) - 1):
                p1, p2 = pts[i], pts[i + 1]
                dx = p2.x - p1.x
                dy = p2.y - p1.y
                seg_len = (dx * dx + dy * dy) ** 0.5
                if seg_len == 0:
                    continue
                ux, uy = dx / seg_len, dy / seg_len
                t = 0.0
                draw = True
                while t < seg_len:
                    t_end = min(t + (dash_len if draw else gap_len), seg_len)
                    if draw:
                        a = imgui.ImVec2(p1.x + ux * t, p1.y + uy * t)
                        b = imgui.ImVec2(p1.x + ux * t_end, p1.y + uy * t_end)
                        draw_list.add_line(a, b, color_u32, brush_size)
                    t = t_end
                    draw = not draw
        else:
            draw_list.add_polyline(pts, color_u32, 0, brush_size)  # type: ignore[arg-type]

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
        try:
            c = shape["color"]
            color_u32 = imgui.color_convert_float4_to_u32(
                imgui.ImVec4(c[0], c[1], c[2], c[3])
            )
            t = shape.get("thickness", 2.0)
            ox, oy = canvas_min.x, canvas_min.y
            stype = shape["type"]

            filled: bool = shape.get("filled", False)
            if stype == "rect":
                if filled:
                    draw_list.add_rect_filled(
                        imgui.ImVec2(ox + shape["x1"], oy + shape["y1"]),
                        imgui.ImVec2(ox + shape["x2"], oy + shape["y2"]),
                        color_u32,
                    )
                else:
                    draw_list.add_rect(
                        imgui.ImVec2(ox + shape["x1"], oy + shape["y1"]),
                        imgui.ImVec2(ox + shape["x2"], oy + shape["y2"]),
                        color_u32,
                        0.0,
                        0,
                        t,
                    )
            elif stype == "circle":
                if filled:
                    draw_list.add_circle_filled(
                        imgui.ImVec2(ox + shape["cx"], oy + shape["cy"]),
                        shape["radius"],
                        color_u32,
                    )
                else:
                    draw_list.add_circle(
                        imgui.ImVec2(ox + shape["cx"], oy + shape["cy"]),
                        shape["radius"],
                        color_u32,
                        0,
                        t,
                    )
            elif stype == "ellipse":
                center = imgui.ImVec2(ox + shape["cx"], oy + shape["cy"])
                radii = imgui.ImVec2(shape["rx"], shape["ry"])
                if filled:
                    draw_list.add_ellipse_filled(
                        center,
                        radii,
                        color_u32,
                    )
                else:
                    draw_list.add_ellipse(
                        center,
                        radii,
                        color_u32,
                        0.0,
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
        except Exception as exc:
            logger.error(f"_draw_shape failed for shape {shape.get('type')!r}: {exc}")

    def _draw_annotations(  # pragma: no cover
        self,
        draw_list: imgui.ImDrawList,
        canvas_min: imgui.ImVec2,
    ) -> None:
        """Draw all text annotations on the canvas.

        Args:
            draw_list: ImGui window draw list
            canvas_min: Canvas origin in screen coordinates
        """
        for annotation in self.state.properties.get("annotations", []):
            if annotation.get("type") == "text":
                try:
                    c = annotation["color"]
                    color_u32 = imgui.color_convert_float4_to_u32(
                        imgui.ImVec4(c[0], c[1], c[2], c[3])
                    )
                    draw_list.add_text(
                        imgui.ImVec2(
                            canvas_min.x + annotation["x"],
                            canvas_min.y + annotation["y"],
                        ),
                        color_u32,
                        annotation["text"],
                    )
                except Exception as exc:
                    logger.error(f"_draw_annotations failed for annotation: {exc}")

    def add_shape(
        self,
        shape_type: str,
        color: tuple[float, float, float, float] = (0.0, 0.5, 1.0, 1.0),
        thickness: float = 2.0,
        filled: bool = False,
        **coords: float,
    ) -> None:
        """Add a shape to the canvas.

        Args:
            shape_type: One of "rect", "circle", "ellipse", "arrow", "line"
            color: RGBA color tuple (0.0-1.0 range)
            thickness: Line thickness in pixels
            filled: Whether the shape is filled (only for "rect", "circle", "ellipse")
            **coords: Coordinate arguments. rect/arrow/line use x1, y1, x2, y2;
                circle uses cx, cy, radius; ellipse uses cx, cy, rx, ry.
                All values are canvas-relative.

        Raises:
            ValueError: If shape_type is unknown or filled is True for a type that
                does not support fill.
        """
        if shape_type not in VALID_SHAPE_TYPES:
            raise ValueError(f"Unknown shape type: '{shape_type}'")
        if filled and shape_type not in FILL_SUPPORTED_TYPES:
            raise ValueError(
                f"Shape type '{shape_type}' does not support fill; "
                f"only {sorted(FILL_SUPPORTED_TYPES)} do"
            )
        shape: dict[str, Any] = {
            "type": shape_type,
            "color": color,
            "thickness": thickness,
            "filled": filled,
            **coords,
        }
        shapes: list[dict[str, Any]] = self.state.properties.get("shapes", [])
        shapes.append(shape)
        self.state.properties["shapes"] = shapes

    def add_annotation(
        self,
        x: float,
        y: float,
        text: str,
        color: tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0),
        font_size: float = 13.0,
    ) -> None:
        """Add a text annotation to the canvas.

        Args:
            x: Canvas-relative x position
            y: Canvas-relative y position
            text: Text to display
            color: RGBA color tuple (0.0-1.0 range)
            font_size: Font size in pixels (informational; ImGui uses current font)
        """
        annotation: dict[str, Any] = {
            "type": "text",
            "x": x,
            "y": y,
            "text": text,
            "color": color,
            "font_size": font_size,
        }
        annotations: list[dict[str, Any]] = self.state.properties.get("annotations", [])
        annotations.append(annotation)
        self.state.properties["annotations"] = annotations

    def clear_shapes(self) -> None:
        """Remove all shapes from the canvas."""
        self.state.properties["shapes"] = []

    def clear(self) -> None:
        """Clear all strokes, shapes, and annotations from the canvas."""
        self.state.properties["strokes"] = []
        self.state.properties["current_stroke"] = []
        self.clear_shapes()
        self.state.properties["annotations"] = []
        self.state.properties["redo_stack"] = []

    @property
    def can_undo(self) -> bool:
        """Return True if there are strokes available to undo."""
        return bool(self.state.properties.get("strokes", []))

    @property
    def can_redo(self) -> bool:
        """Return True if there are undone strokes available to redo."""
        return bool(self.state.properties.get("redo_stack", []))

    def undo(self) -> None:
        """Remove the last completed stroke and push it onto the redo stack."""
        strokes: list[dict[str, Any]] = self.state.properties.get("strokes", [])
        if strokes:
            redo_stack: list[dict[str, Any]] = self.state.properties.get(
                "redo_stack", []
            )
            redo_stack.append(strokes.pop())
            self.state.properties["strokes"] = strokes
            self.state.properties["redo_stack"] = redo_stack

    def redo(self) -> None:
        """Restore the last undone stroke from the redo stack."""
        redo_stack: list[dict[str, Any]] = self.state.properties.get("redo_stack", [])
        if redo_stack:
            strokes: list[dict[str, Any]] = self.state.properties.get("strokes", [])
            strokes.append(redo_stack.pop())
            self.state.properties["strokes"] = strokes
            self.state.properties["redo_stack"] = redo_stack

    def get_strokes_by_author(self, author: str) -> list[dict[str, Any]]:
        """Return all strokes drawn by the given author.

        Args:
            author: Author identifier, e.g. "user" or "llm"

        Returns:
            List of stroke dicts whose "author" field matches the given value.
        """
        return [
            s
            for s in self.state.properties.get("strokes", [])
            if s.get("author") == author
        ]


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
        self._linked_drawing: DrawingWidget | None = None

    def link_to_drawing(self, widget: "DrawingWidget") -> None:
        """Link this BrushWidget to a DrawingWidget for live state sync.

        When any brush property changes, the linked DrawingWidget's matching
        properties are updated so strokes immediately use the new settings.

        Args:
            widget: DrawingWidget instance to sync with.
        """
        self._linked_drawing = widget

    def _sync_to_drawing(self) -> None:
        """Push current brush properties to the linked DrawingWidget."""
        if self._linked_drawing is None:
            return
        props = self._linked_drawing.state.properties
        for key in ("color", "brush_size", "is_eraser", "brush_style"):
            props[key] = self.state.properties[key]

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

        _any_changed = False

        imgui.push_item_width(160)
        imgui.set_next_item_width(160)
        changed, new_color = imgui.color_picker4("##color", color)
        if changed:
            self.state.properties["color"] = new_color
            _any_changed = True
        imgui.pop_item_width()

        imgui.push_item_width(150)
        imgui.set_next_item_width(150)
        changed, new_eraser = imgui.checkbox("Eraser", is_eraser)
        if changed:
            self.state.properties["is_eraser"] = new_eraser
            _any_changed = True
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
            _any_changed = True

        imgui.push_item_width(150)
        imgui.set_next_item_width(150)
        changed, new_size = imgui.slider_float("##brush_size", brush_size, 1.0, 50.0)
        if changed:
            self.state.properties["brush_size"] = new_size
            _any_changed = True
        imgui.pop_item_width()

        imgui.text("Line Width")
        changed, new_line_width = imgui.slider_float(
            "##line_width", line_width, 0.1, 10.0
        )
        if changed:
            self.state.properties["line_width"] = new_line_width
            _any_changed = True

        if _any_changed:
            self._sync_to_drawing()

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

        Opens via begin_popup_context_window on right-click anywhere in the
        current window. Menu items invoke registered callbacks.
        """
        if not self.state.visible:
            return

        popup_id = "##canvas_menu_" + self.widget_id

        if imgui.begin_popup_context_window(popup_id):
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
