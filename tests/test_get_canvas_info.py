"""Tests for get_canvas_info MCP tool and Canvas.request_canvas_info."""

import contextlib
import threading
import uuid
from unittest.mock import MagicMock, patch

import pytest

import champi_imgui.api.server as _srv_mod
from champi_imgui.api.server import create_mcp_app
from champi_imgui.core.canvas import Canvas, CanvasManager
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


# ---------------------------------------------------------------------------
# MCP tool — get_canvas_info
# ---------------------------------------------------------------------------


def test_get_canvas_info_tool_exists():
    """get_canvas_info is registered as an MCP tool."""
    assert hasattr(server.get_canvas_info, "fn")
    assert callable(server.get_canvas_info.fn)


def test_get_canvas_info_canvas_not_found():
    """Returns error when canvas does not exist."""
    result = server.get_canvas_info.fn("nonexistent")
    assert result["success"] is False
    assert "not found" in result["error"]


def test_get_canvas_info_canvas_not_running(cid):
    """Returns error when canvas exists but is not running."""
    server.canvas_manager.create_canvas(cid, auto_start=False)
    canvas = server.canvas_manager.get_canvas(cid)
    assert canvas is not None
    canvas._running = False

    result = server.get_canvas_info.fn(cid)
    assert result["success"] is False
    assert "not running" in result["error"]


def test_get_canvas_info_returns_all_fields(cid, monkeypatch):
    """Returns width, height, offsets, pixel_scale, window_id on success."""
    server.canvas_manager.create_canvas(cid, auto_start=False)
    canvas = server.canvas_manager.get_canvas(cid)
    assert canvas is not None
    canvas._running = True
    canvas._window_id = 0x1234ABC

    monkeypatch.setattr(
        canvas,
        "request_canvas_info",
        lambda timeout=5.0: {
            "screen_offset_x": 10.0,
            "screen_offset_y": 20.0,
            "pixel_scale": 2.0,
        },
    )

    result = server.get_canvas_info.fn(cid)
    assert result["success"] is True
    data = result["data"]
    assert "width" in data
    assert "height" in data
    assert data["screen_offset_x"] == 10.0
    assert data["screen_offset_y"] == 20.0
    assert data["pixel_scale"] == 2.0
    assert data["window_id"] == hex(0x1234ABC)


def test_get_canvas_info_window_id_none(cid, monkeypatch):
    """window_id is 'none' when X11 window ID is unavailable."""
    server.canvas_manager.create_canvas(cid, auto_start=False)
    canvas = server.canvas_manager.get_canvas(cid)
    assert canvas is not None
    canvas._running = True
    canvas._window_id = None

    monkeypatch.setattr(
        canvas,
        "request_canvas_info",
        lambda timeout=5.0: {
            "screen_offset_x": 0.0,
            "screen_offset_y": 0.0,
            "pixel_scale": 1.0,
        },
    )

    result = server.get_canvas_info.fn(cid)
    assert result["success"] is True
    assert result["data"]["window_id"] == "none"


def test_get_canvas_info_propagates_error(cid, monkeypatch):
    """Returns error when request_canvas_info reports a failure."""
    server.canvas_manager.create_canvas(cid, auto_start=False)
    canvas = server.canvas_manager.get_canvas(cid)
    assert canvas is not None
    canvas._running = True

    monkeypatch.setattr(
        canvas,
        "request_canvas_info",
        lambda timeout=5.0: {"error": "imgui context unavailable"},
    )

    result = server.get_canvas_info.fn(cid)
    assert result["success"] is False
    assert "imgui context unavailable" in result["error"]


def test_get_canvas_info_timeout(cid, monkeypatch):
    """Returns timeout error when render thread never responds."""
    server.canvas_manager.create_canvas(cid, auto_start=False)
    canvas = server.canvas_manager.get_canvas(cid)
    assert canvas is not None
    canvas._running = True

    def raise_timeout(*args, **kwargs):
        raise TimeoutError("timed out")

    monkeypatch.setattr(canvas, "request_canvas_info", raise_timeout)

    result = server.get_canvas_info.fn(cid)
    assert result["success"] is False
    assert "timed out" in result["error"].lower()


# ---------------------------------------------------------------------------
# Canvas.request_canvas_info — threading contract
# ---------------------------------------------------------------------------


def test_request_canvas_info_dispatches_to_render_thread(cid):
    """request_canvas_info sets _canvas_info_request before blocking."""
    canvas = Canvas(cid)
    canvas._running = True

    def fake_wake():
        req = canvas._canvas_info_request
        if req is not None:
            req["result"] = {
                "screen_offset_x": 5.0,
                "screen_offset_y": 10.0,
                "pixel_scale": 1.5,
            }
            req["done"].set()

    canvas._wake_render = fake_wake  # type: ignore[method-assign]

    result = canvas.request_canvas_info(timeout=2.0)

    assert result["screen_offset_x"] == 5.0
    assert result["screen_offset_y"] == 10.0
    assert result["pixel_scale"] == 1.5

    canvas.shm_manager.cleanup()


def test_request_canvas_info_timeout_clears_request(cid):
    """request_canvas_info clears _canvas_info_request on timeout."""
    canvas = Canvas(cid)
    canvas._running = True
    canvas._wake_render = lambda: None  # type: ignore[method-assign]

    with pytest.raises(TimeoutError):
        canvas.request_canvas_info(timeout=0.05)

    assert canvas._canvas_info_request is None

    canvas.shm_manager.cleanup()


# ---------------------------------------------------------------------------
# Canvas._handle_canvas_info — render-thread handler
# ---------------------------------------------------------------------------


def test_handle_canvas_info_returns_offset_and_scale(cid):
    """_handle_canvas_info reads imgui.get_io() and DrawingWidget offset."""
    canvas = Canvas(cid)

    drawing = DrawingWidget("dw1")
    drawing.canvas_screen_offset = (15.0, 25.0)
    canvas.widget_registry.add(drawing)

    done = threading.Event()
    req: dict = {"done": done}
    canvas._canvas_info_request = req  # type: ignore[assignment]

    mock_scale = MagicMock()
    mock_scale.x = 2.0
    mock_io = MagicMock()
    mock_io.display_framebuffer_scale = mock_scale

    with patch("champi_imgui.core.canvas.imgui.get_io", return_value=mock_io):
        canvas._handle_canvas_info()

    assert done.is_set()
    assert req["result"]["screen_offset_x"] == 15.0
    assert req["result"]["screen_offset_y"] == 25.0
    assert req["result"]["pixel_scale"] == 2.0

    canvas.shm_manager.cleanup()


def test_handle_canvas_info_no_drawing_widget_returns_zeros(cid):
    """_handle_canvas_info returns 0.0 offsets when no DrawingWidget is registered."""
    canvas = Canvas(cid)

    done = threading.Event()
    req: dict = {"done": done}
    canvas._canvas_info_request = req  # type: ignore[assignment]

    mock_scale = MagicMock()
    mock_scale.x = 1.0
    mock_io = MagicMock()
    mock_io.display_framebuffer_scale = mock_scale

    with patch("champi_imgui.core.canvas.imgui.get_io", return_value=mock_io):
        canvas._handle_canvas_info()

    assert done.is_set()
    assert req["result"]["screen_offset_x"] == 0.0
    assert req["result"]["screen_offset_y"] == 0.0

    canvas.shm_manager.cleanup()


def test_handle_canvas_info_no_request_is_noop(cid):
    """_handle_canvas_info does nothing when no request is pending."""
    canvas = Canvas(cid)
    canvas._canvas_info_request = None

    canvas._handle_canvas_info()

    canvas.shm_manager.cleanup()


# ---------------------------------------------------------------------------
# DrawingWidget.canvas_screen_offset
# ---------------------------------------------------------------------------


def test_drawing_widget_has_canvas_screen_offset():
    """DrawingWidget initialises canvas_screen_offset to (0.0, 0.0)."""
    widget = DrawingWidget("dw_test")
    assert widget.canvas_screen_offset == (0.0, 0.0)
