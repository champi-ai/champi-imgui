"""Canvas management with IPC-based rendering.

All canvases share a single persistent render loop (owned by CanvasManager).
Each Canvas renders as an ImGui window inside that loop.

Note: Screenshot capture uses GDK (PyGObject) as primary path and xwd/ImageMagick
as fallback. Wayland-native (non-XWayland) is out of scope.
"""

import subprocess
import threading
from collections.abc import Callable
from typing import Any, TypedDict

from imgui_bundle import hello_imgui, imgui
from loguru import logger

from champi_imgui.core.state import CanvasState
from champi_imgui.core.widget import Widget, WidgetRegistry
from champi_imgui.ipc.command_types import CommandType
from champi_imgui.ipc.shared_memory_manager import SharedMemoryManager


class _ScreenshotRequest(TypedDict, total=False):
    """Internal screenshot request passed between threads."""

    filepath: str
    region: list[int] | None
    done: threading.Event
    result: dict[str, Any]


class _MeasureTextRequest(TypedDict, total=False):
    """Internal text-measurement request passed between threads."""

    text: str
    font_size: int
    done: threading.Event
    result: dict[str, Any]


class _CanvasInfoRequest(TypedDict, total=False):
    """Internal canvas-info request passed between threads."""

    done: threading.Event
    result: dict[str, Any]


class Canvas:
    """Canvas window with event-driven rendering.

    The canvas runs in a background thread and processes commands
    from shared memory regions. Window appears immediately when created.
    """

    def __init__(self, canvas_id: str, **kwargs: Any):
        """Initialize canvas.

        Args:
            canvas_id: Unique identifier for canvas
            **kwargs: Canvas state parameters (title, size, etc.)
        """
        self.state = CanvasState(canvas_id=canvas_id, **kwargs)
        self.shm_manager = SharedMemoryManager(name_prefix=f"canvas_{canvas_id}")
        self.widget_registry = WidgetRegistry()

        self._running = False
        self._render_error: Exception | None = None

        # Injected by CanvasManager so is_render_healthy() can probe the shared loop.
        self._loop_healthy: Callable[[], bool] = lambda: False

        # Screenshot request: set by request_screenshot(), consumed in render thread
        self._screenshot_request: _ScreenshotRequest | None = None

        # Text-measurement request: set by request_measure_text(), consumed in render thread
        self._measure_text_request: _MeasureTextRequest | None = None

        # Canvas-info request: set by request_canvas_info(), consumed in render thread
        self._canvas_info_request: _CanvasInfoRequest | None = None

        # Create shared memory regions (Canvas is the creator)
        self.shm_manager.create_regions()
        logger.info(f"Canvas '{canvas_id}' initialized with shared memory")

    def get_window_id(self) -> int | None:
        """Return None — window ID is owned by the shared CanvasManager render loop."""
        return None

    def run_async(self) -> None:
        """Mark canvas as active so the shared render loop will render it."""
        if self._running:
            logger.warning(f"Canvas '{self.state.canvas_id}' already running")
            return
        self._running = True
        logger.info(f"Canvas '{self.state.canvas_id}' activated for rendering")

    def is_render_healthy(self) -> bool:
        """Return True when the shared render loop is alive and this canvas has no error."""
        return self._running and self._loop_healthy() and self._render_error is None

    def stop(self) -> None:
        """Mark canvas inactive and release shared memory."""
        if not self._running:
            return
        self._running = False
        self.shm_manager.cleanup()
        logger.info(f"Canvas '{self.state.canvas_id}' stopped")

    def add_widget(self, widget: Widget) -> None:
        """Add a widget to the canvas registry.

        Thread-safe: may be called from any thread.

        Args:
            widget: Widget instance to add
        """
        self.widget_registry.add(widget)
        logger.debug(
            f"Added widget '{widget.widget_id}' to canvas '{self.state.canvas_id}'"
        )
        self._wake_render()

    def _wake_render(self) -> None:
        """Signal hello_imgui to render a fresh frame after external state mutation."""
        import contextlib

        with contextlib.suppress(Exception):
            hello_imgui.get_runner_params().fps_idling.time_active_after_last_event = (
                0.5
            )

    def remove_widget(self, widget_id: str) -> bool:
        """Remove a widget from the canvas registry.

        Args:
            widget_id: Identifier of the widget to remove

        Returns:
            True if removed, False if not found
        """
        removed = self.widget_registry.remove(widget_id)
        if removed:
            logger.debug(
                f"Removed widget '{widget_id}' from canvas '{self.state.canvas_id}'"
            )
        return removed

    def _render_frame(self) -> None:
        """Render a single frame — called by the shared CanvasManager render loop."""
        self._process_commands()

        imgui.set_next_window_size(
            imgui.ImVec2(*self.state.size), imgui.Cond_.first_use_ever
        )
        imgui.begin(
            self.state.title,
            flags=imgui.WindowFlags_.no_collapse,
        )

        # Render all registered widgets (skip widgets owned by a parent container)
        for widget in self.widget_registry.get_all().values():
            if widget._parent_id is not None:
                continue
            try:
                widget.render()
            except Exception as e:
                import traceback

                logger.error(
                    f"Error rendering widget '{widget.widget_id}': {e}\n{traceback.format_exc()}"
                )

        imgui.end()
        self._handle_screenshot()
        self._handle_measure_text()
        self._handle_canvas_info()

    def _handle_screenshot(self) -> None:
        """Capture the canvas window and write a PNG file if requested.

        Tries GDK (PyGObject) first, falls back to xwd + ImageMagick convert.
        Must be called from the render thread after all ImGui draw calls so the
        window contents are fully rendered.
        """
        req = self._screenshot_request
        if req is None:
            return
        self._screenshot_request = None
        filepath = req["filepath"]
        try:
            # OpenGL reads directly from the GPU framebuffer — no X11 needed.
            # Always try it first so Wayland/headless environments are covered.
            if self._capture_opengl(filepath):
                req["result"] = {"path": filepath}
                return

            # Fall back to X11-based methods — not available (shared window).
            win_id = None
            if win_id is None:
                req["result"] = {
                    "success": False,
                    "error": (
                        "Screenshot failed: OpenGL unavailable and no X11 window ID "
                        "(Wayland-native sessions are not supported)"
                    ),
                }
                return

            captured = self._capture_gdk(win_id, filepath)
            if not captured:
                captured = self._capture_xwd(win_id, filepath)

            if captured:
                req["result"] = {"path": filepath}
            else:
                req["result"] = {
                    "success": False,
                    "error": "Screenshot failed: all capture methods unavailable",
                }
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            req["result"] = {"success": False, "error": str(e)}
        finally:
            req["done"].set()

    def _capture_opengl(self, filepath: str) -> bool:
        """Capture the window by reading the OpenGL framebuffer directly.

        Does not use X11 — works on XWayland and when the compositor blocks XGetImage.
        Reads from the back buffer (contains the previous fully-rendered frame).

        Args:
            filepath: Destination PNG path.

        Returns:
            True on success, False if OpenGL or Pillow are unavailable.
        """
        try:
            from OpenGL import GL
            from PIL import Image

            w, h = self.state.size
            data = GL.glReadPixels(0, 0, w, h, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE)
            img = Image.frombytes("RGBA", (w, h), data)
            img = img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
            img.save(filepath, "PNG")
            return True
        except Exception as e:
            logger.debug(f"OpenGL capture failed, will try GDK: {e}")
            return False

    def _capture_gdk(self, win_id: int, filepath: str) -> bool:
        """Capture window using GDK (PyGObject).

        Args:
            win_id: X11 window ID.
            filepath: Destination PNG path.

        Returns:
            True on success, False if GDK is unavailable or capture failed.
        """
        try:
            import gi

            gi.require_version("Gdk", "3.0")
            from gi.repository import Gdk, GdkX11

            display = GdkX11.X11Display.get_default()
            if display is None:
                return False
            gdk_window = GdkX11.X11Window.foreign_new_for_display(display, win_id)
            if gdk_window is None:
                return False
            width = gdk_window.get_width()
            height = gdk_window.get_height()
            pixbuf = Gdk.pixbuf_get_from_window(gdk_window, 0, 0, width, height)
            if pixbuf is None:
                return False
            pixbuf.savev(filepath, "png", [], [])
            return True
        except Exception as e:
            logger.debug(f"GDK capture failed, will try fallback: {e}")
            return False

    def _capture_xwd(self, win_id: int, filepath: str) -> bool:
        """Capture window using xwd + ImageMagick convert as fallback.

        Args:
            win_id: X11 window ID.
            filepath: Destination PNG path.

        Returns:
            True on success, False if xwd/convert are unavailable or failed.
        """
        import contextlib
        import os
        import tempfile

        xwd_fd, xwd_path = tempfile.mkstemp(suffix=".xwd")
        os.close(xwd_fd)
        try:
            subprocess.run(
                ["xwd", "-id", hex(win_id), "-out", xwd_path, "-silent"],
                check=True,
                timeout=10,
            )
            subprocess.run(
                ["convert", xwd_path, filepath],
                check=True,
                timeout=10,
            )
            return True
        except FileNotFoundError as e:
            logger.debug(f"xwd/convert not available: {e}")
            return False
        except subprocess.CalledProcessError as e:
            logger.debug(f"xwd/convert failed: {e}")
            return False
        finally:
            with contextlib.suppress(OSError):
                os.unlink(xwd_path)

    def request_screenshot(
        self,
        filepath: str,
        region: list[int] | None = None,
        timeout: float = 5.0,
    ) -> dict[str, Any]:
        """Capture the canvas window as a PNG file (thread-safe).

        Schedules a screenshot on the render thread and blocks until it
        completes or the timeout expires.

        Args:
            filepath: Destination path for the PNG file.
            region: Optional ``[x, y, width, height]`` crop in pixels (GDK path
                ignores this; the parameter is reserved for future use).
            timeout: Seconds to wait for the render thread to respond.

        Returns:
            ``{"path": filepath}`` on success, or
            ``{"success": False, "error": <message>}`` on failure.

        Raises:
            TimeoutError: If the render thread does not respond within *timeout*.
        """
        done = threading.Event()
        req: _ScreenshotRequest = {"filepath": filepath, "region": region, "done": done}
        self._screenshot_request = req
        self._wake_render()

        if not done.wait(timeout=timeout):
            self._screenshot_request = None
            raise TimeoutError(
                f"Screenshot of canvas '{self.state.canvas_id}' timed out after {timeout}s"
            )

        return req.get("result", {"error": "No result produced"})

    def _handle_measure_text(self) -> None:
        """Measure text on the render thread if a request is pending.

        Must be called from the render thread after ImGui frame setup so that
        the font atlas is active.
        """
        req = self._measure_text_request
        if req is None:
            return
        self._measure_text_request = None
        try:
            text = req["text"]
            font_size = req["font_size"]

            io = imgui.get_io()
            fonts = io.fonts.fonts
            best_font = None
            if fonts:
                best_font = min(fonts, key=lambda f: abs(f.legacy_size - font_size))

            if best_font is not None:
                imgui.push_font(best_font, float(font_size))
                size = imgui.calc_text_size(text)
                imgui.pop_font()
            else:
                size = imgui.calc_text_size(text)

            req["result"] = {"width": int(size.x), "height": int(size.y)}
        except Exception as e:
            logger.error(f"measure_text failed: {e}")
            req["result"] = {"error": str(e)}
        finally:
            req["done"].set()

    def request_measure_text(
        self,
        text: str,
        font_size: int,
        timeout: float = 5.0,
    ) -> dict[str, Any]:
        """Measure rendered text dimensions on the render thread (thread-safe).

        Args:
            text: The string to measure.
            font_size: Desired font size; the closest loaded font is used.
            timeout: Seconds to wait for the render thread to respond.

        Returns:
            ``{"width": int, "height": int}`` or ``{"error": <message>}`` on failure.

        Raises:
            TimeoutError: If the render thread does not respond within *timeout*.
        """
        done = threading.Event()
        req: _MeasureTextRequest = {"text": text, "font_size": font_size, "done": done}
        self._measure_text_request = req
        self._wake_render()

        if not done.wait(timeout=timeout):
            self._measure_text_request = None
            raise TimeoutError(
                f"measure_text on canvas '{self.state.canvas_id}' timed out after {timeout}s"
            )

        return req.get("result", {"error": "No result produced"})

    def _handle_canvas_info(self) -> None:
        """Collect canvas rendering info on the render thread if a request is pending."""
        req = self._canvas_info_request
        if req is None:
            return
        self._canvas_info_request = None
        try:
            io = imgui.get_io()
            pixel_scale = io.display_framebuffer_scale.x

            from champi_imgui.widgets.drawing import DrawingWidget

            offset_x, offset_y = 0.0, 0.0
            for widget in self.widget_registry.get_all().values():
                if isinstance(widget, DrawingWidget):
                    offset_x, offset_y = widget.canvas_screen_offset
                    break

            req["result"] = {
                "screen_offset_x": offset_x,
                "screen_offset_y": offset_y,
                "pixel_scale": pixel_scale,
            }
        except Exception as e:
            logger.error(f"canvas_info fetch failed: {e}")
            req["result"] = {"error": str(e)}
        finally:
            req["done"].set()

    def request_canvas_info(self, timeout: float = 5.0) -> dict[str, Any]:
        """Fetch live canvas rendering info from the render thread (thread-safe).

        Returns:
            Dict with ``screen_offset_x``, ``screen_offset_y``, ``pixel_scale``,
            or ``{"error": <message>}`` on failure.

        Raises:
            TimeoutError: If the render thread does not respond within *timeout*.
        """
        done = threading.Event()
        req: _CanvasInfoRequest = {"done": done}
        self._canvas_info_request = req
        self._wake_render()

        if not done.wait(timeout=timeout):
            self._canvas_info_request = None
            raise TimeoutError(
                f"canvas_info on canvas '{self.state.canvas_id}' timed out after {timeout}s"
            )

        return req.get("result", {"error": "No result produced"})

    def _process_commands(self) -> None:
        """Process all pending commands from shared memory."""
        while self._running:
            # Non-blocking read
            command_data = self.shm_manager.read_command(timeout=0.0)
            if command_data is None:
                break

            logger.debug(
                f"Processing command: {command_data.command_type.name} (seq={command_data.seq_num})"
            )

            # Handle command
            try:
                if command_data.command_type == CommandType.CLEAR_CANVAS:
                    self._handle_clear_canvas(command_data.data)
                elif command_data.command_type == CommandType.UPDATE_TITLE:
                    self._handle_update_title(command_data.data)
                elif command_data.command_type == CommandType.UPDATE_SIZE:
                    self._handle_update_size(command_data.data)
                elif command_data.command_type == CommandType.SHUTDOWN:
                    self._handle_shutdown(command_data.data)
                elif command_data.command_type == CommandType.REMOVE_WIDGET:
                    self._handle_remove_widget(command_data.data)
                else:
                    logger.warning(
                        f"Unknown command type: {command_data.command_type.name}"
                    )

                # Send acknowledgment
                self.shm_manager.write_ack(command_data.seq_num)
            except Exception as e:
                logger.error(
                    f"Error processing command {command_data.command_type.name}: {e}"
                )

    def _handle_clear_canvas(self, data: dict[str, Any]) -> None:
        """Handle CLEAR_CANVAS command."""
        canvas_id = data.get("canvas_id")
        if canvas_id != self.state.canvas_id:
            logger.warning(
                f"Clear command for wrong canvas: {canvas_id} (expected {self.state.canvas_id})"
            )
            return

        self.widget_registry.clear()
        logger.info(f"Clearing canvas '{canvas_id}'")

    def _handle_update_title(self, data: dict[str, Any]) -> None:
        """Handle UPDATE_TITLE command."""
        canvas_id = data.get("canvas_id")
        if canvas_id != self.state.canvas_id:
            logger.warning(
                f"Update title command for wrong canvas: {canvas_id} (expected {self.state.canvas_id})"
            )
            return

        self.state.title = data["title"]
        logger.info(f"Updated title for canvas '{canvas_id}'")

    def _handle_update_size(self, data: dict[str, Any]) -> None:
        """Handle UPDATE_SIZE command."""
        canvas_id = data.get("canvas_id")
        if canvas_id != self.state.canvas_id:
            logger.warning(
                f"Update size command for wrong canvas: {canvas_id} (expected {self.state.canvas_id})"
            )
            return

        self.state.size = (data["width"], data["height"])
        logger.info(f"Updated size for canvas '{canvas_id}'")

    def _handle_remove_widget(self, data: dict[str, Any]) -> None:
        """Handle REMOVE_WIDGET command."""
        canvas_id = data.get("canvas_id")
        if canvas_id != self.state.canvas_id:
            logger.warning(
                f"Remove widget command for wrong canvas: {canvas_id} (expected {self.state.canvas_id})"
            )
            return

        widget_id = data.get("widget_id", "")
        self.widget_registry.remove(widget_id)
        logger.info(f"Removed widget '{widget_id}' from canvas '{canvas_id}'")

    def _handle_shutdown(self, data: dict[str, Any]) -> None:
        """Handle SHUTDOWN command."""
        canvas_id = data.get("canvas_id")
        if canvas_id != self.state.canvas_id:
            logger.warning(
                f"Shutdown command for wrong canvas: {canvas_id} (expected {self.state.canvas_id})"
            )
            return

        logger.info(f"Shutting down canvas '{canvas_id}'")
        self._running = False

    def _on_exit(self) -> None:
        """Cleanup on window close."""
        logger.info(f"Canvas '{self.state.canvas_id}' window closed")
        self._running = False


class CanvasManager:
    """Manages multiple Canvas instances sharing a single persistent render loop.

    hello_imgui.run() is a process-level singleton — calling it more than once
    crashes with "Already initialized a platform backend!".  CanvasManager owns
    exactly one render thread; every Canvas is an ImGui window inside that loop.
    """

    def __init__(self):
        self.canvases: dict[str, Canvas] = {}
        self._render_thread: threading.Thread | None = None
        self._loop_running = False
        self._implot_ctx: object = None
        self._window_id: int | None = None
        logger.info("CanvasManager initialized")

    # ------------------------------------------------------------------
    # Shared render loop
    # ------------------------------------------------------------------

    def is_loop_healthy(self) -> bool:
        return (
            self._loop_running
            and self._render_thread is not None
            and self._render_thread.is_alive()
        )

    def _start_render_loop(self) -> None:
        if self.is_loop_healthy():
            return
        self._loop_running = False
        self._render_thread = threading.Thread(
            target=self._render_loop, daemon=True, name="CanvasRenderThread"
        )
        self._render_thread.start()
        logger.info("Shared canvas render loop started")

    def _render_loop(self) -> None:
        from imgui_bundle import implot

        runner_params = hello_imgui.RunnerParams()
        runner_params.app_window_params.window_title = "champi-imgui"
        runner_params.app_window_params.window_geometry.size = (1600, 900)
        runner_params.fps_idling.enable_idling = True
        runner_params.fps_idling.fps_idle = 10

        def _post_init() -> None:
            self._loop_running = True
            self._implot_ctx = implot.create_context()
            try:
                import glfw
                from imgui_bundle import glfw_utils

                glfw_window = glfw_utils.glfw_window_hello_imgui()
                self._window_id = glfw.get_x11_window(glfw_window)
            except Exception as e:
                logger.debug(f"Could not obtain X11 window id: {e}")

        def _before_exit() -> None:
            if self._implot_ctx is not None:
                implot.destroy_context(self._implot_ctx)
                self._implot_ctx = None
            for canvas in self.canvases.values():
                canvas._running = False
            self._loop_running = False

        runner_params.callbacks.post_init = _post_init
        runner_params.callbacks.show_gui = self._render_all_canvases
        runner_params.callbacks.before_exit = _before_exit

        try:
            hello_imgui.run(runner_params)
        except Exception as e:
            logger.error(f"Shared render loop crashed: {e}")
            for canvas in self.canvases.values():
                if canvas._render_error is None:
                    canvas._render_error = e
        finally:
            self._loop_running = False

    def _render_all_canvases(self) -> None:
        for canvas in list(self.canvases.values()):
            if canvas._running:
                canvas._render_frame()

    # ------------------------------------------------------------------
    # Canvas lifecycle
    # ------------------------------------------------------------------

    def create_canvas(
        self, canvas_id: str, auto_start: bool = True, **kwargs: Any
    ) -> Canvas:
        if canvas_id in self.canvases:
            raise ValueError(f"Canvas '{canvas_id}' already exists")

        canvas = Canvas(canvas_id, **kwargs)
        canvas._loop_healthy = self.is_loop_healthy
        self.canvases[canvas_id] = canvas

        if auto_start:
            canvas._running = True
            self._start_render_loop()

        logger.info(f"Created canvas '{canvas_id}' (auto_start={auto_start})")
        return canvas

    def get_canvas(self, canvas_id: str) -> Canvas | None:
        return self.canvases.get(canvas_id)

    def list_canvases(self) -> list[str]:
        return list(self.canvases.keys())

    def ensure_canvas_running(self, canvas_id: str) -> bool:
        canvas = self.get_canvas(canvas_id)
        if canvas is None:
            return False
        if not canvas._running:
            canvas._running = True
        if not self.is_loop_healthy():
            self._start_render_loop()
        return True

    def cleanup(self) -> None:
        logger.info("Cleaning up all canvases...")
        for canvas_id, canvas in list(self.canvases.items()):
            try:
                canvas.stop()
            except Exception as e:
                logger.error(f"Error stopping canvas '{canvas_id}': {e}")
        self.canvases.clear()
        logger.info("All canvases cleaned up")
