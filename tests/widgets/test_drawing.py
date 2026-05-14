"""Tests for drawing widgets.

Covers initialization, state mutation (clear/undo), serialization,
and WidgetFactory registration. Render tests are omitted because
calling widget.render() outside an active ImGui context segfaults.
"""

import pytest

from champi_imgui.core.widget import WidgetFactory, WidgetRegistry
from champi_imgui.widgets.drawing import BrushWidget, CanvasMenuWidget, DrawingWidget


# ---------------------------------------------------------------------------
# DrawingWidget — initialization and state
# ---------------------------------------------------------------------------


def test_drawing_widget_defaults():
    """DrawingWidget initializes with expected default properties."""
    w = DrawingWidget("canvas-1")

    assert w.widget_id == "canvas-1"
    assert w.state.properties["color"] == (1.0, 0.0, 0.0, 1.0)
    assert w.state.properties["brush_size"] == 5.0
    assert w.state.properties["is_eraser"] is False
    assert w.state.properties["brush_style"] == "solid"
    assert w.state.properties["size"] == (800.0, 600.0)
    assert w.state.properties["strokes"] == []
    assert w.state.properties["current_stroke"] == []


def test_drawing_widget_custom_props():
    """DrawingWidget accepts custom constructor properties."""
    w = DrawingWidget(
        "canvas-2",
        color=(0.0, 1.0, 0.0, 1.0),
        brush_size=10.0,
        is_eraser=True,
        brush_style="dashed",
        size=(400.0, 300.0),
    )

    assert w.state.properties["color"] == (0.0, 1.0, 0.0, 1.0)
    assert w.state.properties["brush_size"] == 10.0
    assert w.state.properties["is_eraser"] is True
    assert w.state.properties["brush_style"] == "dashed"
    assert w.state.properties["size"] == (400.0, 300.0)


def test_drawing_widget_clear():
    """clear() resets strokes and current_stroke."""
    w = DrawingWidget("canvas-3")
    w.state.properties["strokes"] = [[(0.0, 0.0), (1.0, 1.0)]]
    w.state.properties["current_stroke"] = [(2.0, 2.0)]

    w.clear()

    assert w.state.properties["strokes"] == []
    assert w.state.properties["current_stroke"] == []


def test_drawing_widget_undo_removes_last_stroke():
    """undo() removes the most-recently completed stroke."""
    w = DrawingWidget("canvas-4")
    stroke_a = [(0.0, 0.0), (1.0, 1.0)]
    stroke_b = [(2.0, 2.0), (3.0, 3.0)]
    w.state.properties["strokes"] = [stroke_a, stroke_b]

    w.undo()

    assert w.state.properties["strokes"] == [stroke_a]


def test_drawing_widget_undo_on_empty_is_noop():
    """undo() on an empty canvas does not raise."""
    w = DrawingWidget("canvas-5")
    w.undo()  # should not raise
    assert w.state.properties["strokes"] == []


def test_drawing_widget_serialize():
    """serialize() round-trips through the widget state."""
    w = DrawingWidget("canvas-6", brush_size=12.0)
    data = w.serialize()

    assert data["widget_id"] == "canvas-6"
    assert data["properties"]["brush_size"] == 12.0


# ---------------------------------------------------------------------------
# BrushWidget — initialization
# ---------------------------------------------------------------------------


def test_brush_widget_defaults():
    """BrushWidget initializes with expected default properties."""
    w = BrushWidget("brush-1")

    assert w.widget_id == "brush-1"
    assert w.state.properties["color"] == (1.0, 0.0, 0.0, 1.0)
    assert w.state.properties["brush_size"] == 5.0
    assert w.state.properties["is_eraser"] is False
    assert w.state.properties["brush_style"] == "solid"


def test_brush_widget_serialize():
    """BrushWidget serialize includes expected keys."""
    w = BrushWidget("brush-2", brush_size=20.0)
    data = w.serialize()

    assert data["widget_id"] == "brush-2"
    assert data["properties"]["brush_size"] == 20.0


# ---------------------------------------------------------------------------
# CanvasMenuWidget — initialization
# ---------------------------------------------------------------------------


def test_canvas_menu_widget_defaults():
    """CanvasMenuWidget initializes with expected default properties."""
    w = CanvasMenuWidget("menu-1")

    assert w.widget_id == "menu-1"
    assert w.state.properties["can_undo"] is True
    assert w.state.properties["can_redo"] is True
    assert w.state.properties["history_size"] == 10


def test_canvas_menu_widget_serialize():
    """CanvasMenuWidget serialize includes expected keys."""
    w = CanvasMenuWidget("menu-2", history_size=20)
    data = w.serialize()

    assert data["widget_id"] == "menu-2"
    assert data["properties"]["history_size"] == 20


# ---------------------------------------------------------------------------
# WidgetFactory registration
# ---------------------------------------------------------------------------


def test_drawing_widgets_registered_in_factory():
    """WidgetRegistry pre-registers all three drawing widget types."""
    registry = WidgetRegistry()
    types = registry.factory.list_types()

    assert "drawing_area" in types
    assert "brush_controls" in types
    assert "canvas_menu" in types


def test_factory_create_drawing_area():
    """factory.create('drawing_area', ...) returns a DrawingWidget."""
    registry = WidgetRegistry()
    widget = registry.factory.create("drawing_area", "w1")

    assert isinstance(widget, DrawingWidget)
    assert widget.widget_id == "w1"


def test_factory_create_brush_controls():
    """factory.create('brush_controls', ...) returns a BrushWidget."""
    registry = WidgetRegistry()
    widget = registry.factory.create("brush_controls", "w2")

    assert isinstance(widget, BrushWidget)
    assert widget.widget_id == "w2"


def test_factory_create_canvas_menu():
    """factory.create('canvas_menu', ...) returns a CanvasMenuWidget."""
    registry = WidgetRegistry()
    widget = registry.factory.create("canvas_menu", "w3")

    assert isinstance(widget, CanvasMenuWidget)
    assert widget.widget_id == "w3"


def test_factory_create_with_props():
    """factory.create passes keyword props through to the widget constructor."""
    registry = WidgetRegistry()
    widget = registry.factory.create("drawing_area", "w4", brush_size=15.0)

    assert isinstance(widget, DrawingWidget)
    assert widget.state.properties["brush_size"] == 15.0
