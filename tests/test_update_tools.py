"""Integration tests for surgical update MCP tools.

Tests call tool functions directly against a real CanvasManager with
auto_start=False (no ImGui render thread required). Widget state
mutations are verified without an active ImGui context.
"""

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


def _make_stroke(
    points: list | None = None,
    color: tuple = (1.0, 0.0, 0.0, 1.0),
    brush_size: float = 5.0,
) -> dict:
    """Build a minimal stroke dict matching the DrawingWidget stroke model."""
    return {
        "points": points or [(0.0, 0.0), (10.0, 10.0)],
        "author": "llm",
        "timestamp": 1000.0,
        "tool": "brush",
        "color": color,
        "brush_size": brush_size,
        "brush_style": "solid",
    }


# ---------------------------------------------------------------------------
# update_stroke
# ---------------------------------------------------------------------------


class TestUpdateStroke:
    def test_update_stroke_color(self, cid):
        """update_stroke changes only the color; other fields are untouched."""
        widget = _make_canvas_with_drawing(cid)
        stroke = _make_stroke(color=(1.0, 0.0, 0.0, 1.0), brush_size=5.0)
        widget.state.properties["strokes"] = [stroke]

        result = server.update_stroke.fn(cid, "draw1", 0, color=[0.0, 1.0, 0.0, 1.0])

        assert result["success"] is True
        updated = widget.state.properties["strokes"][0]
        assert updated["color"] == (0.0, 1.0, 0.0, 1.0)
        assert updated["brush_size"] == 5.0

    def test_update_stroke_brush_size(self, cid):
        """update_stroke changes only brush_size; other fields are untouched."""
        widget = _make_canvas_with_drawing(cid)
        stroke = _make_stroke(color=(1.0, 0.0, 0.0, 1.0), brush_size=5.0)
        widget.state.properties["strokes"] = [stroke]

        result = server.update_stroke.fn(cid, "draw1", 0, brush_size=12.5)

        assert result["success"] is True
        updated = widget.state.properties["strokes"][0]
        assert updated["brush_size"] == 12.5
        assert updated["color"] == (1.0, 0.0, 0.0, 1.0)

    def test_update_stroke_points(self, cid):
        """update_stroke replaces the point list entirely."""
        widget = _make_canvas_with_drawing(cid)
        stroke = _make_stroke(points=[(0.0, 0.0), (5.0, 5.0)])
        widget.state.properties["strokes"] = [stroke]

        new_points = [[10.0, 20.0], [30.0, 40.0], [50.0, 60.0]]
        result = server.update_stroke.fn(cid, "draw1", 0, points=new_points)

        assert result["success"] is True
        assert widget.state.properties["strokes"][0]["points"] == new_points

    def test_update_stroke_out_of_bounds(self, cid):
        """update_stroke returns a structured error when index >= stroke count."""
        widget = _make_canvas_with_drawing(cid)
        widget.state.properties["strokes"] = [_make_stroke()]

        result = server.update_stroke.fn(cid, "draw1", 5, color=[0.0, 1.0, 0.0, 1.0])

        assert result["success"] is False
        assert "5" in result["error"]
        assert "out of range" in result["error"]
        assert "1 strokes" in result["error"]

    def test_update_stroke_negative_index(self, cid):
        """update_stroke returns a validation error for negative index."""
        widget = _make_canvas_with_drawing(cid)
        widget.state.properties["strokes"] = [_make_stroke()]

        result = server.update_stroke.fn(cid, "draw1", -1, color=[0.0, 1.0, 0.0, 1.0])

        assert result["success"] is False
        assert "non-negative" in result["error"]

    def test_update_stroke_no_op(self, cid):
        """update_stroke with all None params returns success without modifying state."""
        widget = _make_canvas_with_drawing(cid)
        stroke = _make_stroke(color=(1.0, 0.0, 0.0, 1.0), brush_size=5.0)
        widget.state.properties["strokes"] = [stroke]

        result = server.update_stroke.fn(cid, "draw1", 0)

        assert result["success"] is True
        updated = widget.state.properties["strokes"][0]
        assert updated["color"] == (1.0, 0.0, 0.0, 1.0)
        assert updated["brush_size"] == 5.0

    def test_update_stroke_canvas_not_found(self):
        """update_stroke returns error when the canvas does not exist."""
        result = server.update_stroke.fn("missing_canvas", "draw1", 0, brush_size=3.0)

        assert result["success"] is False
        assert "not found" in result["error"]

    def test_update_stroke_widget_not_found(self, cid):
        """update_stroke returns error when the widget does not exist."""
        server.create_canvas.fn(cid, auto_start=False)

        result = server.update_stroke.fn(cid, "nonexistent", 0, brush_size=3.0)

        assert result["success"] is False
        assert "not found" in result["error"]

    def test_update_stroke_only_affects_target_index(self, cid):
        """update_stroke does not modify strokes at other indices."""
        widget = _make_canvas_with_drawing(cid)
        stroke_a = _make_stroke(color=(1.0, 0.0, 0.0, 1.0))
        stroke_b = _make_stroke(color=(0.0, 0.0, 1.0, 1.0))
        widget.state.properties["strokes"] = [stroke_a, stroke_b]

        result = server.update_stroke.fn(cid, "draw1", 0, color=[0.0, 1.0, 0.0, 1.0])

        assert result["success"] is True
        assert widget.state.properties["strokes"][0]["color"] == (0.0, 1.0, 0.0, 1.0)
        assert widget.state.properties["strokes"][1]["color"] == (0.0, 0.0, 1.0, 1.0)
