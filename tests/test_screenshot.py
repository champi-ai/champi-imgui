"""Tests for screenshot_canvas MCP tool and Canvas.request_screenshot."""

import contextlib
import uuid

import pytest

import champi_imgui.server.main as server
from champi_imgui.core.canvas import CanvasManager


@pytest.fixture(autouse=True)
def fresh_canvas_manager(monkeypatch):
    """Swap module-level canvas_manager with a clean instance per test."""
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


def test_screenshot_canvas_missing_canvas():
    result = server.screenshot_canvas.fn("nonexistent", "/tmp/out.png")
    assert result["success"] is False
    assert "not found" in result["error"]


def test_screenshot_canvas_tool_exists():
    """screenshot_canvas is registered as an MCP tool."""
    assert hasattr(server.screenshot_canvas, "fn")
    assert callable(server.screenshot_canvas.fn)


def test_screenshot_no_opengl_import():
    """canvas.py must not import from OpenGL — we use mss instead."""
    import inspect

    from champi_imgui.core import canvas

    source = inspect.getsource(canvas)
    assert "from OpenGL" not in source
    assert "import OpenGL" not in source


def test_screenshot_canvas_timeout(cid, monkeypatch):
    """Returns timeout error when render thread never processes the request."""
    server.canvas_manager.create_canvas(cid, auto_start=False)

    def raise_timeout(*args, **kwargs):
        raise TimeoutError("timed out")

    canvas = server.canvas_manager.get_canvas(cid)
    monkeypatch.setattr(canvas, "request_screenshot", raise_timeout)

    result = server.screenshot_canvas.fn(cid, "/tmp/out.png")
    assert result["success"] is False
    assert "timed out" in result["error"].lower()
