"""CLI entry point for champi-imgui MCP server.

Required environment variables for canvas rendering:
  DISPLAY        - X11 display socket (e.g. :0 or :1)
  XAUTHORITY     - X11 auth cookie file (e.g. /home/user/.Xauthority)
  WAYLAND_DISPLAY - Wayland socket (alternative to DISPLAY on Wayland sessions)

When running as a systemd service, add to the [Service] section:
  Environment="DISPLAY=:0"
  Environment="XAUTHORITY=/home/YOUR_USER/.Xauthority"
Or use: PassEnvironment=DISPLAY XAUTHORITY WAYLAND_DISPLAY
"""

import atexit
import os
import signal
import sys

from loguru import logger

from champi_imgui.server.main import canvas_manager, mcp


def cleanup() -> None:
    """Cleanup handler for shutdown."""
    logger.info("Shutting down champi-imgui...")
    canvas_manager.cleanup()
    logger.info("Shutdown complete")


def signal_handler(signum: int, frame: object) -> None:
    """Handle interrupt signals gracefully."""
    logger.info(f"Received signal {signum}, shutting down...")
    cleanup()
    sys.exit(0)


def main() -> None:
    """Main entry point for champi-imgui CLI."""
    # Configure logger
    logger.remove()  # Remove default handler
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    )

    logger.info("Starting champi-imgui MCP server...")

    if not os.environ.get("DISPLAY") and not os.environ.get("WAYLAND_DISPLAY"):
        logger.warning(
            "Neither DISPLAY nor WAYLAND_DISPLAY is set — canvas windows will likely "
            "fail to render. Set DISPLAY=:0 or ensure the display server environment "
            "is propagated to this process."
        )

    # Register cleanup handlers
    atexit.register(cleanup)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Run FastMCP server (blocking)
        mcp.run()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Error running MCP server: {e}")
        raise
    finally:
        cleanup()


if __name__ == "__main__":
    main()
