"""Tests for drawing widgets.

Covers initialization, state mutation (clear/undo/shapes), serialization,
and WidgetFactory registration. Render tests are omitted because
calling widget.render() outside an active ImGui context segfaults.
"""

from champi_imgui.core.widget import WidgetRegistry
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
    """clear() resets strokes, current_stroke, and shapes."""
    w = DrawingWidget("canvas-3")
    w.state.properties["strokes"] = [[(0.0, 0.0), (1.0, 1.0)]]
    w.state.properties["current_stroke"] = [(2.0, 2.0)]
    w.state.properties["shapes"] = [{"type": "rect", "x1": 0, "y1": 0, "x2": 10, "y2": 10, "color": (1, 0, 0, 1), "thickness": 2.0}]

    w.clear()

    assert w.state.properties["strokes"] == []
    assert w.state.properties["current_stroke"] == []
    assert w.state.properties["shapes"] == []


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
# DrawingWidget — shape support
# ---------------------------------------------------------------------------


def test_shapes_default_empty():
    """New DrawingWidget has empty shapes list."""
    w = DrawingWidget("canvas-s0")
    assert w.state.properties["shapes"] == []


def test_add_shape_rect():
    """add_shape() adds a rect shape to the shapes list."""
    w = DrawingWidget("canvas-s1")
    w.add_shape("rect", color=(1.0, 0.0, 0.0, 1.0), thickness=2.0, x1=10.0, y1=20.0, x2=100.0, y2=80.0)

    shapes = w.state.properties["shapes"]
    assert len(shapes) == 1
    s = shapes[0]
    assert s["type"] == "rect"
    assert s["color"] == (1.0, 0.0, 0.0, 1.0)
    assert s["thickness"] == 2.0
    assert s["x1"] == 10.0
    assert s["y1"] == 20.0
    assert s["x2"] == 100.0
    assert s["y2"] == 80.0


def test_add_shape_circle():
    """add_shape() adds a circle shape to the shapes list."""
    w = DrawingWidget("canvas-s2")
    w.add_shape("circle", color=(0.0, 1.0, 0.0, 1.0), thickness=3.0, cx=50.0, cy=50.0, radius=30.0)

    shapes = w.state.properties["shapes"]
    assert len(shapes) == 1
    s = shapes[0]
    assert s["type"] == "circle"
    assert s["cx"] == 50.0
    assert s["cy"] == 50.0
    assert s["radius"] == 30.0


def test_add_shape_arrow():
    """add_shape() adds an arrow shape to the shapes list."""
    w = DrawingWidget("canvas-s3")
    w.add_shape("arrow", x1=0.0, y1=0.0, x2=100.0, y2=100.0)

    shapes = w.state.properties["shapes"]
    assert len(shapes) == 1
    s = shapes[0]
    assert s["type"] == "arrow"
    assert s["x1"] == 0.0
    assert s["x2"] == 100.0


def test_add_shape_line():
    """add_shape() adds a line shape to the shapes list."""
    w = DrawingWidget("canvas-s4")
    w.add_shape("line", color=(0.0, 0.5, 1.0, 1.0), thickness=1.5, x1=5.0, y1=5.0, x2=200.0, y2=150.0)

    shapes = w.state.properties["shapes"]
    assert len(shapes) == 1
    s = shapes[0]
    assert s["type"] == "line"
    assert s["thickness"] == 1.5


def test_clear_shapes():
    """clear_shapes() empties the shapes list."""
    w = DrawingWidget("canvas-s5")
    w.add_shape("rect", x1=0.0, y1=0.0, x2=10.0, y2=10.0)
    w.add_shape("line", x1=0.0, y1=0.0, x2=50.0, y2=50.0)
    assert len(w.state.properties["shapes"]) == 2

    w.clear_shapes()
    assert w.state.properties["shapes"] == []


def test_clear_also_clears_shapes():
    """clear() resets shapes in addition to strokes."""
    w = DrawingWidget("canvas-s6")
    w.state.properties["strokes"] = [[(0.0, 0.0), (1.0, 1.0)]]
    w.add_shape("circle", cx=50.0, cy=50.0, radius=20.0)

    w.clear()

    assert w.state.properties["strokes"] == []
    assert w.state.properties["shapes"] == []


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


def test_canvas_menu_drawing_widget_id():
    """CanvasMenuWidget stores drawing_widget_id in properties."""
    w = CanvasMenuWidget("menu-3", drawing_widget_id="canvas-1")

    assert w.state.properties["drawing_widget_id"] == "canvas-1"


def test_canvas_menu_serialize_includes_drawing_widget_id():
    """serialize() includes drawing_widget_id."""
    w = CanvasMenuWidget("menu-4", drawing_widget_id="canvas-99")
    data = w.serialize()

    assert data["properties"]["drawing_widget_id"] == "canvas-99"


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
