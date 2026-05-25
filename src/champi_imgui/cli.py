"""CLI entry point for champi-imgui.

Required environment variables for canvas rendering:
  DISPLAY          - X11 display socket (e.g. :0 or :1)
  XAUTHORITY       - X11 auth cookie file (X11 only)
  WAYLAND_DISPLAY  - Wayland socket name (e.g. wayland-0)
  XDG_RUNTIME_DIR  - Runtime dir where the Wayland socket lives (Wayland only)

MCP clients strip the desktop session environment.  Add an "env" block to your
MCP server config so all required variables reach this process:

  Wayland (recommended):
    "env": {
      "WAYLAND_DISPLAY": "wayland-0",
      "XDG_RUNTIME_DIR": "/run/user/1000"
    }

  X11:
    "env": {
      "DISPLAY": ":0"
    }
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


def _check_display() -> None:
    """Abort with a clear message when the display environment is unusable."""
    display = os.environ.get("DISPLAY", "")
    wayland = os.environ.get("WAYLAND_DISPLAY", "")
    xdg = os.environ.get("XDG_RUNTIME_DIR", "")

    if not display and not wayland:
        click.echo(
            "ERROR: Neither DISPLAY nor WAYLAND_DISPLAY is set.\n"
            "Canvas windows cannot open without a display server.\n\n"
            "Add an 'env' block to your MCP server config, for example:\n\n"
            '  Wayland: "env": {"WAYLAND_DISPLAY": "wayland-0", "XDG_RUNTIME_DIR": "/run/user/1000"}\n'
            '  X11:     "env": {"DISPLAY": ":0"}',
            err=True,
        )
        sys.exit(1)

    if wayland and not xdg:
        click.echo(
            "ERROR: WAYLAND_DISPLAY is set but XDG_RUNTIME_DIR is missing.\n"
            f"The Wayland socket '{wayland}' cannot be resolved without XDG_RUNTIME_DIR.\n\n"
            "Add XDG_RUNTIME_DIR to your MCP server config 'env' block:\n\n"
            f'  "env": {{"WAYLAND_DISPLAY": "{wayland}", "XDG_RUNTIME_DIR": "/run/user/1000"}}',
            err=True,
        )
        sys.exit(1)

    if wayland and xdg:
        socket_path = os.path.join(xdg, wayland)
        if not os.path.exists(socket_path):
            click.echo(
                f"ERROR: Wayland socket not found at {socket_path!r}.\n"
                f"Verify XDG_RUNTIME_DIR={xdg!r} is correct for this user.",
                err=True,
            )
            sys.exit(1)


@click.group()
@click.version_option()
def cli() -> None:
    """Champi ImGui — MCP server for LLM-driven UI generation."""


@cli.command("serve")
def serve() -> None:
    """Start the MCP server (stdio transport for MCP clients)."""
    from champi_imgui.api.server import create_mcp_app

    _configure_logger()
    _check_display()
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
    _check_display()
    manager = CanvasManager()
    manager.create_canvas(canvas_id, title=title, size=(800, 800), auto_start=True)
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
    _check_display()
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
