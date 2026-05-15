"""Integration tests for drawing widget MCP tools.

Tests call tool functions directly against a real CanvasManager with
auto_start=False (no ImGui render thread required). Widget state
mutations are verified without an active ImGui context.
"""

import contextlib
import uuid

import pytest

import champi_imgui.server.main as server
from champi_imgui.core.canvas import CanvasManager
from champi_imgui.widgets.drawing import DrawingWidget


@pytest.fixture(autouse=True)
def fresh_canvas_manager(monkeypatch):
    """Swap the module-level canvas_manager with a clean instance per test."""
    manager = CanvasManager()
    monkeypatch.setattr(manager, "ensure_canvas_running", lambda canvas_id: True)
    original = server.canvas_manager
    server.canvas_manager = manager
    yield manager
    for canvas in list(manager.canvases.values()):
        with contextlib.suppress(Exception):
            canvas.shm_manager.cleanup()
    server.canvas_manager = original


@pytest.fixture()
def cid() -> str:
    """Return a unique canvas ID per test."""
    return f"c_{uuid.uuid4().hex[:8]}"


def _make_canvas_with_drawing(cid: str, widget_id: str = "draw1") -> DrawingWidget:
    """Create a canvas, register a DrawingWidget directly, and return it."""
    server.create_canvas.fn(cid, auto_start=False)
    canvas = server.canvas_manager.get_canvas(cid)
    assert canvas is not None
    widget = DrawingWidget(widget_id)
    canvas.widget_registry._widgets[widget_id] = widget
    return widget


# ---------------------------------------------------------------------------
# drawing_clear
# ---------------------------------------------------------------------------


class TestDrawingClear:
    def test_clear_resets_strokes(self, cid):
        """drawing_clear removes all strokes from the widget."""
        widget = _make_canvas_with_drawing(cid)
        widget.state.properties["strokes"] = [[(0.0, 0.0), (1.0, 1.0)]]

        result = server.drawing_clear.fn(cid, "draw1")

        assert result["success"] is True
        assert widget.state.properties["strokes"] == []

    def test_clear_resets_shapes_and_annotations(self, cid):
        """drawing_clear removes shapes and annotations in addition to strokes."""
        widget = _make_canvas_with_drawing(cid)
        widget.add_shape("rect", x1=0.0, y1=0.0, x2=10.0, y2=10.0)
        widget.add_annotation(5.0, 5.0, "label")
        widget.state.properties["strokes"] = [[(0.0, 0.0), (1.0, 1.0)]]

        result = server.drawing_clear.fn(cid, "draw1")

        assert result["success"] is True
        assert widget.state.properties["shapes"] == []
        assert widget.state.properties["annotations"] == []
        assert widget.state.properties["strokes"] == []

    def test_clear_missing_canvas(self):
        """drawing_clear returns error when canvas does not exist."""
        result = server.drawing_clear.fn("missing", "draw1")

        assert result["success"] is False
        assert "not found" in result["error"]

    def test_clear_missing_widget(self, cid):
        """drawing_clear returns error when widget does not exist on canvas."""
        server.create_canvas.fn(cid, auto_start=False)

        result = server.drawing_clear.fn(cid, "nonexistent")

        assert result["success"] is False
        assert "not found" in result["error"]

    def test_clear_wrong_widget_type(self, cid):
        """drawing_clear returns error when widget is not a DrawingWidget."""
        server.create_canvas.fn(cid, auto_start=False)
        server.add_button.fn(cid, "btn1")

        result = server.drawing_clear.fn(cid, "btn1")

        assert result["success"] is False
        assert "not a DrawingWidget" in result["error"]


# ---------------------------------------------------------------------------
# drawing_undo
# ---------------------------------------------------------------------------


class TestDrawingUndo:
    def test_undo_removes_last_stroke(self, cid):
        """drawing_undo removes the last completed stroke."""
        widget = _make_canvas_with_drawing(cid)
        stroke_a = [(0.0, 0.0), (1.0, 1.0)]
        stroke_b = [(2.0, 2.0), (3.0, 3.0)]
        widget.state.properties["strokes"] = [stroke_a, stroke_b]

        result = server.drawing_undo.fn(cid, "draw1")

        assert result["success"] is True
        assert widget.state.properties["strokes"] == [stroke_a]

    def test_undo_on_empty_is_safe(self, cid):
        """drawing_undo on an empty canvas does not raise."""
        _make_canvas_with_drawing(cid)

        result = server.drawing_undo.fn(cid, "draw1")

        assert result["success"] is True
        assert server.canvas_manager.get_canvas(cid) is not None

    def test_undo_pushes_to_redo_stack(self, cid):
        """drawing_undo moves the popped stroke onto the redo stack."""
        widget = _make_canvas_with_drawing(cid)
        stroke = [(0.0, 0.0), (5.0, 5.0)]
        widget.state.properties["strokes"] = [stroke]

        server.drawing_undo.fn(cid, "draw1")

        assert widget.state.properties["redo_stack"] == [stroke]

    def test_undo_missing_canvas(self):
        """drawing_undo returns error when canvas does not exist."""
        result = server.drawing_undo.fn("missing", "draw1")

        assert result["success"] is False
        assert "not found" in result["error"]

    def test_undo_missing_widget(self, cid):
        """drawing_undo returns error when widget does not exist."""
        server.create_canvas.fn(cid, auto_start=False)

        result = server.drawing_undo.fn(cid, "nonexistent")

        assert result["success"] is False
        assert "not found" in result["error"]


# ---------------------------------------------------------------------------
# drawing_redo
# ---------------------------------------------------------------------------


class TestDrawingRedo:
    def test_redo_restores_stroke(self, cid):
        """drawing_redo moves the last redo entry back into strokes."""
        widget = _make_canvas_with_drawing(cid)
        stroke_a = [(0.0, 0.0), (1.0, 1.0)]
        stroke_b = [(2.0, 2.0), (3.0, 3.0)]
        widget.state.properties["strokes"] = [stroke_a]
        widget.state.properties["redo_stack"] = [stroke_b]

        result = server.drawing_redo.fn(cid, "draw1")

        assert result["success"] is True
        assert widget.state.properties["strokes"] == [stroke_a, stroke_b]
        assert widget.state.properties["redo_stack"] == []

    def test_redo_on_empty_is_safe(self, cid):
        """drawing_redo with no redo history does not raise."""
        _make_canvas_with_drawing(cid)

        result = server.drawing_redo.fn(cid, "draw1")

        assert result["success"] is True

    def test_redo_missing_canvas(self):
        """drawing_redo returns error when canvas does not exist."""
        result = server.drawing_redo.fn("missing", "draw1")

        assert result["success"] is False
        assert "not found" in result["error"]

    def test_redo_missing_widget(self, cid):
        """drawing_redo returns error when widget does not exist."""
        server.create_canvas.fn(cid, auto_start=False)

        result = server.drawing_redo.fn(cid, "nonexistent")

        assert result["success"] is False
        assert "not found" in result["error"]


# ---------------------------------------------------------------------------
# drawing_add_shape
# ---------------------------------------------------------------------------


class TestDrawingAddShape:
    def test_add_rect(self, cid):
        """drawing_add_shape adds a rect to the shapes list."""
        widget = _make_canvas_with_drawing(cid)

        result = server.drawing_add_shape.fn(
            cid, "draw1", "rect", x1=10.0, y1=20.0, x2=110.0, y2=120.0
        )

        assert result["success"] is True
        shapes = widget.state.properties["shapes"]
        assert len(shapes) == 1
        assert shapes[0]["type"] == "rect"
        assert shapes[0]["x1"] == 10.0
        assert shapes[0]["y1"] == 20.0
        assert shapes[0]["x2"] == 110.0
        assert shapes[0]["y2"] == 120.0

    def test_add_circle(self, cid):
        """drawing_add_shape adds a circle using cx, cy, radius."""
        widget = _make_canvas_with_drawing(cid)

        result = server.drawing_add_shape.fn(
            cid, "draw1", "circle", cx=50.0, cy=60.0, radius=30.0
        )

        assert result["success"] is True
        shapes = widget.state.properties["shapes"]
        assert len(shapes) == 1
        assert shapes[0]["type"] == "circle"
        assert shapes[0]["cx"] == 50.0
        assert shapes[0]["cy"] == 60.0
        assert shapes[0]["radius"] == 30.0

    def test_add_arrow(self, cid):
        """drawing_add_shape adds an arrow shape."""
        widget = _make_canvas_with_drawing(cid)

        result = server.drawing_add_shape.fn(
            cid, "draw1", "arrow", x1=0.0, y1=0.0, x2=100.0, y2=100.0
        )

        assert result["success"] is True
        assert widget.state.properties["shapes"][0]["type"] == "arrow"

    def test_add_line(self, cid):
        """drawing_add_shape adds a line shape."""
        widget = _make_canvas_with_drawing(cid)

        result = server.drawing_add_shape.fn(
            cid, "draw1", "line", x1=5.0, y1=5.0, x2=50.0, y2=50.0
        )

        assert result["success"] is True
        assert widget.state.properties["shapes"][0]["type"] == "line"

    def test_default_color_applied_when_none(self, cid):
        """drawing_add_shape uses blue default color when color is not specified."""
        widget = _make_canvas_with_drawing(cid)

        server.drawing_add_shape.fn(cid, "draw1", "line")

        color = widget.state.properties["shapes"][0]["color"]
        assert color == (0.0, 0.5, 1.0, 1.0)

    def test_custom_color_applied(self, cid):
        """drawing_add_shape stores the provided color on the shape."""
        widget = _make_canvas_with_drawing(cid)

        server.drawing_add_shape.fn(cid, "draw1", "rect", color=[1.0, 0.0, 0.0, 1.0])

        color = widget.state.properties["shapes"][0]["color"]
        assert color == (1.0, 0.0, 0.0, 1.0)

    def test_add_shape_missing_canvas(self):
        """drawing_add_shape returns error when canvas does not exist."""
        result = server.drawing_add_shape.fn("missing", "draw1", "rect")

        assert result["success"] is False
        assert "not found" in result["error"]

    def test_add_shape_missing_widget(self, cid):
        """drawing_add_shape returns error when widget does not exist."""
        server.create_canvas.fn(cid, auto_start=False)

        result = server.drawing_add_shape.fn(cid, "nonexistent", "rect")

        assert result["success"] is False
        assert "not found" in result["error"]


# ---------------------------------------------------------------------------
# drawing_add_text
# ---------------------------------------------------------------------------


class TestDrawingAddText:
    def test_add_annotation(self, cid):
        """drawing_add_text appends a text annotation to the widget."""
        widget = _make_canvas_with_drawing(cid)

        result = server.drawing_add_text.fn(cid, "draw1", x=10.0, y=20.0, text="Hello")

        assert result["success"] is True
        annotations = widget.state.properties["annotations"]
        assert len(annotations) == 1
        ann = annotations[0]
        assert ann["type"] == "text"
        assert ann["x"] == 10.0
        assert ann["y"] == 20.0
        assert ann["text"] == "Hello"

    def test_add_text_default_color(self, cid):
        """drawing_add_text uses white as default color."""
        widget = _make_canvas_with_drawing(cid)

        server.drawing_add_text.fn(cid, "draw1", x=0.0, y=0.0, text="hi")

        color = widget.state.properties["annotations"][0]["color"]
        assert color == (1.0, 1.0, 1.0, 1.0)

    def test_add_text_custom_color(self, cid):
        """drawing_add_text stores the provided color."""
        widget = _make_canvas_with_drawing(cid)

        server.drawing_add_text.fn(
            cid, "draw1", x=0.0, y=0.0, text="hi", color=[1.0, 0.0, 0.0, 1.0]
        )

        color = widget.state.properties["annotations"][0]["color"]
        assert color == (1.0, 0.0, 0.0, 1.0)

    def test_add_text_missing_canvas(self):
        """drawing_add_text returns error when canvas does not exist."""
        result = server.drawing_add_text.fn("missing", "draw1", x=0.0, y=0.0, text="x")

        assert result["success"] is False
        assert "not found" in result["error"]

    def test_add_text_missing_widget(self, cid):
        """drawing_add_text returns error when widget does not exist."""
        server.create_canvas.fn(cid, auto_start=False)

        result = server.drawing_add_text.fn(cid, "nonexistent", x=0.0, y=0.0, text="x")

        assert result["success"] is False
        assert "not found" in result["error"]


# ---------------------------------------------------------------------------
# drawing_export_strokes / drawing_import_strokes
# ---------------------------------------------------------------------------


class TestDrawingExportImport:
    def test_export_returns_strokes(self, cid):
        """drawing_export_strokes includes the strokes list."""
        widget = _make_canvas_with_drawing(cid)
        stroke = [(0.0, 0.0), (5.0, 5.0)]
        widget.state.properties["strokes"] = [stroke]

        result = server.drawing_export_strokes.fn(cid, "draw1")

        assert result["success"] is True
        assert result["data"]["strokes"] == [stroke]

    def test_export_includes_shapes_by_default(self, cid):
        """drawing_export_strokes includes shapes when include_shapes=True."""
        widget = _make_canvas_with_drawing(cid)
        widget.add_shape("rect", x1=0.0, y1=0.0, x2=10.0, y2=10.0)

        result = server.drawing_export_strokes.fn(cid, "draw1")

        assert result["success"] is True
        assert "shapes" in result["data"]
        assert len(result["data"]["shapes"]) == 1

    def test_export_excludes_shapes_when_flag_false(self, cid):
        """drawing_export_strokes omits shapes when include_shapes=False."""
        widget = _make_canvas_with_drawing(cid)
        widget.add_shape("rect", x1=0.0, y1=0.0, x2=10.0, y2=10.0)

        result = server.drawing_export_strokes.fn(cid, "draw1", include_shapes=False)

        assert result["success"] is True
        assert "shapes" not in result["data"]

    def test_import_replaces_strokes(self, cid):
        """drawing_import_strokes replaces existing strokes when merge=False."""
        widget = _make_canvas_with_drawing(cid)
        widget.state.properties["strokes"] = [[(0.0, 0.0), (1.0, 1.0)]]

        new_stroke = [(2.0, 2.0), (3.0, 3.0)]
        result = server.drawing_import_strokes.fn(cid, "draw1", strokes=[new_stroke])

        assert result["success"] is True
        assert widget.state.properties["strokes"] == [new_stroke]

    def test_import_merges_strokes(self, cid):
        """drawing_import_strokes appends strokes when merge=True."""
        widget = _make_canvas_with_drawing(cid)
        old_stroke = [(0.0, 0.0), (1.0, 1.0)]
        widget.state.properties["strokes"] = [old_stroke]

        new_stroke = [(2.0, 2.0), (3.0, 3.0)]
        result = server.drawing_import_strokes.fn(
            cid, "draw1", strokes=[new_stroke], merge=True
        )

        assert result["success"] is True
        assert widget.state.properties["strokes"] == [old_stroke, new_stroke]

    def test_import_shapes(self, cid):
        """drawing_import_strokes replaces shapes list when merge=False."""
        widget = _make_canvas_with_drawing(cid)
        shape = {"type": "rect", "x1": 0.0, "y1": 0.0, "x2": 10.0, "y2": 10.0}
        result = server.drawing_import_strokes.fn(cid, "draw1", shapes=[shape])

        assert result["success"] is True
        assert widget.state.properties["shapes"] == [shape]

    def test_export_import_roundtrip(self, cid):
        """Exported data can be re-imported to reproduce the original state."""
        widget = _make_canvas_with_drawing(cid)
        stroke = [(1.0, 2.0), (3.0, 4.0)]
        widget.state.properties["strokes"] = [stroke]
        widget.add_shape("circle", cx=5.0, cy=5.0, radius=3.0)
        widget.add_annotation(1.0, 1.0, "note")

        export_result = server.drawing_export_strokes.fn(cid, "draw1")
        assert export_result["success"] is True
        exported = export_result["data"]

        widget.clear()
        import_result = server.drawing_import_strokes.fn(
            cid,
            "draw1",
            strokes=exported["strokes"],
            shapes=exported["shapes"],
            annotations=exported["annotations"],
        )
        assert import_result["success"] is True
        assert widget.state.properties["strokes"] == [stroke]
        assert len(widget.state.properties["shapes"]) == 1
        assert len(widget.state.properties["annotations"]) == 1

    def test_export_missing_canvas(self):
        """drawing_export_strokes returns error when canvas does not exist."""
        result = server.drawing_export_strokes.fn("missing", "draw1")

        assert result["success"] is False
        assert "not found" in result["error"]

    def test_import_missing_canvas(self):
        """drawing_import_strokes returns error when canvas does not exist."""
        result = server.drawing_import_strokes.fn("missing", "draw1", strokes=[])

        assert result["success"] is False
        assert "not found" in result["error"]
