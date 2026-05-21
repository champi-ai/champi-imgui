"""Unit tests for create_canvas health-polling (issue #129).

Tests the 2s render-thread wait added to the create_canvas MCP tool.
All tests use mocks — no display required.
"""

import contextlib
from unittest.mock import MagicMock

import pytest

import champi_imgui.server.main as server
from champi_imgui.core.canvas import CanvasManager


@pytest.fixture(autouse=True)
def fresh_canvas_manager(monkeypatch):
    manager = CanvasManager()
    original = server.canvas_manager
    server.canvas_manager = manager
    yield manager
    for canvas in list(manager.canvases.values()):
        with contextlib.suppress(Exception):
            canvas.shm_manager.cleanup()
    server.canvas_manager = original


def test_create_canvas_already_exists(fresh_canvas_manager):
    """Returns error when canvas_id already registered."""
    mock_canvas = MagicMock()
    fresh_canvas_manager.canvases["dup"] = mock_canvas

    result = server.create_canvas.fn("dup")
    assert result["success"] is False
    assert "already exists" in result["error"]


def test_create_canvas_auto_start_false_skips_poll(monkeypatch):
    """auto_start=False returns success without any health polling."""
    mock_canvas = MagicMock()
    mock_canvas.state.to_dict.return_value = {"canvas_id": "c1"}

    mock_mgr = MagicMock()
    mock_mgr.get_canvas.return_value = None
    mock_mgr.create_canvas.return_value = mock_canvas
    monkeypatch.setattr(server, "canvas_manager", mock_mgr)

    result = server.create_canvas.fn("c1", auto_start=False)
    assert result["success"] is True
    mock_canvas.is_render_healthy.assert_not_called()


def test_create_canvas_healthy_on_first_poll(monkeypatch):
    """Returns success when render thread is healthy immediately."""
    mock_canvas = MagicMock()
    mock_canvas.state.to_dict.return_value = {"canvas_id": "c2"}
    mock_canvas.is_render_healthy.return_value = True

    mock_mgr = MagicMock()
    mock_mgr.get_canvas.return_value = None
    mock_mgr.create_canvas.return_value = mock_canvas
    monkeypatch.setattr(server, "canvas_manager", mock_mgr)

    result = server.create_canvas.fn("c2", auto_start=True)
    assert result["success"] is True
    assert result["data"]["canvas_id"] == "c2"


def test_create_canvas_timeout_returns_error(monkeypatch):
    """Returns error when render thread never becomes healthy within 2s."""
    mock_canvas = MagicMock()
    mock_canvas.is_render_healthy.return_value = False
    mock_canvas._render_error = RuntimeError("GL init failed")

    mock_mgr = MagicMock()
    mock_mgr.get_canvas.return_value = None
    mock_mgr.create_canvas.return_value = mock_canvas
    monkeypatch.setattr(server, "canvas_manager", mock_mgr)

    # Speed up the test: make monotonic advance past deadline immediately
    import time as _time

    call_count = {"n": 0}
    original_monotonic = _time.monotonic
    start = original_monotonic()

    def fast_monotonic():
        call_count["n"] += 1
        # First call returns start (sets deadline), subsequent calls skip past it
        if call_count["n"] <= 1:
            return start
        return start + 3.0

    monkeypatch.setattr(server.time, "monotonic", fast_monotonic)
    monkeypatch.setattr(server.time, "sleep", lambda _: None)

    result = server.create_canvas.fn("c3", auto_start=True)
    assert result["success"] is False
    assert "Render thread did not start" in result["error"]
    assert "GL init failed" in result["error"]
