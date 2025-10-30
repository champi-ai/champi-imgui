"""Canvas management with IPC-based rendering.

Canvas runs in a separate thread, processing commands via shared memory
from the MCP server.
"""

import threading
from typing import Any

from imgui_bundle import hello_imgui, imgui
from loguru import logger

from champi_imgui.core.state import CanvasState
from champi_imgui.ipc.command_types import CommandType
from champi_imgui.ipc.shared_memory_manager import SharedMemoryManager


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

        # Thread control
        self._running = False
        self._render_thread: threading.Thread | None = None

        # Create shared memory regions (Canvas is the creator)
        self.shm_manager.create_regions()
        logger.info(f"Canvas '{canvas_id}' initialized with shared memory")

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

        # Callbacks
        runner_params.callbacks.show_gui = self._render_frame
        runner_params.callbacks.before_exit = self._on_exit

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

        # Placeholder content for Stage 5
        imgui.text(f"Canvas ID: {self.state.canvas_id}")
        imgui.text(f"Size: {self.state.size[0]} x {self.state.size[1]}")
        imgui.separator()
        imgui.text("Ready for widgets (Stage 6)")

        imgui.end()

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

        logger.info(f"Clearing canvas '{canvas_id}'")
        # Stage 6 will implement actual widget clearing

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
