"""Tests for update_annotation and update_shape MCP tools."""

import contextlib
import uuid

import pytest

import champi_imgui.api.server as _srv_mod
from champi_imgui.api.server import create_mcp_app
from champi_imgui.core.canvas import CanvasManager
from champi_imgui.widgets.drawing import DrawingWidget

_DEFAULT_MCP = None


class _Server:
    """Proxy that exposes MCP tools and managers from a factory instance.

    Falls back to a lazy default instance for parametrize collection.
    """

    _mcp = None

    def __getattr__(self, name: str):
        global _DEFAULT_MCP
        if hasattr(_srv_mod, name):
            return getattr(_srv_mod, name)
        mcp = type(self)._mcp
        if mcp is None:
            if _DEFAULT_MCP is None:
                _DEFAULT_MCP = create_mcp_app()
            mcp = _DEFAULT_MCP
        if hasattr(mcp, name):
            return getattr(mcp, name)
        if hasattr(mcp, f"_{name}"):
            return getattr(mcp, f"_{name}")
        tools = mcp._tool_manager._tools
        if name in tools:
            return tools[name]
        raise AttributeError(f"_Server has no attribute '{name}'")


server = _Server()


@pytest.fixture(autouse=True)
def fresh_canvas_manager(monkeypatch):
    manager = CanvasManager()
    monkeypatch.setattr(manager, "ensure_canvas_running", lambda canvas_id: True)
    _Server._mcp = create_mcp_app(canvas_manager=manager)
    yield manager
    for canvas in list(manager.canvases.values()):
        with contextlib.suppress(Exception):
            canvas.shm_manager.cleanup()
    _Server._mcp = None


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


def _make_annotation(
    x: float = 10.0,
    y: float = 20.0,
    text: str = "hello",
    color: tuple = (1.0, 1.0, 1.0, 1.0),
    font_size: float = 13.0,
) -> dict:
    """Build a minimal annotation dict matching DrawingWidget annotation model."""
    return {
        "type": "text",
        "x": x,
        "y": y,
        "text": text,
        "color": color,
        "font_size": font_size,
    }


def _make_rect_shape(
    x1: float = 0.0,
    y1: float = 0.0,
    x2: float = 100.0,
    y2: float = 80.0,
    color: tuple = (0.0, 0.5, 1.0, 1.0),
    thickness: float = 2.0,
    filled: bool = False,
) -> dict:
    """Build a minimal rect shape dict."""
    return {
        "type": "rect",
        "x1": x1,
        "y1": y1,
        "x2": x2,
        "y2": y2,
        "color": color,
        "thickness": thickness,
        "filled": filled,
    }


def _make_circle_shape(
    cx: float = 50.0,
    cy: float = 50.0,
    radius: float = 30.0,
    color: tuple = (1.0, 0.0, 0.0, 1.0),
    thickness: float = 2.0,
    filled: bool = False,
) -> dict:
    """Build a minimal circle shape dict."""
    return {
        "type": "circle",
        "cx": cx,
        "cy": cy,
        "radius": radius,
        "color": color,
        "thickness": thickness,
        "filled": filled,
    }


# ---------------------------------------------------------------------------
# update_annotation
# ---------------------------------------------------------------------------


class TestUpdateAnnotation:
    def test_tool_exists(self):
        """update_annotation is registered as an MCP tool."""
        assert hasattr(server.update_annotation, "fn")
        assert callable(server.update_annotation.fn)

    def test_update_text(self, cid):
        """update_annotation changes only the text; other fields are untouched."""
        widget = _make_canvas_with_drawing(cid)
        ann = _make_annotation(x=5.0, y=15.0, text="original", font_size=12.0)
        widget.state.properties["annotations"] = [ann]

        result = server.update_annotation.fn(cid, "draw1", 0, text="updated")

        assert result["success"] is True
        updated = widget.state.properties["annotations"][0]
        assert updated["text"] == "updated"
        assert updated["x"] == 5.0
        assert updated["y"] == 15.0
        assert updated["font_size"] == 12.0

    def test_update_position(self, cid):
        """update_annotation moves x and y independently."""
        widget = _make_canvas_with_drawing(cid)
        ann = _make_annotation(x=0.0, y=0.0)
        widget.state.properties["annotations"] = [ann]

        result = server.update_annotation.fn(cid, "draw1", 0, x=55.0, y=77.0)

        assert result["success"] is True
        updated = widget.state.properties["annotations"][0]
        assert updated["x"] == 55.0
        assert updated["y"] == 77.0

    def test_update_color(self, cid):
        """update_annotation stores color as tuple."""
        widget = _make_canvas_with_drawing(cid)
        ann = _make_annotation()
        widget.state.properties["annotations"] = [ann]

        result = server.update_annotation.fn(
            cid, "draw1", 0, color=[1.0, 0.0, 0.0, 1.0]
        )

        assert result["success"] is True
        assert widget.state.properties["annotations"][0]["color"] == (
            1.0,
            0.0,
            0.0,
            1.0,
        )

    def test_update_font_size(self, cid):
        """update_annotation changes font_size."""
        widget = _make_canvas_with_drawing(cid)
        ann = _make_annotation(font_size=13.0)
        widget.state.properties["annotations"] = [ann]

        result = server.update_annotation.fn(cid, "draw1", 0, font_size=20.0)

        assert result["success"] is True
        assert widget.state.properties["annotations"][0]["font_size"] == 20.0

    def test_out_of_bounds(self, cid):
        """update_annotation returns error when index >= annotation count."""
        widget = _make_canvas_with_drawing(cid)
        widget.state.properties["annotations"] = [_make_annotation()]

        result = server.update_annotation.fn(cid, "draw1", 5, text="x")

        assert result["success"] is False
        assert "5" in result["error"]
        assert "out of range" in result["error"]
        assert "1 annotations" in result["error"]

    def test_negative_index(self, cid):
        """update_annotation returns error for negative index."""
        widget = _make_canvas_with_drawing(cid)
        widget.state.properties["annotations"] = [_make_annotation()]

        result = server.update_annotation.fn(cid, "draw1", -1, text="x")

        assert result["success"] is False
        assert "non-negative" in result["error"]

    def test_no_op(self, cid):
        """update_annotation with all None params succeeds without modifying state."""
        widget = _make_canvas_with_drawing(cid)
        ann = _make_annotation(text="keep", x=3.0)
        widget.state.properties["annotations"] = [ann]

        result = server.update_annotation.fn(cid, "draw1", 0)

        assert result["success"] is True
        assert widget.state.properties["annotations"][0]["text"] == "keep"
        assert widget.state.properties["annotations"][0]["x"] == 3.0

    def test_canvas_not_found(self):
        """update_annotation returns error when canvas does not exist."""
        result = server.update_annotation.fn("missing", "draw1", 0, text="x")
        assert result["success"] is False
        assert "not found" in result["error"]

    def test_widget_not_found(self, cid):
        """update_annotation returns error when widget does not exist."""
        server.create_canvas.fn(cid, auto_start=False)
        result = server.update_annotation.fn(cid, "nonexistent", 0, text="x")
        assert result["success"] is False
        assert "not found" in result["error"]

    def test_only_affects_target_index(self, cid):
        """update_annotation does not modify annotations at other indices."""
        widget = _make_canvas_with_drawing(cid)
        ann_a = _make_annotation(text="a")
        ann_b = _make_annotation(text="b")
        widget.state.properties["annotations"] = [ann_a, ann_b]

        result = server.update_annotation.fn(cid, "draw1", 0, text="A_updated")

        assert result["success"] is True
        assert widget.state.properties["annotations"][0]["text"] == "A_updated"
        assert widget.state.properties["annotations"][1]["text"] == "b"


# ---------------------------------------------------------------------------
# update_shape
# ---------------------------------------------------------------------------


class TestUpdateShape:
    def test_tool_exists(self):
        """update_shape is registered as an MCP tool."""
        assert hasattr(server.update_shape, "fn")
        assert callable(server.update_shape.fn)

    def test_update_color(self, cid):
        """update_shape changes only color; other fields are untouched."""
        widget = _make_canvas_with_drawing(cid)
        shape = _make_rect_shape(color=(0.0, 0.5, 1.0, 1.0), thickness=2.0)
        widget.state.properties["shapes"] = [shape]

        result = server.update_shape.fn(cid, "draw1", 0, color=[1.0, 0.0, 0.0, 1.0])

        assert result["success"] is True
        updated = widget.state.properties["shapes"][0]
        assert updated["color"] == (1.0, 0.0, 0.0, 1.0)
        assert updated["thickness"] == 2.0

    def test_update_thickness(self, cid):
        """update_shape changes only thickness."""
        widget = _make_canvas_with_drawing(cid)
        shape = _make_rect_shape(thickness=2.0)
        widget.state.properties["shapes"] = [shape]

        result = server.update_shape.fn(cid, "draw1", 0, thickness=5.0)

        assert result["success"] is True
        assert widget.state.properties["shapes"][0]["thickness"] == 5.0

    def test_update_rect_coords(self, cid):
        """update_shape moves rect coordinates."""
        widget = _make_canvas_with_drawing(cid)
        shape = _make_rect_shape(x1=0.0, y1=0.0, x2=100.0, y2=80.0)
        widget.state.properties["shapes"] = [shape]

        result = server.update_shape.fn(
            cid, "draw1", 0, x1=10.0, y1=20.0, x2=200.0, y2=150.0
        )

        assert result["success"] is True
        s = widget.state.properties["shapes"][0]
        assert s["x1"] == 10.0
        assert s["y1"] == 20.0
        assert s["x2"] == 200.0
        assert s["y2"] == 150.0

    def test_update_circle_radius(self, cid):
        """update_shape changes circle radius."""
        widget = _make_canvas_with_drawing(cid)
        shape = _make_circle_shape(radius=30.0)
        widget.state.properties["shapes"] = [shape]

        result = server.update_shape.fn(cid, "draw1", 0, radius=60.0)

        assert result["success"] is True
        assert widget.state.properties["shapes"][0]["radius"] == 60.0

    def test_update_fill_on_supported_type(self, cid):
        """update_shape can enable fill on rect/circle/ellipse."""
        widget = _make_canvas_with_drawing(cid)
        shape = _make_rect_shape(filled=False)
        widget.state.properties["shapes"] = [shape]

        result = server.update_shape.fn(cid, "draw1", 0, filled=True)

        assert result["success"] is True
        assert widget.state.properties["shapes"][0]["filled"] is True

    def test_update_fill_on_unsupported_type_rejected(self, cid):
        """update_shape rejects filled=True for arrow/line shapes."""
        widget = _make_canvas_with_drawing(cid)
        shape = {
            "type": "arrow",
            "x1": 0.0,
            "y1": 0.0,
            "x2": 50.0,
            "y2": 50.0,
            "color": (0.0, 0.5, 1.0, 1.0),
            "thickness": 2.0,
            "filled": False,
        }
        widget.state.properties["shapes"] = [shape]

        result = server.update_shape.fn(cid, "draw1", 0, filled=True)

        assert result["success"] is False
        assert "does not support fill" in result["error"]

    def test_out_of_bounds(self, cid):
        """update_shape returns error when index >= shape count."""
        widget = _make_canvas_with_drawing(cid)
        widget.state.properties["shapes"] = [_make_rect_shape()]

        result = server.update_shape.fn(cid, "draw1", 3, thickness=5.0)

        assert result["success"] is False
        assert "3" in result["error"]
        assert "out of range" in result["error"]
        assert "1 shapes" in result["error"]

    def test_negative_index(self, cid):
        """update_shape returns error for negative index."""
        widget = _make_canvas_with_drawing(cid)
        widget.state.properties["shapes"] = [_make_rect_shape()]

        result = server.update_shape.fn(cid, "draw1", -1, thickness=5.0)

        assert result["success"] is False
        assert "non-negative" in result["error"]

    def test_no_op(self, cid):
        """update_shape with all None params succeeds without modifying state."""
        widget = _make_canvas_with_drawing(cid)
        shape = _make_rect_shape(thickness=2.0)
        widget.state.properties["shapes"] = [shape]

        result = server.update_shape.fn(cid, "draw1", 0)

        assert result["success"] is True
        assert widget.state.properties["shapes"][0]["thickness"] == 2.0

    def test_canvas_not_found(self):
        """update_shape returns error when canvas does not exist."""
        result = server.update_shape.fn("missing", "draw1", 0, thickness=2.0)
        assert result["success"] is False
        assert "not found" in result["error"]

    def test_widget_not_found(self, cid):
        """update_shape returns error when widget does not exist."""
        server.create_canvas.fn(cid, auto_start=False)
        result = server.update_shape.fn(cid, "nonexistent", 0, thickness=2.0)
        assert result["success"] is False
        assert "not found" in result["error"]

    def test_only_affects_target_index(self, cid):
        """update_shape does not modify shapes at other indices."""
        widget = _make_canvas_with_drawing(cid)
        shape_a = _make_rect_shape(thickness=1.0)
        shape_b = _make_rect_shape(thickness=3.0)
        widget.state.properties["shapes"] = [shape_a, shape_b]

        result = server.update_shape.fn(cid, "draw1", 0, thickness=9.0)

        assert result["success"] is True
        assert widget.state.properties["shapes"][0]["thickness"] == 9.0
        assert widget.state.properties["shapes"][1]["thickness"] == 3.0
