"""Regression tests for DrawingWidget shape storage and stroke retrieval (#190).

Focuses on the data layer (shapes list populated, strokes retrievable) and
headless render safety.  These tests complement tests/widgets/test_drawing.py
and tests/test_drawing_shm_fixes.py without duplicating them.
"""

import time
from unittest.mock import MagicMock, patch

from champi_imgui.widgets.drawing import DrawingWidget

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_stroke(
    author: str = "test_author",
    points: list[tuple[float, float]] | None = None,
) -> dict:
    """Return a minimal well-formed stroke dict."""
    return {
        "points": points or [(0.0, 0.0), (10.0, 10.0)],
        "author": author,
        "timestamp": time.time(),
        "tool": "brush",
        "color": (1.0, 0.0, 0.0, 1.0),
        "brush_size": 5.0,
        "brush_style": "solid",
    }


# ---------------------------------------------------------------------------
# Test 1 — add_shape() populates the shapes list (#190)
# ---------------------------------------------------------------------------


def test_add_shape_populates_shapes_list():
    """add_shape('rect', ...) appends a shape dict with correct type and coords.

    Regression guard: the shapes list must be non-empty after calling add_shape
    so the render loop can replay LLM-added shapes on screen.
    """
    w = DrawingWidget("dw-190-shape-1")
    assert w.state.properties["shapes"] == [], "shapes list must start empty"

    w.add_shape("rect", x1=5.0, y1=15.0, x2=55.0, y2=65.0)

    shapes = w.state.properties["shapes"]
    assert len(shapes) == 1, "exactly one shape should be stored after add_shape()"
    shape = shapes[0]
    assert shape["type"] == "rect"
    assert shape["x1"] == 5.0
    assert shape["y1"] == 15.0
    assert shape["x2"] == 55.0
    assert shape["y2"] == 65.0


# ---------------------------------------------------------------------------
# Test 2 — strokes are stored and retrievable by author (#190)
# ---------------------------------------------------------------------------


def test_add_stroke_retrievable_by_author():
    """Strokes added to state are retrievable via get_strokes_by_author().

    Regression guard: get_strokes_by_author must filter by the 'author' field
    so callers can distinguish user strokes from LLM strokes.
    """
    w = DrawingWidget("dw-190-stroke-1")
    assert w.get_strokes_by_author("test_author") == []

    stroke = _make_stroke(author="test_author", points=[(0.0, 0.0), (50.0, 50.0)])
    w.state.properties["strokes"].append(stroke)

    result = w.get_strokes_by_author("test_author")
    assert len(result) == 1
    assert result[0]["author"] == "test_author"
    assert result[0]["points"] == [(0.0, 0.0), (50.0, 50.0)]

    # Strokes for a different author must not be returned
    assert w.get_strokes_by_author("other_author") == []


# ---------------------------------------------------------------------------
# Test 3 — render() does not raise with a mocked draw list (#190)
# ---------------------------------------------------------------------------


def test_render_does_not_raise_with_mocked_draw_list():
    """render() completes without error when imgui is replaced by mocks.

    Headless-safe: patches champi_imgui.widgets.drawing.imgui so no real ImGui
    context is needed.  Verifies that adding a shape and calling render() does
    not raise even without a display server.
    """
    w = DrawingWidget("dw-190-render-1")
    w.add_shape("rect", x1=0.0, y1=0.0, x2=100.0, y2=100.0)

    mock_pos = MagicMock()
    mock_pos.x = 0.0
    mock_pos.y = 0.0

    mock_draw_list = MagicMock()

    with patch("champi_imgui.widgets.drawing.imgui") as mock_imgui:
        mock_imgui.get_cursor_screen_pos.return_value = mock_pos
        mock_imgui.ImVec2.return_value = mock_pos
        mock_imgui.ImVec4.return_value = MagicMock()
        mock_imgui.invisible_button.return_value = None
        mock_imgui.get_item_rect_min.return_value = mock_pos
        mock_imgui.get_item_rect_max.return_value = mock_pos
        mock_imgui.get_window_draw_list.return_value = mock_draw_list
        mock_imgui.color_convert_float4_to_u32.return_value = 0xFFFFFFFF
        mock_imgui.is_item_hovered.return_value = False
        mock_imgui.is_mouse_released.return_value = False

        w.render()  # must not raise

    mock_draw_list.push_clip_rect.assert_called_once()
    mock_draw_list.pop_clip_rect.assert_called_once()
