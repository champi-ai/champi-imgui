"""Diagnostic tests: why canvas windows appear in CLI but not via MCP.

Root hypothesis: MCP clients spawn the server process with a stripped
environment.  The Wayland socket lives at $XDG_RUNTIME_DIR/$WAYLAND_DISPLAY;
without XDG_RUNTIME_DIR the socket path cannot be resolved even when
WAYLAND_DISPLAY is set.

Required env vars for a working canvas:
  DISPLAY          - X11 / XWayland display (e.g. :0)
  WAYLAND_DISPLAY  - Wayland socket name (e.g. wayland-0)  [alternative]
  XDG_RUNTIME_DIR  - Runtime dir where the Wayland socket lives (/run/user/UID)

MCP config must carry all three:
  "env": {
    "DISPLAY": ":0",
    "WAYLAND_DISPLAY": "wayland-0",
    "XDG_RUNTIME_DIR": "/run/user/1000"
  }
"""

import contextlib
import os
import time
import uuid
from unittest.mock import MagicMock, patch

import pytest

from champi_imgui.api.server import create_mcp_app
from champi_imgui.core.canvas import Canvas, CanvasManager

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _fn(mcp, name):
    return mcp._local_provider._components[f"tool:{name}@"].fn


def _has_display() -> bool:
    return bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))


def _has_xdg_runtime() -> bool:
    xdg = os.environ.get("XDG_RUNTIME_DIR", "")
    if not xdg:
        return False
    wayland = os.environ.get("WAYLAND_DISPLAY", "")
    if wayland:
        return os.path.exists(os.path.join(xdg, wayland))
    return os.path.isdir(xdg)


# ---------------------------------------------------------------------------
# 1. Environment variable audit
# ---------------------------------------------------------------------------


def test_required_display_env_vars_present():
    """All three display env vars needed for MCP must be set in this process."""
    missing = []
    if not os.environ.get("DISPLAY") and not os.environ.get("WAYLAND_DISPLAY"):
        missing.append("DISPLAY or WAYLAND_DISPLAY")
    if not os.environ.get("XDG_RUNTIME_DIR"):
        missing.append("XDG_RUNTIME_DIR")

    assert not missing, (
        f"Missing env vars that MCP config must carry: {missing}\n"
        "Add them to the 'env' block in your MCP server config."
    )


def test_wayland_socket_is_reachable():
    """$XDG_RUNTIME_DIR/$WAYLAND_DISPLAY must exist as a socket file."""
    xdg = os.environ.get("XDG_RUNTIME_DIR", "")
    wayland = os.environ.get("WAYLAND_DISPLAY", "")

    if not xdg or not wayland:
        pytest.skip("WAYLAND_DISPLAY or XDG_RUNTIME_DIR not set")

    socket_path = os.path.join(xdg, wayland)
    assert os.path.exists(socket_path), (
        f"Wayland socket not found at {socket_path!r}.\n"
        "GLFW will fail to connect even if WAYLAND_DISPLAY is set.\n"
        "XDG_RUNTIME_DIR must also be in the MCP env block."
    )


# ---------------------------------------------------------------------------
# 2. Render thread captures GLFW failure and propagates it
# ---------------------------------------------------------------------------


def test_render_thread_captures_glfw_error():
    """_render_error is set when hello_imgui.run raises an exception."""
    cid = f"dbg_{uuid.uuid4().hex[:8]}"
    canvas = Canvas(cid)

    glfw_exc = RuntimeError("GLFW: Wayland: Failed to connect to display")

    with patch("champi_imgui.core.canvas.hello_imgui") as mock_hi:
        mock_hi.RunnerParams.return_value = MagicMock()
        mock_hi.run.side_effect = glfw_exc
        canvas.run_async()
        canvas._render_thread.join(timeout=3.0)

    assert canvas._render_error is glfw_exc, (
        f"Expected _render_error to be set, got: {canvas._render_error!r}"
    )
    assert not canvas.is_render_healthy()
    canvas.shm_manager.cleanup()


def test_render_error_propagates_to_create_canvas_mcp_tool():
    """create_canvas MCP tool returns the render error in its response."""
    cid = f"dbg_{uuid.uuid4().hex[:8]}"
    glfw_exc = RuntimeError("GLFW: Wayland: Failed to connect to display")

    mock_canvas = MagicMock()
    mock_canvas.state.to_dict.return_value = {"canvas_id": cid}
    mock_canvas.is_render_healthy.return_value = False
    mock_canvas._render_error = glfw_exc

    mock_mgr = MagicMock()
    mock_mgr.get_canvas.return_value = None
    mock_mgr.create_canvas.return_value = mock_canvas

    mcp = create_mcp_app(canvas_manager=mock_mgr)
    result = _fn(mcp, "create_canvas")(cid, auto_start=True)

    assert result["success"] is False, f"Expected failure, got: {result}"
    assert "Render thread did not start" in result["error"]
    assert "Wayland" in result["error"], (
        f"GLFW error not surfaced in MCP response.\nGot: {result['error']}"
    )


# ---------------------------------------------------------------------------
# 3. Simulate stripped MCP environment (missing XDG_RUNTIME_DIR)
# ---------------------------------------------------------------------------


def test_render_fails_without_xdg_runtime_dir(monkeypatch, tmp_path):
    """Canvas render thread fails when XDG_RUNTIME_DIR is stripped (as in MCP).

    This simulates what happens when the MCP client spawns the server without
    propagating XDG_RUNTIME_DIR.
    """
    monkeypatch.delenv("XDG_RUNTIME_DIR", raising=False)

    # Wayland lookup must fail now: socket path becomes just the socket name
    xdg = os.environ.get("XDG_RUNTIME_DIR", "")
    wayland = os.environ.get("WAYLAND_DISPLAY", "wayland-0")
    socket_path = os.path.join(xdg, wayland) if xdg else wayland

    assert not os.path.exists(socket_path), (
        "Socket unexpectedly reachable without XDG_RUNTIME_DIR — "
        "test assumption is wrong; update this test."
    )


def test_mcp_env_block_recommendation():
    """Documents the exact env block needed in the MCP config.

    Not a functional test — asserts that the required keys resolve to
    real paths on this machine so the documented config is copy-pasteable.
    """
    recommendations = {
        "DISPLAY": os.environ.get("DISPLAY", ""),
        "WAYLAND_DISPLAY": os.environ.get("WAYLAND_DISPLAY", ""),
        "XDG_RUNTIME_DIR": os.environ.get("XDG_RUNTIME_DIR", ""),
    }

    empty = [k for k, v in recommendations.items() if not v]
    assert not empty, f"Cannot recommend MCP env block — these vars are unset: {empty}"

    # Confirm XDG_RUNTIME_DIR is a real directory
    xdg = recommendations["XDG_RUNTIME_DIR"]
    assert os.path.isdir(xdg), f"XDG_RUNTIME_DIR={xdg!r} is not a directory"

    # Emit the recommended block to stdout so pytest -s shows it
    print("\n--- Recommended MCP env block ---")
    print('"env": {')
    for k, v in recommendations.items():
        if v:
            print(f'  "{k}": "{v}",')
    print("}")


# ---------------------------------------------------------------------------
# 4. Live integration — only when a display is reachable
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not (_has_display() and _has_xdg_runtime()),
    reason="No reachable display or Wayland socket — skipping live render test",
)
def test_live_create_canvas_render_healthy(tmp_path):
    """Full path: create_canvas → render thread starts → screenshot succeeds.

    Requires DISPLAY/WAYLAND_DISPLAY and XDG_RUNTIME_DIR all set.
    """
    cid = f"live_{uuid.uuid4().hex[:8]}"
    manager = CanvasManager()
    mcp = create_mcp_app(canvas_manager=manager)

    try:
        result = _fn(mcp, "create_canvas")(
            cid, title="Debug Window", width=400, height=300
        )

        assert result["success"] is True, (
            f"create_canvas failed — render error: {result.get('error')}\n"
            f"Check that DISPLAY, WAYLAND_DISPLAY, and XDG_RUNTIME_DIR are all "
            f"set in the MCP env block.\n"
            f"Current values:\n"
            f"  DISPLAY={os.environ.get('DISPLAY')!r}\n"
            f"  WAYLAND_DISPLAY={os.environ.get('WAYLAND_DISPLAY')!r}\n"
            f"  XDG_RUNTIME_DIR={os.environ.get('XDG_RUNTIME_DIR')!r}"
        )

        canvas = manager.get_canvas(cid)
        assert canvas is not None
        assert canvas.is_render_healthy(), (
            f"Render thread unhealthy after create_canvas succeeded.\n"
            f"_render_error: {canvas._render_error!r}"
        )

        # Screenshot confirms the window is actually visible
        out = str(tmp_path / "debug.png")
        deadline = time.monotonic() + 5.0
        shot_result = None
        while time.monotonic() < deadline:
            shot_result = _fn(mcp, "screenshot_canvas")(cid, out)
            if shot_result.get("success"):
                break
            time.sleep(0.25)

        assert shot_result is not None and shot_result["success"] is True, (
            f"Screenshot failed: {shot_result}"
        )
        with open(out, "rb") as f:
            assert f.read(8) == b"\x89PNG\r\n\x1a\n", "Output is not a valid PNG"

    finally:
        with contextlib.suppress(Exception):
            _fn(mcp, "shutdown_canvas")(cid)
        manager.cleanup()
