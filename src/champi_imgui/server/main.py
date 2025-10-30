"""FastMCP server for champi-imgui.

Provides MCP tools for creating and managing Canvas windows through
shared memory IPC.
"""

from typing import Any

from fastmcp import FastMCP
from loguru import logger

from champi_imgui.core.canvas import CanvasManager
from champi_imgui.ipc.command_types import CommandType
from champi_imgui.ipc.shared_memory_manager import SharedMemoryManager

# Global canvas manager (single instance for all MCP tool calls)
canvas_manager = CanvasManager()

# FastMCP server instance
mcp = FastMCP("champi-imgui")


@mcp.tool()
def create_canvas(
    canvas_id: str,
    title: str = "Canvas",
    width: int = 800,
    height: int = 600,
    auto_start: bool = True,
) -> dict[str, Any]:
    """Create a new canvas window.

    The canvas window will appear immediately and run in a background thread.
    Commands can be sent to the canvas via other MCP tools.

    Args:
        canvas_id: Unique identifier for the canvas
        title: Window title
        width: Window width in pixels
        height: Window height in pixels
        auto_start: Whether to automatically start rendering (default: True)

    Returns:
        Success status and canvas state data
    """
    try:
        # Check if canvas already exists
        existing = canvas_manager.get_canvas(canvas_id)
        if existing is not None:
            return {
                "success": False,
                "error": f"Canvas '{canvas_id}' already exists",
            }

        # Create canvas (window appears immediately if auto_start=True)
        canvas = canvas_manager.create_canvas(
            canvas_id=canvas_id,
            title=title,
            size=(width, height),
            auto_start=auto_start,
        )

        logger.info(f"Created canvas '{canvas_id}' via MCP tool")

        return {
            "success": True,
            "data": canvas.state.to_dict(),
        }

    except Exception as e:
        logger.error(f"Error creating canvas '{canvas_id}': {e}")
        return {
            "success": False,
            "error": str(e),
        }


@mcp.tool()
def get_canvas_state(canvas_id: str) -> dict[str, Any]:
    """Get the current state of a canvas.

    Args:
        canvas_id: Canvas identifier

    Returns:
        Success status and canvas state data
    """
    try:
        canvas = canvas_manager.get_canvas(canvas_id)
        if canvas is None:
            return {
                "success": False,
                "error": f"Canvas '{canvas_id}' not found",
            }

        return {
            "success": True,
            "data": canvas.state.to_dict(),
        }

    except Exception as e:
        logger.error(f"Error getting canvas state for '{canvas_id}': {e}")
        return {
            "success": False,
            "error": str(e),
        }


@mcp.tool()
def clear_canvas(canvas_id: str) -> dict[str, Any]:
    """Clear all widgets from a canvas.

    Sends a CLEAR_CANVAS command via shared memory to the canvas render thread.
    The command is processed asynchronously (fire-and-forget).

    Args:
        canvas_id: Canvas identifier

    Returns:
        Success status
    """
    try:
        canvas = canvas_manager.get_canvas(canvas_id)
        if canvas is None:
            return {
                "success": False,
                "error": f"Canvas '{canvas_id}' not found",
            }

        # Ensure canvas is running
        if not canvas._running:
            canvas.run_async()

        # Send command via shared memory (MCP server attaches to Canvas's memory)
        shm_manager = SharedMemoryManager(name_prefix=f"canvas_{canvas_id}")
        try:
            shm_manager.attach_regions()

            # Write command (fire-and-forget)
            seq_num = shm_manager.write_command(
                CommandType.CLEAR_CANVAS, canvas_id=canvas_id
            )

            logger.info(f"Sent CLEAR_CANVAS command to '{canvas_id}' (seq={seq_num})")

            return {
                "success": True,
                "data": {
                    "canvas_id": canvas_id,
                    "command": "CLEAR_CANVAS",
                    "seq_num": seq_num,
                },
            }

        finally:
            # Clean up shared memory handle (Canvas owns the memory)
            shm_manager.cleanup()

    except Exception as e:
        logger.error(f"Error clearing canvas '{canvas_id}': {e}")
        return {
            "success": False,
            "error": str(e),
        }


@mcp.tool()
def list_canvases() -> dict[str, Any]:
    """List all active canvas IDs.

    Returns:
        Success status and list of canvas IDs
    """
    try:
        canvas_ids = canvas_manager.list_canvases()

        return {
            "success": True,
            "data": {
                "canvas_ids": canvas_ids,
                "count": len(canvas_ids),
            },
        }

    except Exception as e:
        logger.error(f"Error listing canvases: {e}")
        return {
            "success": False,
            "error": str(e),
        }


@mcp.tool()
def update_canvas_state(
    canvas_id: str,
    title: str | None = None,
    width: int | None = None,
    height: int | None = None,
) -> dict[str, Any]:
    """Update canvas state (title, size).

    Sends an UPDATE_STATE command via shared memory to the canvas render thread.

    Args:
        canvas_id: Canvas identifier
        title: New window title (optional)
        width: New window width in pixels (optional)
        height: New window height in pixels (optional)

    Returns:
        Success status
    """
    try:
        canvas = canvas_manager.get_canvas(canvas_id)
        if canvas is None:
            return {
                "success": False,
                "error": f"Canvas '{canvas_id}' not found",
            }

        # Ensure canvas is running
        if not canvas._running:
            canvas.run_async()

        # Prepare command data
        cmd_data: dict[str, Any] = {"canvas_id": canvas_id}
        if title is not None:
            cmd_data["title"] = title
        if width is not None:
            cmd_data["width"] = width
        if height is not None:
            cmd_data["height"] = height

        # Send command via shared memory
        shm_manager = SharedMemoryManager(name_prefix=f"canvas_{canvas_id}")
        try:
            shm_manager.attach_regions()

            seq_num = shm_manager.write_command(CommandType.UPDATE_STATE, **cmd_data)

            logger.info(f"Sent UPDATE_STATE command to '{canvas_id}' (seq={seq_num})")

            return {
                "success": True,
                "data": {
                    "canvas_id": canvas_id,
                    "command": "UPDATE_STATE",
                    "seq_num": seq_num,
                    "updates": cmd_data,
                },
            }

        finally:
            shm_manager.cleanup()

    except Exception as e:
        logger.error(f"Error updating canvas state for '{canvas_id}': {e}")
        return {
            "success": False,
            "error": str(e),
        }


@mcp.tool()
def shutdown_canvas(canvas_id: str) -> dict[str, Any]:
    """Shutdown a canvas window gracefully.

    Sends a SHUTDOWN command via shared memory and removes canvas from manager.

    Args:
        canvas_id: Canvas identifier

    Returns:
        Success status
    """
    try:
        canvas = canvas_manager.get_canvas(canvas_id)
        if canvas is None:
            return {
                "success": False,
                "error": f"Canvas '{canvas_id}' not found",
            }

        # Send shutdown command via shared memory
        if canvas._running:
            shm_manager = SharedMemoryManager(name_prefix=f"canvas_{canvas_id}")
            try:
                shm_manager.attach_regions()
                seq_num = shm_manager.write_command(
                    CommandType.SHUTDOWN, canvas_id=canvas_id
                )
                logger.info(f"Sent SHUTDOWN command to '{canvas_id}' (seq={seq_num})")
            finally:
                shm_manager.cleanup()

        # Stop canvas and cleanup
        canvas.stop()

        # Remove from manager
        del canvas_manager.canvases[canvas_id]

        logger.info(f"Shutdown canvas '{canvas_id}'")

        return {
            "success": True,
            "data": {"canvas_id": canvas_id, "shutdown": True},
        }

    except Exception as e:
        logger.error(f"Error shutting down canvas '{canvas_id}': {e}")
        return {
            "success": False,
            "error": str(e),
        }
