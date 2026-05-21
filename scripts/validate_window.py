"""Manual validation: create a canvas window with widgets and take a screenshot.

Run with:
    uv run python scripts/validate_window.py
"""

import sys
import time
from pathlib import Path

from champi_imgui.core.canvas import Canvas, CanvasManager
from champi_imgui.widgets.basic import ButtonWidget, TextWidget
from champi_imgui.widgets.container import WindowWidget

SCREENSHOT_PATH = "/tmp/champi_validation.png"


def main() -> int:
    manager = CanvasManager()

    print("Creating canvas...")
    canvas = manager.create_canvas("val", title="Validation Window", size=(600, 400))
    manager.ensure_canvas_running("val")

    # Give the render thread time to initialise
    time.sleep(1.0)

    print("Adding widgets...")
    canvas.add_widget(TextWidget("lbl1", text="champi-imgui window validation"))
    canvas.add_widget(ButtonWidget("btn1", label="OK"))
    canvas.add_widget(WindowWidget("win1", title="Child Window", closable=False))

    # Another frame to let widgets render
    time.sleep(0.5)

    print(f"Requesting screenshot → {SCREENSHOT_PATH}")
    try:
        result = canvas.request_screenshot(SCREENSHOT_PATH, timeout=8.0)
    except TimeoutError:
        print("FAIL: screenshot timed out — render thread may not be running")
        manager.cleanup()
        return 1

    if result.get("success") is False:
        print(f"FAIL: screenshot error — {result.get('error')}")
        manager.cleanup()
        return 1

    path = Path(result.get("path", SCREENSHOT_PATH))
    if not path.exists() or path.stat().st_size == 0:
        print(f"FAIL: screenshot file missing or empty at {path}")
        manager.cleanup()
        return 1

    size_kb = path.stat().st_size // 1024
    print(f"PASS: screenshot saved → {path} ({size_kb} KB)")
    manager.cleanup()
    return 0


if __name__ == "__main__":
    sys.exit(main())
