"""Tests for screenshot_canvas MCP tool and Canvas.request_screenshot."""

import contextlib
import subprocess
import threading
import uuid
from unittest.mock import patch

import pytest

import champi_imgui.api.server as _srv_mod
from champi_imgui.api.server import create_mcp_app
from champi_imgui.core.canvas import Canvas, CanvasManager

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


def test_screenshot_canvas_missing_canvas():
    result = server.screenshot_canvas.fn("nonexistent", "/tmp/out.png")
    assert result["success"] is False
    assert "not found" in result["error"]


def test_screenshot_canvas_tool_exists():
    """screenshot_canvas is registered as an MCP tool."""
    assert hasattr(server.screenshot_canvas, "fn")
    assert callable(server.screenshot_canvas.fn)


def test_screenshot_opengl_import_is_lazy():
    """canvas.py imports OpenGL only inside _capture_opengl, not at module level."""
    import inspect

    from champi_imgui.core import canvas as canvas_mod

    source = inspect.getsource(canvas_mod)
    # Lazy import is acceptable; it must not be a top-level import
    lines = source.splitlines()
    top_level = [
        ln
        for ln in lines
        if (ln.startswith("import OpenGL") or ln.startswith("from OpenGL"))
    ]
    assert top_level == [], f"Top-level OpenGL import found: {top_level}"


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


def test_handle_screenshot_no_window_id(cid):
    """_handle_screenshot returns error when OpenGL fails and window_id is None."""
    canvas = Canvas(cid)
    canvas._window_id = None

    done = threading.Event()
    req = {"filepath": "/tmp/out.png", "region": None, "done": done}
    canvas._screenshot_request = req
    with patch.object(canvas, "_capture_opengl", return_value=False):
        canvas._handle_screenshot()

    assert done.is_set()
    assert req["result"]["success"] is False
    assert "Wayland" in req["result"]["error"] or "X11" in req["result"]["error"]

    canvas.shm_manager.cleanup()


def test_handle_screenshot_opengl_succeeds_without_window_id(cid, tmp_path):
    """OpenGL capture works even when win_id is None (Wayland/headless).

    This is the regression test for the bug introduced in v1.9.2 where
    _capture_opengl was placed after the win_id-is-None guard, causing
    every screenshot to fail on Wayland and headless environments.
    """
    canvas = Canvas(cid)
    canvas._window_id = None  # Simulates Wayland / no X11
    filepath = str(tmp_path / "shot.png")

    done = threading.Event()
    req = {"filepath": filepath, "region": None, "done": done}
    canvas._screenshot_request = req

    with patch.object(canvas, "_capture_opengl", return_value=True) as mock_gl:
        canvas._handle_screenshot()

    assert done.is_set()
    assert req["result"] == {"path": filepath}
    mock_gl.assert_called_once_with(filepath)  # OpenGL was attempted
    canvas.shm_manager.cleanup()


def test_capture_gdk_returns_bool(cid, tmp_path):
    """_capture_gdk returns a bool regardless of whether gi is installed."""
    canvas = Canvas(cid)
    filepath = str(tmp_path / "shot.png")

    result = canvas._capture_gdk(12345, filepath)

    assert isinstance(result, bool)

    canvas.shm_manager.cleanup()


def test_capture_gdk_gi_unavailable(cid, tmp_path):
    """_capture_gdk returns False gracefully when gi is not installed."""
    canvas = Canvas(cid)
    filepath = str(tmp_path / "shot.png")

    with patch("builtins.__import__", side_effect=ImportError("No module named 'gi'")):
        result = canvas._capture_gdk(12345, filepath)

    assert result is False
    canvas.shm_manager.cleanup()


def test_capture_xwd_tools_unavailable(cid, tmp_path):
    """_capture_xwd returns False when xwd is not on PATH."""
    canvas = Canvas(cid)
    filepath = str(tmp_path / "shot.png")

    with patch("subprocess.run", side_effect=FileNotFoundError("xwd not found")):
        result = canvas._capture_xwd(12345, filepath)

    assert result is False
    canvas.shm_manager.cleanup()


def test_capture_xwd_process_error(cid, tmp_path):
    """_capture_xwd returns False when xwd returns non-zero exit code."""
    canvas = Canvas(cid)
    filepath = str(tmp_path / "shot.png")

    with patch(
        "subprocess.run",
        side_effect=subprocess.CalledProcessError(1, "xwd"),
    ):
        result = canvas._capture_xwd(12345, filepath)

    assert result is False
    canvas.shm_manager.cleanup()


def test_handle_screenshot_gdk_fallback_to_xwd(cid, tmp_path):
    """When GDK fails, _handle_screenshot falls back to xwd path."""
    canvas = Canvas(cid)
    canvas._window_id = 99999
    filepath = str(tmp_path / "shot.png")

    done = threading.Event()
    req = {"filepath": filepath, "region": None, "done": done}
    canvas._screenshot_request = req

    with (
        patch.object(canvas, "_capture_gdk", return_value=False),
        patch.object(canvas, "_capture_xwd", return_value=True),
    ):
        canvas._handle_screenshot()

    assert done.is_set()
    assert req["result"] == {"path": filepath}
    canvas.shm_manager.cleanup()


def test_handle_screenshot_all_fail(cid, tmp_path):
    """When all capture methods fail, result contains success=False."""
    canvas = Canvas(cid)
    canvas._window_id = 99999
    filepath = str(tmp_path / "shot.png")

    done = threading.Event()
    req = {"filepath": filepath, "region": None, "done": done}
    canvas._screenshot_request = req

    with (
        patch.object(canvas, "_capture_opengl", return_value=False),
        patch.object(canvas, "_capture_gdk", return_value=False),
        patch.object(canvas, "_capture_xwd", return_value=False),
    ):
        canvas._handle_screenshot()

    assert done.is_set()
    assert req["result"]["success"] is False
    assert "unavailable" in req["result"]["error"]
    canvas.shm_manager.cleanup()


def test_handle_screenshot_gdk_success(cid, tmp_path):
    """When GDK succeeds, result is {"path": filepath}."""
    canvas = Canvas(cid)
    canvas._window_id = 11111
    filepath = str(tmp_path / "shot.png")

    done = threading.Event()
    req = {"filepath": filepath, "region": None, "done": done}
    canvas._screenshot_request = req

    with (
        patch.object(canvas, "_capture_gdk", return_value=True),
        patch.object(canvas, "_capture_xwd", return_value=False),
    ):
        canvas._handle_screenshot()

    assert done.is_set()
    assert req["result"] == {"path": filepath}
    canvas.shm_manager.cleanup()


def test_screenshot_canvas_mcp_returns_filepath(cid, monkeypatch):
    """screenshot_canvas MCP tool returns success with filepath key."""
    server.canvas_manager.create_canvas(cid, auto_start=False)
    canvas = server.canvas_manager.get_canvas(cid)
    monkeypatch.setattr(
        canvas,
        "request_screenshot",
        lambda filepath, region=None, timeout=5.0: {"path": filepath},
    )

    result = server.screenshot_canvas.fn(cid, "/tmp/out.png")
    assert result["success"] is True
    assert result["filepath"] == "/tmp/out.png"


def test_screenshot_canvas_mcp_propagates_error(cid, monkeypatch):
    """screenshot_canvas MCP tool propagates error from request_screenshot."""
    server.canvas_manager.create_canvas(cid, auto_start=False)
    canvas = server.canvas_manager.get_canvas(cid)
    monkeypatch.setattr(
        canvas,
        "request_screenshot",
        lambda filepath, region=None, timeout=5.0: {
            "success": False,
            "error": "GDK and xwd fallback both unavailable",
        },
    )

    result = server.screenshot_canvas.fn(cid, "/tmp/out.png")
    assert result["success"] is False
    assert "unavailable" in result["error"]
