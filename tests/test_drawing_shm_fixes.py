"""Regression tests for issues #181 (DrawingWidget invisible) and #182 (macOS SHM crash).

#181 — DrawingWidget renders nothing
    Root causes:
    1. push_clip_rect / pop_clip_rect missing → draw commands clipped by wrong rect
    2. drawing_add_llm_stroke missing canvas._wake_render() call

#182 — create_canvas crashes MCP server on macOS (resource_tracker)
    Root cause: SharedMemory created with create=True is tracked by Python's
    multiprocessing.resource_tracker.  On macOS the tracker fires at exit,
    killing the stdio connection.  Fix: unregister from resource_tracker
    immediately after creation so our own cleanup() controls the lifecycle.
"""

import inspect
import uuid
from unittest.mock import MagicMock, patch

import pytest

from champi_imgui.api.server import create_mcp_app
from champi_imgui.ipc.shared_memory_manager import SharedMemoryManager
from champi_imgui.widgets.drawing import DrawingWidget

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _fn(mcp, name):
    return mcp._local_provider._components[f"tool:{name}@"].fn


# ---------------------------------------------------------------------------
# #181 — push_clip_rect / pop_clip_rect present in DrawingWidget.render()
# ---------------------------------------------------------------------------


def test_drawing_render_calls_push_clip_rect():
    """DrawingWidget.render() must call draw_list.push_clip_rect before any draw."""
    source = inspect.getsource(DrawingWidget.render)
    assert "push_clip_rect" in source, (
        "DrawingWidget.render() is missing draw_list.push_clip_rect — "
        "without it, draw commands are not clipped to the canvas bounds and "
        "may be invisible inside imgui-bundle windows (issue #181)"
    )


def test_drawing_render_calls_pop_clip_rect():
    """DrawingWidget.render() must call pop_clip_rect after drawing."""
    source = inspect.getsource(DrawingWidget.render)
    assert "pop_clip_rect" in source, (
        "DrawingWidget.render() is missing draw_list.pop_clip_rect — "
        "the clip rect pushed for the canvas area must be restored (issue #181)"
    )


def test_drawing_render_push_before_pop():
    """push_clip_rect must appear before pop_clip_rect in render source."""
    source = inspect.getsource(DrawingWidget.render)
    push_pos = source.index("push_clip_rect")
    pop_pos = source.index("pop_clip_rect")
    assert push_pos < pop_pos, "push_clip_rect must precede pop_clip_rect"


def test_drawing_render_pop_before_mouse_input():
    """pop_clip_rect must appear before the mouse input handling block.

    Mouse input (is_item_hovered, is_mouse_down) must NOT be inside the
    clipped region — only drawing calls should be clipped.
    """
    source = inspect.getsource(DrawingWidget.render)
    pop_pos = source.index("pop_clip_rect")
    mouse_pos = source.index("is_item_hovered")
    assert pop_pos < mouse_pos, (
        "pop_clip_rect must come before mouse-input handling; "
        "mouse checks should not be inside the canvas clip rect"
    )


# ---------------------------------------------------------------------------
# #181 — drawing_add_llm_stroke must call _wake_render
# ---------------------------------------------------------------------------


def test_drawing_add_llm_stroke_wakes_render():
    """drawing_add_llm_stroke must call canvas._wake_render() after mutating state."""
    cid = f"c_{uuid.uuid4().hex[:8]}"
    mock_canvas = MagicMock()
    mock_canvas.widget_registry = MagicMock()

    widget = DrawingWidget("board")
    mock_canvas.widget_registry.get.return_value = widget

    mock_mgr = MagicMock()
    mock_mgr.get_canvas.return_value = mock_canvas
    mcp = create_mcp_app(canvas_manager=mock_mgr)

    result = _fn(mcp, "drawing_add_llm_stroke")(
        canvas_id=cid,
        widget_id="board",
        points=[[10, 20], [30, 40]],
        color=[1.0, 0.0, 0.0, 1.0],
    )

    assert result["success"] is True
    (
        mock_canvas._wake_render.assert_called_once(),
        (
            "drawing_add_llm_stroke must call canvas._wake_render() so the render "
            "thread processes the new stroke immediately (issue #181)"
        ),
    )


def test_drawing_add_llm_stroke_stroke_stored():
    """Stroke added by drawing_add_llm_stroke appears in widget state."""
    widget = DrawingWidget("board")
    mock_canvas = MagicMock()
    mock_canvas.widget_registry.get.return_value = widget

    mock_mgr = MagicMock()
    mock_mgr.get_canvas.return_value = mock_canvas
    mcp = create_mcp_app(canvas_manager=mock_mgr)

    _fn(mcp, "drawing_add_llm_stroke")(
        canvas_id="c1",
        widget_id="board",
        points=[[0, 0], [100, 100]],
    )

    strokes = widget.state.properties["strokes"]
    assert len(strokes) == 1
    assert strokes[0]["author"] == "llm"
    assert strokes[0]["points"] == [(0.0, 0.0), (100.0, 100.0)]


def test_drawing_add_shape_wakes_render():
    """drawing_add_shape must call canvas._wake_render() (regression guard)."""
    widget = DrawingWidget("board")
    mock_canvas = MagicMock()
    mock_canvas.widget_registry.get.return_value = widget

    mock_mgr = MagicMock()
    mock_mgr.get_canvas.return_value = mock_canvas
    mcp = create_mcp_app(canvas_manager=mock_mgr)

    result = _fn(mcp, "drawing_add_shape")(
        canvas_id="c1",
        widget_id="board",
        shape_type="circle",
        cx=100.0,
        cy=100.0,
        radius=50.0,
    )

    assert result["success"] is True
    mock_canvas._wake_render.assert_called_once()


def test_drawing_add_text_wakes_render():
    """drawing_add_text must call canvas._wake_render() (regression guard)."""
    widget = DrawingWidget("board")
    mock_canvas = MagicMock()
    mock_canvas.widget_registry.get.return_value = widget

    mock_mgr = MagicMock()
    mock_mgr.get_canvas.return_value = mock_canvas
    mcp = create_mcp_app(canvas_manager=mock_mgr)

    result = _fn(mcp, "drawing_add_text")(
        canvas_id="c1",
        widget_id="board",
        x=50.0,
        y=50.0,
        text="Hello",
    )

    assert result["success"] is True
    mock_canvas._wake_render.assert_called_once()


# ---------------------------------------------------------------------------
# #181 — _render_frame checks imgui.begin() return value
# ---------------------------------------------------------------------------


def test_render_frame_checks_begin_return():
    """_render_frame must only render widgets when imgui.begin() returns True."""
    from champi_imgui.core import canvas as canvas_mod

    source = inspect.getsource(canvas_mod.Canvas._render_frame)
    assert "expanded" in source or "imgui.begin" in source, (
        "_render_frame must capture the return value of imgui.begin()"
    )
    # The widget loop must be conditional on the begin() result
    assert "if expanded" in source or "if not expanded" in source, (
        "_render_frame must guard widget rendering on imgui.begin() return value"
    )


# ---------------------------------------------------------------------------
# #182 — SharedMemory resource_tracker unregistration on macOS
# ---------------------------------------------------------------------------


def test_shm_creator_unregisters_from_resource_tracker():
    """create_regions() must call resource_tracker.unregister() for both regions."""
    cid = f"shm_{uuid.uuid4().hex[:8]}"
    mgr = SharedMemoryManager(name_prefix=cid)

    unregistered: list[str] = []

    import champi_imgui.ipc.shared_memory_manager as shm_mod

    original = shm_mod._untrack_shm

    def capturing_untrack(shm):
        unregistered.append(shm.name)
        original(shm)

    try:
        shm_mod._untrack_shm = capturing_untrack
        mgr.create_regions()
    finally:
        shm_mod._untrack_shm = original
        mgr.cleanup()

    assert len(unregistered) == 2, (
        f"Expected 2 untrack calls (cmd + ack), got {len(unregistered)}: {unregistered}\n"
        "Both shared memory regions must be unregistered from resource_tracker "
        "so macOS does not crash the server at process exit (issue #182)"
    )
    assert any("cmd" in n for n in unregistered), "cmd region not untracked"
    assert any("ack" in n for n in unregistered), "ack region not untracked"


def test_shm_untrack_suppresses_missing_resource_tracker():
    """_untrack_shm must not raise if resource_tracker is unavailable."""
    from multiprocessing import shared_memory

    from champi_imgui.ipc.shared_memory_manager import _untrack_shm

    cid = f"shm_{uuid.uuid4().hex[:8]}"
    shm = shared_memory.SharedMemory(name=cid, create=True, size=8)
    try:
        with patch(
            "multiprocessing.resource_tracker.unregister", side_effect=Exception("boom")
        ):
            _untrack_shm(shm)  # must not raise
    finally:
        shm.close()
        shm.unlink()


def test_shm_attacher_does_not_unregister():
    """attach_regions() must NOT call _untrack_shm (only creator manages lifecycle)."""
    cid = f"shm_{uuid.uuid4().hex[:8]}"
    creator = SharedMemoryManager(name_prefix=cid)
    creator.create_regions()

    attacher = SharedMemoryManager(name_prefix=cid)
    import champi_imgui.ipc.shared_memory_manager as shm_mod

    calls: list[str] = []
    original = shm_mod._untrack_shm

    def spy(shm):
        calls.append(shm.name)
        original(shm)

    try:
        shm_mod._untrack_shm = spy
        attacher.attach_regions()
    finally:
        shm_mod._untrack_shm = original
        attacher.cmd_region.close()
        attacher.ack_region.close()
        creator.cleanup()

    assert calls == [], (
        "attach_regions() must not call _untrack_shm — only the creator "
        "should opt out of resource_tracker tracking"
    )


def test_shm_cleanup_unlinks_after_untrack():
    """After _untrack_shm, cleanup() must still unlink the regions."""
    cid = f"shm_{uuid.uuid4().hex[:8]}"
    mgr = SharedMemoryManager(name_prefix=cid)
    mgr.create_regions()

    # Manually verify the regions exist before cleanup
    from multiprocessing import shared_memory as shm_lib

    cmd_name = f"{cid}_cmd"
    ack_name = f"{cid}_ack"

    # Both should be accessible (creator side)
    assert mgr.cmd_region is not None
    assert mgr.ack_region is not None

    mgr.cleanup()

    # After cleanup, regions should be gone (unlinked)
    with pytest.raises(FileNotFoundError):
        shm_lib.SharedMemory(name=cmd_name)
    with pytest.raises(FileNotFoundError):
        shm_lib.SharedMemory(name=ack_name)
