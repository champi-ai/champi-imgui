"""CLI entry point for champi-imgui MCP server."""

import atexit
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
