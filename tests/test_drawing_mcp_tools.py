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
# drawing_add_llm_stroke
# ---------------------------------------------------------------------------


class TestDrawingAddLlmStroke:
    def test_drawing_add_llm_stroke_success(self, cid):
        """drawing_add_llm_stroke appends a stroke with author='llm'."""
        widget = _make_canvas_with_drawing(cid)

        result = server.drawing_add_llm_stroke.fn(
            cid,
            "draw1",
            points=[[10.0, 20.0], [30.0, 40.0], [50.0, 60.0]],
        )

        assert result["success"] is True
        strokes = widget.state.properties["strokes"]
        assert len(strokes) == 1
        s = strokes[0]
        assert s["author"] == "llm"
        assert s["tool"] == "brush"
        assert s["points"] == [(10.0, 20.0), (30.0, 40.0), (50.0, 60.0)]
        assert result["data"]["stroke_count"] == 1

    def test_drawing_add_llm_stroke_default_color(self, cid):
        """drawing_add_llm_stroke uses LLM blue when color is not specified."""
        from champi_imgui.widgets.drawing import AUTHOR_COLORS

        widget = _make_canvas_with_drawing(cid)

        server.drawing_add_llm_stroke.fn(cid, "draw1", points=[[0.0, 0.0], [1.0, 1.0]])

        color = widget.state.properties["strokes"][0]["color"]
        assert color == AUTHOR_COLORS["llm"]

    def test_drawing_add_llm_stroke_custom_color(self, cid):
        """drawing_add_llm_stroke stores the provided color."""
        widget = _make_canvas_with_drawing(cid)

        server.drawing_add_llm_stroke.fn(
            cid,
            "draw1",
            points=[[0.0, 0.0], [1.0, 1.0]],
            color=[1.0, 0.0, 0.0, 1.0],
        )

        color = widget.state.properties["strokes"][0]["color"]
        assert color == (1.0, 0.0, 0.0, 1.0)

    def test_drawing_add_llm_stroke_missing_canvas(self):
        """drawing_add_llm_stroke returns error when canvas does not exist."""
        result = server.drawing_add_llm_stroke.fn(
            "missing", "draw1", points=[[0.0, 0.0], [1.0, 1.0]]
        )

        assert result["success"] is False
        assert "not found" in result["error"]

    def test_drawing_add_llm_stroke_missing_widget(self, cid):
        """drawing_add_llm_stroke returns error when widget does not exist."""
        server.create_canvas.fn(cid, auto_start=False)

        result = server.drawing_add_llm_stroke.fn(
            cid, "nonexistent", points=[[0.0, 0.0], [1.0, 1.0]]
        )

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

        # Clear the widget then re-import
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


# ---------------------------------------------------------------------------
# TestExportImportWithMetadata
# ---------------------------------------------------------------------------


class TestExportImportWithMetadata:
    def test_export_preserves_stroke_author(self, cid):
        """Exported strokes retain their author field."""
        widget = _make_canvas_with_drawing(cid)
        stroke = {
            "points": [(0.0, 0.0), (1.0, 1.0)],
            "author": "user",
            "timestamp": 1000.0,
            "tool": "brush",
            "color": (1.0, 0.0, 0.0, 1.0),
            "brush_size": 5.0,
            "brush_style": "solid",
        }
        widget.state.properties["strokes"] = [stroke]

        result = server.drawing_export_strokes.fn(cid, "draw1")

        assert result["success"] is True
        exported_stroke = result["data"]["strokes"][0]
        assert exported_stroke["author"] == "user"

    def test_export_preserves_stroke_timestamp(self, cid):
        """Exported strokes retain their timestamp field."""
        widget = _make_canvas_with_drawing(cid)
        fixed_ts = 1_700_000_000.0
        stroke = {
            "points": [(0.0, 0.0), (1.0, 1.0)],
            "author": "llm",
            "timestamp": fixed_ts,
            "tool": "brush",
            "color": (0.0, 0.5, 1.0, 1.0),
            "brush_size": 3.0,
            "brush_style": "solid",
        }
        widget.state.properties["strokes"] = [stroke]

        result = server.drawing_export_strokes.fn(cid, "draw1")

        assert result["success"] is True
        assert result["data"]["strokes"][0]["timestamp"] == fixed_ts

    def test_import_roundtrip_preserves_metadata(self, cid):
        """Export then import keeps author, timestamp, tool intact."""
        widget = _make_canvas_with_drawing(cid)
        fixed_ts = 1_700_000_000.0
        original_stroke = {
            "points": [(5.0, 10.0), (15.0, 20.0)],
            "author": "llm",
            "timestamp": fixed_ts,
            "tool": "brush",
            "color": (0.0, 0.5, 1.0, 1.0),
            "brush_size": 3.0,
            "brush_style": "dashed",
        }
        widget.state.properties["strokes"] = [original_stroke]

        export_result = server.drawing_export_strokes.fn(cid, "draw1")
        assert export_result["success"] is True

        widget.clear()
        import_result = server.drawing_import_strokes.fn(
            cid, "draw1", strokes=export_result["data"]["strokes"]
        )

        assert import_result["success"] is True
        restored = widget.state.properties["strokes"][0]
        assert restored["author"] == "llm"
        assert restored["timestamp"] == fixed_ts
        assert restored["tool"] == "brush"
        assert restored["brush_style"] == "dashed"

    def test_llm_stroke_author_preserved_in_export(self, cid):
        """A stroke added via drawing_add_llm_stroke has author=llm in export."""
        _make_canvas_with_drawing(cid)

        server.drawing_add_llm_stroke.fn(
            cid, "draw1", points=[[0.0, 0.0], [10.0, 10.0]]
        )

        result = server.drawing_export_strokes.fn(cid, "draw1")

        assert result["success"] is True
        strokes = result["data"]["strokes"]
        assert len(strokes) == 1
        assert strokes[0]["author"] == "llm"

    def test_import_merge_keeps_existing_author(self, cid):
        """Merging import does not overwrite existing stroke metadata."""
        widget = _make_canvas_with_drawing(cid)
        existing_stroke = {
            "points": [(0.0, 0.0), (1.0, 1.0)],
            "author": "user",
            "timestamp": 999.0,
            "tool": "brush",
            "color": (1.0, 0.0, 0.0, 1.0),
            "brush_size": 5.0,
            "brush_style": "solid",
        }
        widget.state.properties["strokes"] = [existing_stroke]

        incoming_stroke = {
            "points": [(2.0, 2.0), (3.0, 3.0)],
            "author": "llm",
            "timestamp": 1234.0,
            "tool": "brush",
            "color": (0.0, 0.5, 1.0, 1.0),
            "brush_size": 3.0,
            "brush_style": "solid",
        }
        result = server.drawing_import_strokes.fn(
            cid, "draw1", strokes=[incoming_stroke], merge=True
        )

        assert result["success"] is True
        strokes = widget.state.properties["strokes"]
        assert len(strokes) == 2
        assert strokes[0]["author"] == "user"
        assert strokes[0]["timestamp"] == 999.0
        assert strokes[1]["author"] == "llm"
        assert strokes[1]["timestamp"] == 1234.0


# ---------------------------------------------------------------------------
# Regression: strokes/annotations stored in state.properties must be
# readable back from the registry after add_drawing_area (issue #79)
# ---------------------------------------------------------------------------


class TestDrawingWidgetStatePreserved:
    def test_strokes_stored_in_registry_widget(self, cid):
        """Strokes added via drawing_add_llm_stroke are visible on the widget
        retrieved from canvas.widget_registry (not a stale copy)."""
        server.create_canvas.fn(cid, auto_start=False)
        server.add_drawing_area.fn(cid, "draw1")

        server.drawing_add_llm_stroke.fn(
            cid, "draw1", points=[[0.0, 0.0], [10.0, 10.0]]
        )

        canvas = server.canvas_manager.get_canvas(cid)
        assert canvas is not None
        widget = canvas.widget_registry.get("draw1")
        assert widget is not None
        strokes = widget.state.properties.get("strokes", [])
        assert len(strokes) == 1, "Stroke must be present in the registry widget"

    def test_annotations_stored_in_registry_widget(self, cid):
        """Text annotations added via drawing_add_text are visible on the
        widget retrieved from canvas.widget_registry."""
        server.create_canvas.fn(cid, auto_start=False)
        server.add_drawing_area.fn(cid, "draw1")

        server.drawing_add_text.fn(cid, "draw1", x=5.0, y=10.0, text="hello")

        canvas = server.canvas_manager.get_canvas(cid)
        assert canvas is not None
        widget = canvas.widget_registry.get("draw1")
        assert widget is not None
        annotations = widget.state.properties.get("annotations", [])
        assert len(annotations) == 1
        assert annotations[0]["text"] == "hello"

    def test_shapes_stored_in_registry_widget(self, cid):
        """Shapes added via drawing_add_shape are visible on the widget
        retrieved from canvas.widget_registry."""
        server.create_canvas.fn(cid, auto_start=False)
        server.add_drawing_area.fn(cid, "draw1")

        server.drawing_add_shape.fn(
            cid, "draw1", "rect", x1=0.0, y1=0.0, x2=100.0, y2=100.0
        )

        canvas = server.canvas_manager.get_canvas(cid)
        assert canvas is not None
        widget = canvas.widget_registry.get("draw1")
        assert widget is not None
        shapes = widget.state.properties.get("shapes", [])
        assert len(shapes) == 1
        assert shapes[0]["type"] == "rect"


# ---------------------------------------------------------------------------
# Regression: import_canvas_json must restore DrawingWidget with its strokes
# ---------------------------------------------------------------------------


class TestDrawingWidgetImportRoundtrip:
    def test_drawing_widget_survives_export_import(self, cid, tmp_path):
        """A DrawingWidget with strokes/annotations exported to JSON and then
        re-imported must land in the new canvas's widget_registry with its
        data intact."""
        import json

        from champi_imgui.core.serialization import UIExporter
        from champi_imgui.widgets.drawing import DrawingWidget

        # Create canvas and drawing widget with data
        server.create_canvas.fn(cid, auto_start=False)
        server.add_drawing_area.fn(cid, "draw1")
        server.drawing_add_llm_stroke.fn(cid, "draw1", points=[[1.0, 2.0], [3.0, 4.0]])
        server.drawing_add_text.fn(cid, "draw1", x=5.0, y=5.0, text="label")
        server.drawing_add_shape.fn(
            cid, "draw1", "line", x1=0.0, y1=0.0, x2=50.0, y2=50.0
        )

        # Export to JSON
        canvas = server.canvas_manager.get_canvas(cid)
        assert canvas is not None
        json_str = UIExporter.export_canvas_state(canvas)
        data = json.loads(json_str)

        # Patch canvas_id to avoid collision, then import
        new_cid = cid + "_imported"
        data["canvas_id"] = new_cid
        filepath = str(tmp_path / "drawing_export.json")
        with open(filepath, "w") as f:
            json.dump(data, f)

        from champi_imgui.core.serialization import UIImporter

        imported_canvas = UIImporter.import_from_json(filepath, server.canvas_manager)
        assert imported_canvas is not None

        widget = imported_canvas.widget_registry.get("draw1")
        assert widget is not None, (
            "DrawingWidget must be in the imported canvas registry"
        )
        assert isinstance(widget, DrawingWidget)
        assert len(widget.state.properties.get("strokes", [])) == 1
        assert len(widget.state.properties.get("annotations", [])) == 1
        assert len(widget.state.properties.get("shapes", [])) == 1


# ---------------------------------------------------------------------------
# Ellipse shape and fill rendering (issue #93)
# ---------------------------------------------------------------------------


class TestEllipseShape:
    def test_add_ellipse_unfilled(self, cid):
        """drawing_add_shape stores an ellipse with cx, cy, rx, ry."""
        widget = _make_canvas_with_drawing(cid)

        result = server.drawing_add_shape.fn(
            cid, "draw1", "ellipse", cx=100.0, cy=80.0, rx=50.0, ry=30.0
        )

        assert result["success"] is True
        shapes = widget.state.properties["shapes"]
        assert len(shapes) == 1
        s = shapes[0]
        assert s["type"] == "ellipse"
        assert s["cx"] == 100.0
        assert s["cy"] == 80.0
        assert s["rx"] == 50.0
        assert s["ry"] == 30.0
        assert s["filled"] is False

    def test_add_ellipse_filled(self, cid):
        """drawing_add_shape with filled=True stores a filled ellipse (not an error)."""
        widget = _make_canvas_with_drawing(cid)

        result = server.drawing_add_shape.fn(
            cid, "draw1", "ellipse", cx=60.0, cy=40.0, rx=25.0, ry=15.0, filled=True
        )

        assert result["success"] is True
        shapes = widget.state.properties["shapes"]
        assert len(shapes) == 1
        assert shapes[0]["filled"] is True

    def test_ellipse_negative_rx_returns_error(self, cid):
        """drawing_add_shape returns error when rx <= 0."""
        _make_canvas_with_drawing(cid)

        result = server.drawing_add_shape.fn(
            cid, "draw1", "ellipse", cx=50.0, cy=50.0, rx=-10.0, ry=20.0
        )

        assert result["success"] is False
        assert "radii must be positive" in result["error"]

    def test_ellipse_zero_ry_returns_error(self, cid):
        """drawing_add_shape returns error when ry <= 0."""
        _make_canvas_with_drawing(cid)

        result = server.drawing_add_shape.fn(
            cid, "draw1", "ellipse", cx=50.0, cy=50.0, rx=20.0, ry=0.0
        )

        assert result["success"] is False
        assert "radii must be positive" in result["error"]

    def test_ellipse_in_valid_shape_types(self):
        """VALID_SHAPE_TYPES includes 'ellipse'."""
        from champi_imgui.widgets.drawing import VALID_SHAPE_TYPES

        assert "ellipse" in VALID_SHAPE_TYPES

    def test_ellipse_in_fill_supported_types(self):
        """FILL_SUPPORTED_TYPES includes 'ellipse'."""
        from champi_imgui.widgets.drawing import FILL_SUPPORTED_TYPES

        assert "ellipse" in FILL_SUPPORTED_TYPES

    def test_ellipse_roundtrip_serialize(self, cid):
        """An ellipse shape survives export and re-import unchanged."""
        widget = _make_canvas_with_drawing(cid)

        server.drawing_add_shape.fn(
            cid, "draw1", "ellipse", cx=70.0, cy=50.0, rx=35.0, ry=20.0, filled=True
        )

        export_result = server.drawing_export_strokes.fn(cid, "draw1")
        assert export_result["success"] is True
        exported_shapes = export_result["data"]["shapes"]
        assert len(exported_shapes) == 1

        widget.clear()
        import_result = server.drawing_import_strokes.fn(
            cid, "draw1", shapes=exported_shapes
        )
        assert import_result["success"] is True
        restored = widget.state.properties["shapes"][0]
        assert restored["type"] == "ellipse"
        assert restored["cx"] == 70.0
        assert restored["rx"] == 35.0
        assert restored["filled"] is True


class TestFillRendering:
    def test_rect_filled_stored(self, cid):
        """drawing_add_shape with shape_type='rect' and filled=True stores filled flag."""
        widget = _make_canvas_with_drawing(cid)

        result = server.drawing_add_shape.fn(
            cid, "draw1", "rect", x1=0.0, y1=0.0, x2=100.0, y2=50.0, filled=True
        )

        assert result["success"] is True
        shapes = widget.state.properties["shapes"]
        assert shapes[0]["filled"] is True

    def test_rect_unfilled_stored(self, cid):
        """drawing_add_shape with rect and filled=False stores filled=False."""
        widget = _make_canvas_with_drawing(cid)

        result = server.drawing_add_shape.fn(
            cid, "draw1", "rect", x1=0.0, y1=0.0, x2=100.0, y2=50.0
        )

        assert result["success"] is True
        shapes = widget.state.properties["shapes"]
        assert shapes[0]["filled"] is False

    def test_circle_filled_stored(self, cid):
        """drawing_add_shape with shape_type='circle' and filled=True stores filled flag."""
        widget = _make_canvas_with_drawing(cid)

        result = server.drawing_add_shape.fn(
            cid, "draw1", "circle", cx=50.0, cy=50.0, radius=20.0, filled=True
        )

        assert result["success"] is True
        assert widget.state.properties["shapes"][0]["filled"] is True

    def test_fill_unsupported_on_line_returns_error(self, cid):
        """drawing_add_shape returns error when filled=True on a line shape."""
        _make_canvas_with_drawing(cid)

        result = server.drawing_add_shape.fn(
            cid, "draw1", "line", x1=0.0, y1=0.0, x2=100.0, y2=100.0, filled=True
        )

        assert result["success"] is False
        assert "does not support fill" in result["error"]

    def test_fill_unsupported_on_arrow_returns_error(self, cid):
        """drawing_add_shape returns error when filled=True on an arrow shape."""
        _make_canvas_with_drawing(cid)

        result = server.drawing_add_shape.fn(
            cid, "draw1", "arrow", x1=0.0, y1=0.0, x2=100.0, y2=100.0, filled=True
        )

        assert result["success"] is False
        assert "does not support fill" in result["error"]

    def test_unknown_shape_type_returns_error(self, cid):
        """drawing_add_shape returns error for an unknown shape type."""
        _make_canvas_with_drawing(cid)

        result = server.drawing_add_shape.fn(cid, "draw1", "pentagon")

        assert result["success"] is False
        assert "Unknown shape type" in result["error"]

    def test_import_filled_ellipse_succeeds(self, cid):
        """drawing_import_strokes accepts a filled ellipse shape dict."""
        widget = _make_canvas_with_drawing(cid)

        shape = {
            "type": "ellipse",
            "cx": 50.0,
            "cy": 50.0,
            "rx": 30.0,
            "ry": 20.0,
            "color": [0.0, 1.0, 0.0, 1.0],
            "thickness": 2.0,
            "filled": True,
        }
        result = server.drawing_import_strokes.fn(cid, "draw1", shapes=[shape])

        assert result["success"] is True
        assert widget.state.properties["shapes"][0]["filled"] is True

    def test_import_filled_rect_succeeds(self, cid):
        """drawing_import_strokes accepts a filled rect shape dict."""
        widget = _make_canvas_with_drawing(cid)

        shape = {
            "type": "rect",
            "x1": 0.0,
            "y1": 0.0,
            "x2": 100.0,
            "y2": 60.0,
            "color": [1.0, 0.0, 0.0, 1.0],
            "thickness": 1.5,
            "filled": True,
        }
        result = server.drawing_import_strokes.fn(cid, "draw1", shapes=[shape])

        assert result["success"] is True
        assert widget.state.properties["shapes"][0]["filled"] is True

    def test_import_filled_line_returns_error(self, cid):
        """drawing_import_strokes rejects a filled line shape dict."""
        _make_canvas_with_drawing(cid)

        shape = {
            "type": "line",
            "x1": 0.0,
            "y1": 0.0,
            "x2": 50.0,
            "y2": 50.0,
            "color": [1.0, 1.0, 1.0, 1.0],
            "thickness": 2.0,
            "filled": True,
        }
        result = server.drawing_import_strokes.fn(cid, "draw1", shapes=[shape])

        assert result["success"] is False
        assert "does not support fill" in result["error"]

    def test_import_unknown_shape_type_returns_error(self, cid):
        """drawing_import_strokes rejects a shape dict with an unknown type."""
        _make_canvas_with_drawing(cid)

        shape = {"type": "hexagon", "color": [1.0, 1.0, 1.0, 1.0]}
        result = server.drawing_import_strokes.fn(cid, "draw1", shapes=[shape])

        assert result["success"] is False
        assert "Unknown shape type" in result["error"]

    def test_rect_and_ellipse_in_fill_supported_types(self):
        """FILL_SUPPORTED_TYPES includes both 'rect' and 'ellipse'."""
        from champi_imgui.widgets.drawing import FILL_SUPPORTED_TYPES

        assert "rect" in FILL_SUPPORTED_TYPES
        assert "ellipse" in FILL_SUPPORTED_TYPES


class TestShapeValidation:
    @pytest.mark.parametrize("shape_type", ["unknown_blob", "triangle", "", "RECT"])
    def test_add_shape_unknown_type_returns_error(self, cid, shape_type):
        """drawing_add_shape returns a structured error for unknown shape types."""
        _make_canvas_with_drawing(cid)

        result = server.drawing_add_shape.fn(cid, "draw1", shape_type)

        assert result["success"] is False
        assert f"Unknown shape type: '{shape_type}'" in result["error"]

    def test_add_shape_filled_defaults_to_false(self, cid):
        """drawing_add_shape stores filled=False on the shape when not specified."""
        widget = _make_canvas_with_drawing(cid)

        server.drawing_add_shape.fn(cid, "draw1", "rect")

        assert widget.state.properties["shapes"][0]["filled"] is False

    @pytest.mark.parametrize("shape_type", ["unknown_blob", "triangle", "", "RECT"])
    def test_import_strokes_unknown_shape_type_returns_error(self, cid, shape_type):
        """drawing_import_strokes returns a structured error for unknown shape types."""
        _make_canvas_with_drawing(cid)
        shape = {
            "type": shape_type,
            "color": [0.0, 0.5, 1.0, 1.0],
            "thickness": 2.0,
            "x1": 0.0,
            "y1": 0.0,
            "x2": 10.0,
            "y2": 10.0,
        }

        result = server.drawing_import_strokes.fn(cid, "draw1", shapes=[shape])

        assert result["success"] is False
        assert f"Unknown shape type: '{shape_type}'" in result["error"]

    def test_import_strokes_valid_shapes_succeed(self, cid):
        """drawing_import_strokes accepts a list of valid shapes without errors."""
        widget = _make_canvas_with_drawing(cid)
        shapes = [
            {
                "type": "rect",
                "color": [1.0, 0.0, 0.0, 1.0],
                "thickness": 2.0,
                "x1": 0.0,
                "y1": 0.0,
                "x2": 50.0,
                "y2": 50.0,
            },
            {
                "type": "circle",
                "color": [0.0, 1.0, 0.0, 1.0],
                "thickness": 1.0,
                "cx": 25.0,
                "cy": 25.0,
                "radius": 10.0,
            },
            {
                "type": "arrow",
                "color": [0.0, 0.0, 1.0, 1.0],
                "thickness": 2.0,
                "x1": 0.0,
                "y1": 0.0,
                "x2": 100.0,
                "y2": 100.0,
            },
            {
                "type": "line",
                "color": [1.0, 1.0, 0.0, 1.0],
                "thickness": 1.5,
                "x1": 5.0,
                "y1": 5.0,
                "x2": 80.0,
                "y2": 80.0,
            },
        ]

        result = server.drawing_import_strokes.fn(cid, "draw1", shapes=shapes)

        assert result["success"] is True
        assert len(widget.state.properties["shapes"]) == 2

    def test_import_strokes_no_shapes_arg_is_safe(self, cid):
        """drawing_import_strokes with shapes=None does not raise."""
        _make_canvas_with_drawing(cid)

        result = server.drawing_import_strokes.fn(cid, "draw1", shapes=None)

        assert result["success"] is True
