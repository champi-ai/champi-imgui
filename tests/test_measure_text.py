"""Tests for measure_text MCP tool and Canvas.request_measure_text."""

import contextlib
import threading
import uuid
from unittest.mock import MagicMock, patch

import pytest

import champi_imgui.server.main as server
from champi_imgui.core.canvas import Canvas, CanvasManager


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


# ---------------------------------------------------------------------------
# MCP tool — measure_text
# ---------------------------------------------------------------------------


def test_measure_text_tool_exists():
    """measure_text is registered as an MCP tool."""
    assert hasattr(server.measure_text, "fn")
    assert callable(server.measure_text.fn)


def test_measure_text_canvas_not_found():
    """Returns error when canvas does not exist."""
    result = server.measure_text.fn("nonexistent", "w1", "Hello", 16)
    assert result["success"] is False
    assert "not found" in result["error"]


def test_measure_text_canvas_not_running(cid):
    """Returns error when canvas exists but is not running."""
    server.canvas_manager.create_canvas(cid, auto_start=False)
    canvas = server.canvas_manager.get_canvas(cid)
    assert canvas is not None
    canvas._running = False

    result = server.measure_text.fn(cid, "w1", "Hello", 16)
    assert result["success"] is False
    assert "not running" in result["error"]


def test_measure_text_returns_width_and_height(cid, monkeypatch):
    """Returns truncated int dimensions from request_measure_text."""
    server.canvas_manager.create_canvas(cid, auto_start=False)
    canvas = server.canvas_manager.get_canvas(cid)
    assert canvas is not None
    canvas._running = True

    monkeypatch.setattr(
        canvas,
        "request_measure_text",
        lambda text, font_size, timeout=5.0: {"width": 42, "height": 16},
    )

    result = server.measure_text.fn(cid, "w1", "Hello", 16)
    assert result["success"] is True
    assert result["data"]["width"] == 42
    assert result["data"]["height"] == 16


def test_measure_text_propagates_error(cid, monkeypatch):
    """Returns error when request_measure_text reports a failure."""
    server.canvas_manager.create_canvas(cid, auto_start=False)
    canvas = server.canvas_manager.get_canvas(cid)
    assert canvas is not None
    canvas._running = True

    monkeypatch.setattr(
        canvas,
        "request_measure_text",
        lambda text, font_size, timeout=5.0: {"error": "imgui context unavailable"},
    )

    result = server.measure_text.fn(cid, "w1", "Hello", 16)
    assert result["success"] is False
    assert "imgui context unavailable" in result["error"]


def test_measure_text_timeout(cid, monkeypatch):
    """Returns timeout error when render thread never responds."""
    server.canvas_manager.create_canvas(cid, auto_start=False)
    canvas = server.canvas_manager.get_canvas(cid)
    assert canvas is not None
    canvas._running = True

    def raise_timeout(*args, **kwargs):
        raise TimeoutError("timed out")

    monkeypatch.setattr(canvas, "request_measure_text", raise_timeout)

    result = server.measure_text.fn(cid, "w1", "Hello", 16)
    assert result["success"] is False
    assert "timed out" in result["error"].lower()


# ---------------------------------------------------------------------------
# Canvas.request_measure_text — threading contract
# ---------------------------------------------------------------------------


def test_request_measure_text_dispatches_to_render_thread(cid):
    """request_measure_text sets _measure_text_request before blocking."""
    canvas = Canvas(cid)
    canvas._running = True

    captured_req = {}

    def fake_wake():
        # Simulate the render thread handling the request immediately
        req = canvas._measure_text_request
        if req is not None:
            captured_req.update(req)
            req["result"] = {"width": 42, "height": 16}
            req["done"].set()

    canvas._wake_render = fake_wake  # type: ignore[method-assign]

    result = canvas.request_measure_text("Hello", 16, timeout=2.0)

    assert result == {"width": 42, "height": 16}
    assert captured_req["text"] == "Hello"
    assert captured_req["font_size"] == 16

    canvas.shm_manager.cleanup()


def test_request_measure_text_timeout_clears_request(cid):
    """request_measure_text clears _measure_text_request on timeout."""
    canvas = Canvas(cid)
    canvas._running = True
    canvas._wake_render = lambda: None  # type: ignore[method-assign]

    with pytest.raises(TimeoutError):
        canvas.request_measure_text("Hello", 16, timeout=0.05)

    assert canvas._measure_text_request is None

    canvas.shm_manager.cleanup()


# ---------------------------------------------------------------------------
# Canvas._handle_measure_text — render-thread handler
# ---------------------------------------------------------------------------


def test_handle_measure_text_calls_calc_text_size(cid):
    """_handle_measure_text calls imgui.calc_text_size and stores result."""
    canvas = Canvas(cid)

    done = threading.Event()
    req = {"text": "Hello", "font_size": 14, "done": done}
    canvas._measure_text_request = req  # type: ignore[assignment]

    mock_size = MagicMock()
    mock_size.x = 42.7
    mock_size.y = 16.3

    mock_font = MagicMock()
    mock_font.legacy_size = 14.0

    mock_io = MagicMock()
    mock_io.fonts.fonts = [mock_font]

    with (
        patch("champi_imgui.core.canvas.imgui.get_io", return_value=mock_io),
        patch("champi_imgui.core.canvas.imgui.push_font"),
        patch("champi_imgui.core.canvas.imgui.calc_text_size", return_value=mock_size),
        patch("champi_imgui.core.canvas.imgui.pop_font"),
    ):
        canvas._handle_measure_text()

    assert done.is_set()
    assert req["result"]["width"] == 42
    assert req["result"]["height"] == 16

    canvas.shm_manager.cleanup()


def test_handle_measure_text_no_request_is_noop(cid):
    """_handle_measure_text does nothing when no request is pending."""
    canvas = Canvas(cid)
    canvas._measure_text_request = None

    # Should not raise
    canvas._handle_measure_text()

    canvas.shm_manager.cleanup()


def test_handle_measure_text_truncates_floats(cid):
    """_handle_measure_text truncates float dimensions to int via int()."""
    canvas = Canvas(cid)

    done = threading.Event()
    req = {"text": "X", "font_size": 12, "done": done}
    canvas._measure_text_request = req  # type: ignore[assignment]

    mock_size = MagicMock()
    mock_size.x = 9.99
    mock_size.y = 13.01

    mock_io = MagicMock()
    mock_io.fonts.fonts = []

    with (
        patch("champi_imgui.core.canvas.imgui.get_io", return_value=mock_io),
        patch("champi_imgui.core.canvas.imgui.calc_text_size", return_value=mock_size),
    ):
        canvas._handle_measure_text()

    assert req["result"]["width"] == 9
    assert req["result"]["height"] == 13

    canvas.shm_manager.cleanup()
