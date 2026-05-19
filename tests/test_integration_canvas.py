"""Integration test: create_canvas + screenshot_canvas within 5s.

Skipped automatically when no display is available (headless CI without Xvfb).
Both tests share a single canvas to avoid hello_imgui re-init limitations.
"""

import os
import time
import uuid

import pytest


def _has_display() -> bool:
    return bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))


pytestmark = pytest.mark.skipif(
    not _has_display(),
    reason="No display available — skipping live render integration test",
)

_CANVAS_ID = f"integ_{uuid.uuid4().hex[:8]}"


@pytest.fixture(scope="module")
def live_canvas():
    """Create one canvas for the whole module, shut it down at the end."""
    import champi_imgui.server.main as server

    result = server.create_canvas.fn(
        canvas_id=_CANVAS_ID, title="Integration Test", width=640, height=480
    )
    assert result["success"] is True, f"create_canvas failed: {result.get('error')}"
    canvas = server.canvas_manager.get_canvas(_CANVAS_ID)
    yield canvas
    server.shutdown_canvas.fn(_CANVAS_ID)


def test_create_canvas_render_thread_healthy(live_canvas):
    """Render thread must be healthy after create_canvas returns."""
    assert live_canvas.is_render_healthy(), "Render thread is not healthy"


def test_create_canvas_screenshot_within_5s(live_canvas, tmp_path):
    """End-to-end: take screenshot of running canvas, assert valid PNG within 5s."""
    import champi_imgui.server.main as server

    out_path = str(tmp_path / "screenshot.png")
    deadline = time.monotonic() + 5.0
    screenshot_result = None

    while time.monotonic() < deadline:
        screenshot_result = server.screenshot_canvas.fn(
            canvas_id=_CANVAS_ID, filepath=out_path
        )
        if screenshot_result.get("success"):
            break
        time.sleep(0.25)

    assert screenshot_result is not None
    assert screenshot_result["success"] is True, (
        f"screenshot_canvas failed: {screenshot_result.get('error')}"
    )

    with open(out_path, "rb") as f:
        header = f.read(8)
    assert header == b"\x89PNG\r\n\x1a\n", "Output file is not a valid PNG"
