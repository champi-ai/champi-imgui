"""CLI entry point for champi-imgui.

Required environment variables for canvas rendering:
  DISPLAY        - X11 display socket (e.g. :0 or :1)
  XAUTHORITY     - X11 auth cookie file
  WAYLAND_DISPLAY - Wayland socket (alternative to DISPLAY)

When running as a systemd service add to [Service]:
  Environment="DISPLAY=:0"
  Environment="XAUTHORITY=/home/YOUR_USER/.Xauthority"
"""

import os
import sys
from typing import Any

import click
from loguru import logger


def _configure_logger() -> None:
    logger.remove()
    logger.add(
        sys.stderr,
        level="INFO",
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
    )


def _warn_display() -> None:
    if not os.environ.get("DISPLAY") and not os.environ.get("WAYLAND_DISPLAY"):
        logger.warning(
            "Neither DISPLAY nor WAYLAND_DISPLAY is set — canvas windows will likely "
            "fail to render. Set DISPLAY=:0 or ensure the display environment is "
            "propagated to this process."
        )


@click.group()
@click.version_option()
def cli() -> None:
    """Champi ImGui — MCP server for LLM-driven UI generation."""


@cli.command("serve")
def serve() -> None:
    """Start the MCP server (stdio transport for MCP clients)."""
    from champi_imgui.api.server import create_mcp_app

    _configure_logger()
    _warn_display()
    mcp = create_mcp_app()
    mcp.run()


@cli.command("demo")
@click.option("--canvas-id", default="demo", show_default=True)
@click.option("--title", default="Champi ImGui Demo", show_default=True)
@click.option("--width", default=800, show_default=True, type=int)
@click.option("--height", default=600, show_default=True, type=int)
def demo(canvas_id: str, title: str, width: int, height: int) -> None:
    """Open a standalone demo canvas window (no MCP required)."""
    import time

    from champi_imgui.core.canvas import CanvasManager

    _configure_logger()
    _warn_display()
    manager = CanvasManager()
    manager.create_canvas(canvas_id, title=title, size=(width, height), auto_start=True)
    click.echo(f"Canvas '{canvas_id}' open — Ctrl+C to exit")
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        manager.cleanup()


@cli.command("validate")
def validate() -> None:
    """Run the installation validation (creates a window and takes a screenshot)."""
    import time
    from pathlib import Path

    from champi_imgui.core.canvas import CanvasManager
    from champi_imgui.widgets.basic import ButtonWidget, TextWidget
    from champi_imgui.widgets.container import WindowWidget

    _configure_logger()
    _warn_display()
    manager = CanvasManager()

    click.echo("Creating canvas...")
    canvas = manager.create_canvas("val", title="Validation Window", size=(600, 400))
    manager.ensure_canvas_running("val")
    time.sleep(1.0)

    click.echo("Adding widgets...")
    canvas.add_widget(TextWidget("lbl1", text="champi-imgui window validation"))
    canvas.add_widget(ButtonWidget("btn1", label="OK"))
    canvas.add_widget(WindowWidget("win1", title="Child Window", closable=False))
    time.sleep(0.5)

    screenshot_path = "champi_validation.png"
    click.echo(f"Requesting screenshot → {screenshot_path}")
    try:
        result: dict[str, Any] = canvas.request_screenshot(screenshot_path, timeout=8.0)
    except TimeoutError:
        click.echo(
            "FAIL: screenshot timed out — render thread may not be running", err=True
        )
        manager.cleanup()
        sys.exit(1)

    if result.get("success") is False:
        click.echo(f"FAIL: screenshot error — {result.get('error')}", err=True)
        manager.cleanup()
        sys.exit(1)

    path = Path(result.get("path", screenshot_path))
    if not path.exists() or path.stat().st_size == 0:
        click.echo(f"FAIL: screenshot file missing or empty at {path}", err=True)
        manager.cleanup()
        sys.exit(1)

    size_kb = path.stat().st_size // 1024
    click.echo(f"PASS: screenshot saved → {path} ({size_kb} KB)")
    manager.cleanup()


@cli.group()
def ipc() -> None:
    """Shared memory IPC management."""


@ipc.command("status")
@click.option("--prefix", default="canvas_", show_default=True)
def ipc_status(prefix: str) -> None:
    """Show active shared memory regions."""
    import glob

    regions = sorted(glob.glob(f"/dev/shm/{prefix}*"))
    if not regions:
        click.echo(f"No shared memory regions found with prefix '{prefix}'")
        return
    click.echo(f"Active regions ({len(regions)}):")
    for r in regions:
        try:
            size = os.path.getsize(r)
            click.echo(f"  {os.path.basename(r)}  ({size} bytes)")
        except OSError:
            click.echo(f"  {os.path.basename(r)}  (unreadable)")


@ipc.command("cleanup")
@click.option("--prefix", default="canvas_", show_default=True)
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt.")
def ipc_cleanup(prefix: str, yes: bool) -> None:
    """Remove orphaned shared memory regions."""
    import glob

    regions = sorted(glob.glob(f"/dev/shm/{prefix}*"))
    if not regions:
        click.echo(f"No regions found with prefix '{prefix}'")
        return

    click.echo(f"Found {len(regions)} region(s):")
    for r in regions:
        click.echo(f"  {os.path.basename(r)}")

    if not yes:
        click.confirm("Remove all listed regions?", abort=True)

    removed = 0
    for r in regions:
        try:
            os.unlink(r)
            removed += 1
        except OSError as e:
            click.echo(f"  Could not remove {os.path.basename(r)}: {e}", err=True)

    click.echo(f"Removed {removed}/{len(regions)} region(s)")


if __name__ == "__main__":
    cli()
