"""Canvas management with IPC-based rendering.

Canvas runs in a separate thread, processing commands via shared memory
from the MCP server.

Note: Screenshot capture uses GDK (PyGObject) as primary path and xwd/ImageMagick
as fallback. Wayland-native (non-XWayland) is out of scope.
"""

import subprocess
import threading
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

        # Thread control
        self._running = False
        self._render_thread: threading.Thread | None = None

        # X11 window ID, populated after the render thread initialises the window
        self._window_id: int | None = None

        # Screenshot request: set by request_screenshot(), consumed in render thread
        self._screenshot_request: _ScreenshotRequest | None = None

        # Text-measurement request: set by request_measure_text(), consumed in render thread
        self._measure_text_request: _MeasureTextRequest | None = None

        # Create shared memory regions (Canvas is the creator)
        self.shm_manager.create_regions()
        logger.info(f"Canvas '{canvas_id}' initialized with shared memory")

    def get_window_id(self) -> int | None:
        """Return the X11 window ID for this canvas, or None if unavailable.

        The value is populated after the render thread initialises the GLFW
        window.  It will be None on Wayland-native sessions or in headless
        environments.

        Returns:
            X11 window ID as an integer, or None.
        """
        return self._window_id

    def run_async(self) -> None:
        """Start canvas in background thread (non-blocking).

        Window appears immediately and begins processing commands.
        """
        if self._running:
            logger.warning(f"Canvas '{self.state.canvas_id}' already running")
            return

        self._running = True
        self._render_thread = threading.Thread(
            target=self._render_loop, daemon=True, name=f"Canvas-{self.state.canvas_id}"
        )
        self._render_thread.start()
        logger.info(f"Canvas '{self.state.canvas_id}' started in background thread")

    def stop(self) -> None:
        """Stop canvas rendering and cleanup."""
        if not self._running:
            return

        self._running = False
        if self._render_thread is not None:
            self._render_thread.join(timeout=2.0)
            logger.info(f"Canvas '{self.state.canvas_id}' stopped")

        # Cleanup shared memory
        self.shm_manager.cleanup()

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

    def _render_loop(self) -> None:
        """Main render loop (runs in background thread).

        Event-driven: polls for commands and renders UI accordingly.
        """
        # Configure HelloImGui runner params
        runner_params = hello_imgui.RunnerParams()
        runner_params.app_window_params.window_title = self.state.title
        runner_params.app_window_params.window_geometry.size = self.state.size

        # FPS idling configuration (event-driven, not continuous)
        runner_params.fps_idling.enable_idling = True
        runner_params.fps_idling.fps_idle = 10  # Low FPS when idle

        # ImPlot context — must be created after ImGui init on the render thread
        from imgui_bundle import implot

        _implot_ctx: object = None

        def _post_init() -> None:
            nonlocal _implot_ctx
            _implot_ctx = implot.create_context()
            try:
                from imgui_bundle import glfw_utils

                glfw_window = glfw_utils.glfw_window_hello_imgui()
                import glfw

                self._window_id = glfw.get_x11_window(glfw_window)
            except Exception as e:
                logger.debug(f"Could not obtain X11 window id: {e}")

        def _before_exit() -> None:
            if _implot_ctx is not None:
                implot.destroy_context(_implot_ctx)
            self._on_exit()

        # Callbacks
        runner_params.callbacks.post_init = _post_init
        runner_params.callbacks.show_gui = self._render_frame
        runner_params.callbacks.before_exit = _before_exit

        # Run ImGui app (blocking until window closed)
        try:
            hello_imgui.run(runner_params)
        except Exception as e:
            logger.error(f"Error in render loop for '{self.state.canvas_id}': {e}")
        finally:
            self._running = False

    def _render_frame(self) -> None:
        """Render a single frame (called by ImGui loop).

        Processes commands from shared memory and renders UI.
        """
        # Process pending commands
        self._process_commands()

        # Render canvas content
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
            win_id = self._window_id
            if win_id is None:
                req["result"] = {
                    "success": False,
                    "error": (
                        "No X11 window ID available — "
                        "Wayland-native sessions are not supported"
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
                    "error": "Screenshot failed: GDK and xwd fallback both unavailable",
                }
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            req["result"] = {"success": False, "error": str(e)}
        finally:
            req["done"].set()

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
                elif command_data.command_type == CommandType.UPDATE_STATE:
                    self._handle_update_state(command_data.data)
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

    def _handle_update_state(self, data: dict[str, Any]) -> None:
        """Handle UPDATE_STATE command."""
        canvas_id = data.get("canvas_id")
        if canvas_id != self.state.canvas_id:
            logger.warning(
                f"Update command for wrong canvas: {canvas_id} (expected {self.state.canvas_id})"
            )
            return

        # Update state
        if "title" in data:
            self.state.title = data["title"]
        if "width" in data and "height" in data:
            self.state.size = (data["width"], data["height"])

        logger.info(f"Updated state for canvas '{canvas_id}'")

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
    """Manages multiple Canvas instances.

    Provides centralized access to all canvases and ensures proper cleanup.
    """

    def __init__(self):
        """Initialize canvas manager."""
        self.canvases: dict[str, Canvas] = {}
        logger.info("CanvasManager initialized")

    def create_canvas(
        self, canvas_id: str, auto_start: bool = True, **kwargs: Any
    ) -> Canvas:
        """Create a new canvas.

        Args:
            canvas_id: Unique identifier for canvas
            auto_start: Whether to automatically start rendering
            **kwargs: Canvas state parameters

        Returns:
            Created Canvas instance

        Raises:
            ValueError: If canvas with same ID already exists
        """
        if canvas_id in self.canvases:
            msg = f"Canvas '{canvas_id}' already exists"
            raise ValueError(msg)

        canvas = Canvas(canvas_id, **kwargs)
        self.canvases[canvas_id] = canvas

        if auto_start:
            canvas.run_async()

        logger.info(f"Created canvas '{canvas_id}' (auto_start={auto_start})")
        return canvas

    def get_canvas(self, canvas_id: str) -> Canvas | None:
        """Get canvas by ID.

        Args:
            canvas_id: Canvas identifier

        Returns:
            Canvas instance or None if not found
        """
        return self.canvases.get(canvas_id)

    def list_canvases(self) -> list[str]:
        """List all canvas IDs.

        Returns:
            List of canvas IDs
        """
        return list(self.canvases.keys())

    def ensure_canvas_running(self, canvas_id: str) -> bool:
        """Ensure canvas is running.

        Args:
            canvas_id: Canvas identifier

        Returns:
            True if canvas is running, False if not found
        """
        canvas = self.get_canvas(canvas_id)
        if canvas is None:
            return False

        if not canvas._running:
            canvas.run_async()

        return True

    def cleanup(self) -> None:
        """Stop all canvases and cleanup resources."""
        logger.info("Cleaning up all canvases...")
        for canvas_id, canvas in self.canvases.items():
            try:
                canvas.stop()
            except Exception as e:
                logger.error(f"Error stopping canvas '{canvas_id}': {e}")

        self.canvases.clear()
        logger.info("All canvases cleaned up")
