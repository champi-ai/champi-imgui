# Phase 2: CLI Rewrite with Click Group

## Goal
Replace the existing CLI with a `click` group providing `serve`, `demo`, `validate`, and nested `ipc` subcommands (`cleanup`, `status`).

## Deliverables

### Backend
- [ ] Add `click>=8.0` to `[project.dependencies]` in `pyproject.toml`
- [ ] Rewrite `src/champi_imgui/cli.py` using `@click.group()`
- [ ] Implement `serve` subcommand (starts MCP server via `create_mcp_app`)
- [ ] Implement `demo` subcommand (launches demo canvas)
- [ ] Implement `validate` subcommand (checks IPC/system health)
- [ ] Implement nested `ipc` group with `cleanup` and `status` subcommands
- [ ] Fix entry point in `pyproject.toml`: `champi_imgui.cli:main` -> `champi_imgui.cli:cli`

### Frontend
- [ ] N/A

### Infrastructure
- [ ] Run `uv lock` / `uv sync` after dependency addition

## Done Definition
- `uv run champi-imgui --help` shows group with `serve`, `demo`, `validate`, `ipc` subcommands
- `uv run champi-imgui ipc --help` shows `cleanup` and `status` subcommands
- `uv run champi-imgui serve` starts the MCP server (calls `create_mcp_app`)
- Entry point in `pyproject.toml` is `champi_imgui.cli:cli`
- `click` is listed in `[project.dependencies]`
- `ruff check src/` passes
- `mypy src/` passes
- `uv run pytest` passes

## Parallel work
- N/A (single-track: depends on Phase 1 factory being available for `serve`)

## Phase dependencies
- Requires: Phase 1 `create_mcp_app` factory (CLI `serve` calls it)

## Complexity
- Backend: M
- Frontend: N/A
- Infra: S

## Risks
- Existing scripts or CI calling `champi-imgui` without subcommand will break (breaking change)
- `demo` subcommand may require optional GUI dependencies not available in CI
