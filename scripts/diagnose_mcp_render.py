#!/usr/bin/env python3
"""Render diagnostics script.

Launches the champi-imgui canvas manager in-process, creates a canvas,
waits for the render thread to start, and reports environment variables,
thread health, and any stored render errors.

Usage:
    uv run python scripts/diagnose_mcp_render.py

Exit codes:
    0 - Canvas rendered successfully (thread alive, no errors)
    1 - Canvas failed to render (thread dead or error stored)
    2 - Environment is headless / no display available (expected in CI)
"""

import contextlib
import os
import sys
import time

# ---------------------------------------------------------------------------
# Environment report
# ---------------------------------------------------------------------------

DISPLAY_VARS = [
    "DISPLAY",
    "WAYLAND_DISPLAY",
    "XDG_SESSION_TYPE",
    "LIBGL_ALWAYS_SOFTWARE",
    "XAUTHORITY",
]


def _report_env() -> None:
    print("\n=== Display Environment ===")
    for var in DISPLAY_VARS:
        val = os.environ.get(var)
        status = val if val else "(not set)"
        print(f"  {var}: {status}")


def _has_display() -> bool:
    return bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))


# ---------------------------------------------------------------------------
# Canvas health check
# ---------------------------------------------------------------------------

def _check_canvas_health(canvas: object, wait_seconds: float = 3.0) -> dict:
    """Wait for the render thread and report health."""
    result: dict = {
        "thread_alive": False,
        "render_error": None,
        "running": False,
        "window_id": None,
    }

    deadline = time.monotonic() + wait_seconds
    while time.monotonic() < deadline:
        thread = getattr(canvas, "_render_thread", None)
        if thread is not None and thread.is_alive():
            result["thread_alive"] = True
            break
        time.sleep(0.1)

    result["running"] = getattr(canvas, "_running", False)
    result["render_error"] = getattr(canvas, "_render_error", None)
    result["window_id"] = getattr(canvas, "_window_id", None)
    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    _report_env()

    if not _has_display():
        print("\n[SKIP] No DISPLAY or WAYLAND_DISPLAY found — headless environment.")
        print("       Set DISPLAY=:0 or run under Xvfb to test rendering.")
        return 2

    print("\n=== Creating canvas in-process ===")

    try:
        from champi_imgui.core.canvas import CanvasManager
    except ImportError as e:
        print(f"[ERROR] Failed to import champi_imgui: {e}")
        return 1

    mgr = CanvasManager()
    canvas_id = "diagnose_render"

    try:
        canvas = mgr.create_canvas(
            canvas_id, title="Render Diagnostics", size=(640, 480), auto_start=True
        )
        print(f"  Canvas '{canvas_id}' created. Waiting up to 3s for render thread...")
    except Exception as e:
        print(f"[ERROR] create_canvas raised: {e}")
        return 1

    health = _check_canvas_health(canvas, wait_seconds=3.0)

    print("\n=== Render Thread Health ===")
    print(f"  running:      {health['running']}")
    print(f"  thread_alive: {health['thread_alive']}")
    print(f"  window_id:    {health['window_id']}")
    print(f"  render_error: {health['render_error']}")

    # Cleanup
    with contextlib.suppress(Exception):
        mgr.cleanup()

    if not health["thread_alive"]:
        print("\n[FAIL] Render thread is not alive after 3 seconds.")
        if health["render_error"]:
            print(f"       Stored error: {health['render_error']}")
        else:
            print("       No stored error — likely a display initialisation failure.")
            print("       Check DISPLAY env var and ensure X11/Wayland is accessible.")
        return 1

    if health["render_error"]:
        print(f"\n[FAIL] Render thread crashed: {health['render_error']}")
        return 1

    print("\n[OK] Canvas render thread is alive and healthy.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
