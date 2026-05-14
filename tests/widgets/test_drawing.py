"""Tests for drawing widgets.

Covers initialization, state mutation (clear/undo), serialization,
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
    """clear() resets strokes, current_stroke, and redo_stack."""
    w = DrawingWidget("canvas-3")
    w.state.properties["strokes"] = [[(0.0, 0.0), (1.0, 1.0)]]
    w.state.properties["current_stroke"] = [(2.0, 2.0)]
    w.state.properties["redo_stack"] = [[(3.0, 3.0), (4.0, 4.0)]]

    w.clear()

    assert w.state.properties["strokes"] == []
    assert w.state.properties["current_stroke"] == []
    assert w.state.properties["redo_stack"] == []


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


def test_drawing_widget_add_shape_rect():
    """add_shape() appends a rect shape dict to state.properties['shapes']."""
    w = DrawingWidget("canvas-shape-1")
    w.add_shape("rect", x1=10.0, y1=20.0, x2=110.0, y2=120.0)

    shapes = w.state.properties["shapes"]
    assert len(shapes) == 1
    assert shapes[0]["type"] == "rect"
    assert shapes[0]["x1"] == 10.0
    assert shapes[0]["x2"] == 110.0


def test_drawing_widget_add_shape_circle():
    """add_shape() appends a circle shape dict with cx, cy, radius."""
    w = DrawingWidget("canvas-shape-2")
    w.add_shape("circle", cx=50.0, cy=50.0, radius=30.0)

    shapes = w.state.properties["shapes"]
    assert len(shapes) == 1
    assert shapes[0]["type"] == "circle"
    assert shapes[0]["radius"] == 30.0


def test_drawing_widget_add_shape_color_default():
    """add_shape() uses default blue color when none supplied."""
    w = DrawingWidget("canvas-shape-3")
    w.add_shape("line", x1=0.0, y1=0.0, x2=10.0, y2=10.0)

    assert w.state.properties["shapes"][0]["color"] == (0.0, 0.5, 1.0, 1.0)


def test_drawing_widget_clear_shapes():
    """clear_shapes() removes all shapes without touching strokes."""
    w = DrawingWidget("canvas-shape-4")
    w.add_shape("line", x1=0.0, y1=0.0, x2=5.0, y2=5.0)
    w.state.properties["strokes"] = [[(0.0, 0.0), (1.0, 1.0)]]

    w.clear_shapes()

    assert w.state.properties["shapes"] == []
    assert len(w.state.properties["strokes"]) == 1


def test_drawing_widget_clear_includes_shapes_and_annotations():
    """clear() removes strokes, shapes, and annotations."""
    w = DrawingWidget("canvas-shape-5")
    w.add_shape("rect", x1=0.0, y1=0.0, x2=10.0, y2=10.0)
    w.add_annotation(5.0, 5.0, "hello")
    w.state.properties["strokes"] = [[(0.0, 0.0), (1.0, 1.0)]]

    w.clear()

    assert w.state.properties["shapes"] == []
    assert w.state.properties["annotations"] == []
    assert w.state.properties["strokes"] == []


def test_drawing_widget_add_annotation():
    """add_annotation() appends a text annotation dict."""
    w = DrawingWidget("canvas-ann-1")
    w.add_annotation(10.0, 20.0, "label", color=(1.0, 0.0, 0.0, 1.0), font_size=14.0)

    annotations = w.state.properties["annotations"]
    assert len(annotations) == 1
    ann = annotations[0]
    assert ann["type"] == "text"
    assert ann["x"] == 10.0
    assert ann["y"] == 20.0
    assert ann["text"] == "label"
    assert ann["color"] == (1.0, 0.0, 0.0, 1.0)
    assert ann["font_size"] == 14.0


def test_undo_pushes_to_redo_stack():
    """undo() moves the last stroke onto the redo stack."""
    w = DrawingWidget("canvas-undo-redo-1")
    stroke_a = [(0.0, 0.0), (1.0, 1.0)]
    stroke_b = [(2.0, 2.0), (3.0, 3.0)]
    w.state.properties["strokes"] = [stroke_a, stroke_b]

    w.undo()

    assert w.state.properties["strokes"] == [stroke_a]
    assert w.state.properties["redo_stack"] == [stroke_b]


def test_redo_restores_stroke():
    """redo() moves the last redo entry back into strokes."""
    w = DrawingWidget("canvas-undo-redo-2")
    stroke_a = [(0.0, 0.0), (1.0, 1.0)]
    stroke_b = [(2.0, 2.0), (3.0, 3.0)]
    w.state.properties["strokes"] = [stroke_a]
    w.state.properties["redo_stack"] = [stroke_b]

    w.redo()

    assert w.state.properties["strokes"] == [stroke_a, stroke_b]
    assert w.state.properties["redo_stack"] == []


def test_redo_on_empty_is_noop():
    """redo() with no redo history does not raise."""
    w = DrawingWidget("canvas-undo-redo-3")
    w.redo()  # should not raise
    assert w.state.properties["strokes"] == []


def test_clear_resets_redo_stack():
    """clear() wipes the redo stack in addition to strokes."""
    w = DrawingWidget("canvas-undo-redo-4")
    w.state.properties["redo_stack"] = [[(5.0, 5.0), (6.0, 6.0)]]
    w.clear()
    assert w.state.properties["redo_stack"] == []


def test_can_undo_false_when_empty():
    """can_undo is False when there are no strokes."""
    w = DrawingWidget("canvas-can-undo-1")
    assert w.can_undo is False


def test_can_undo_true_with_strokes():
    """can_undo is True when strokes exist."""
    w = DrawingWidget("canvas-can-undo-2")
    w.state.properties["strokes"] = [[(0.0, 0.0), (1.0, 1.0)]]
    assert w.can_undo is True


def test_can_redo_false_when_empty():
    """can_redo is False when the redo stack is empty."""
    w = DrawingWidget("canvas-can-redo-1")
    assert w.can_redo is False


def test_can_redo_true_after_undo():
    """can_redo is True after an undo operation."""
    w = DrawingWidget("canvas-can-redo-2")
    w.state.properties["strokes"] = [[(0.0, 0.0), (1.0, 1.0)]]
    w.undo()
    assert w.can_redo is True


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
