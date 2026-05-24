# MCP Server Structure — champi-ai Standard

Reference document for the canonical layout and patterns used in all champi-ai MCP
server repositories. **champi-imgui** is the reference implementation.

---

## 1. Directory layout

```
src/<package>/
├── api/
│   ├── __init__.py        # exports create_mcp_app
│   └── server.py          # factory + all @mcp.tool() closures
├── cli.py                 # click group entry point
└── __init__.py
```

`server/main.py` with module-level globals is the **anti-pattern** this structure replaces.

---

## 2. Factory pattern — `create_mcp_app(**overrides)`

All managers are instantiated inside the factory. Callers override them via keyword
arguments (used in tests for injection without monkeypatching).

```python
# src/<package>/api/server.py
from contextlib import asynccontextmanager
from fastmcp import FastMCP

def create_mcp_app(**overrides: Any) -> FastMCP:
    canvas_manager = overrides.get("canvas_manager") or CanvasManager()
    event_queue    = overrides.get("event_queue")    or EventQueue()
    # ... remaining managers ...

    @asynccontextmanager
    async def _lifespan(app: Any) -> Any:
        yield
        canvas_manager.cleanup()

    mcp = FastMCP("champi-imgui", lifespan=_lifespan)

    # Expose managers for test access
    mcp._canvas_manager = canvas_manager  # type: ignore[attr-defined]

    @mcp.tool()
    def create_canvas(canvas_id: str, ...) -> dict[str, Any]:
        canvas = canvas_manager.get_canvas(canvas_id)  # closure, no global
        ...

    return mcp
```

`api/__init__.py` re-exports the factory:

```python
from <package>.api.server import create_mcp_app
__all__ = ["create_mcp_app"]
```

---

## 3. FastMCP lifespan for cleanup

Cleanup runs automatically when the server stops — no atexit or signal handlers needed
in `cli.py`.

```python
@asynccontextmanager
async def _lifespan(app: Any) -> Any:
    yield
    canvas_manager.cleanup()

mcp = FastMCP("champi-imgui", lifespan=_lifespan)
```

---

## 4. CLI group structure

`cli.py` uses a `click` group. `click>=8.0` must be an explicit `[project.dependencies]`
entry (not transitive).

```python
import click
from <package>.api.server import create_mcp_app

@click.group()
@click.version_option()
def cli() -> None:
    """<Package> — MCP server for ..."""

@cli.command("serve")
def serve() -> None:
    """Start the MCP server (stdio transport)."""
    mcp = create_mcp_app()
    mcp.run()

@cli.command("demo")
@click.option("--canvas-id", default="demo")
def demo(canvas_id: str) -> None:
    """Open a standalone demo window (no MCP required)."""
    ...

@cli.command("validate")
def validate() -> None:
    """Run installation validation."""
    ...

@cli.group()
def ipc() -> None:
    """Shared memory IPC management."""

@ipc.command("status")
def ipc_status() -> None: ...

@ipc.command("cleanup")
@click.option("--yes", "-y", is_flag=True)
def ipc_cleanup(yes: bool) -> None: ...
```

Entry point in `pyproject.toml`:

```toml
[project.scripts]
champi-imgui = "champi_imgui.cli:cli"   # always :cli, never :main
```

---

## 5. Testing — factory injection, no monkeypatching globals

```python
from champi_imgui.api.server import create_mcp_app

@pytest.fixture(autouse=True)
def fresh_canvas_manager(monkeypatch):
    manager = CanvasManager()
    monkeypatch.setattr(manager, "ensure_canvas_running", lambda _: True)
    _Server._mcp = create_mcp_app(canvas_manager=manager)
    yield manager
    _Server._mcp = None

# Call tools directly
result = mcp._tool_manager._tools["create_canvas"].fn(canvas_id, auto_start=False)
```

For multiple-manager injection (e.g. `get_system_state` tests):

```python
mcp = create_mcp_app(
    canvas_manager=mock_cm,
    animation_manager=MagicMock(...),
    theme_manager=MagicMock(...),
)
result = mcp._tool_manager._tools["get_system_state"].fn()
```

Never `monkeypatch.setattr(server_module, "canvas_manager", mock)` — that pattern
requires module-level globals which this architecture eliminates.

---

## 6. Tool return shape

Every MCP tool returns a consistent dict:

```python
{"success": True,  "data": {...}}   # on success
{"success": False, "error": "..."}  # on failure
```

```python
@mcp.tool()
def add_button(canvas_id: str, widget_id: str, ...) -> dict[str, Any]:
    try:
        canvas = canvas_manager.get_canvas(canvas_id)
        if canvas is None:
            return {"success": False, "error": f"Canvas '{canvas_id}' not found"}
        ...
        return {"success": True, "data": widget.serialize()}
    except Exception as e:
        logger.error(f"Error: {e}")
        return {"success": False, "error": str(e)}
```

---

## 7. Logging — stderr only

The MCP stdio transport uses stdout for JSON-RPC. All logging must go to stderr.

```python
from loguru import logger

logger.remove()
logger.add(sys.stderr, level="INFO", format="...")
```

Configure in `cli.py serve` before calling `mcp.run()`. Never configure logging at
import time in `api/server.py`.

---

## 8. Entry point naming

```toml
[project.scripts]
champi-imgui = "champi_imgui.cli:cli"
```

Always target the click `cli` group, never a bare `main()` function. This allows
`champi-imgui --help` to show all subcommands automatically.

---

## Reference implementations

| Repository | Status |
|---|---|
| `champi-imgui` | Conforms (this refactor) |
| `champi-stt` | Conforms (reference model for factory pattern) |
