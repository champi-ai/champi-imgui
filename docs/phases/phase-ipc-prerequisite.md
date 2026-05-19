# Phase: IPC Prerequisite

## Goal
The IPC command layer correctly separates title and size updates, uses explicit cross-platform struct layout, and produces correct values on all supported architectures (x86-64 and ARM64 / Apple Silicon).

## Deliverables

### Backend
- [ ] Fix `unpack_command` in `ipc/structs.py` to handle `UPDATE_TITLE` and `UPDATE_SIZE` (remove stale `UPDATE_STATE` / `UPDATE_STATE_STRUCT` references)
- [ ] Update `_process_ipc_command` in `core/canvas.py` to dispatch `UPDATE_TITLE` and `UPDATE_SIZE` separately (remove `UPDATE_STATE` handler)
- [ ] Add `_handle_update_title` and `_handle_update_size` methods to Canvas
- [ ] Update `update_canvas_state` MCP tool in `server/main.py` to send `UPDATE_TITLE` when only title changes, `UPDATE_SIZE` when only size changes, or both commands sequentially when both change
- [ ] Remove all remaining references to `CommandType.UPDATE_STATE` across the codebase

### Infrastructure
- [ ] Add `[project.optional-dependencies] ecosystem` to `pyproject.toml` with `champi-signals` and `champi-ipc` as optional deps
- [ ] Add `HAS_ECOSYSTEM` import guard pattern to a shared utils module for reuse in later phases

### Cross-platform struct fix (Apple Silicon / ARM64)
- [ ] Change all struct format strings in `ipc/structs.py` from `=` (native byte order) to `<` (explicit little-endian) to guarantee consistent wire format across Linux x86-64 and macOS ARM64
- [ ] Add 3 explicit padding bytes (`3x`) before the `II` fields in `UPDATE_SIZE_STRUCT` so integer fields land on 4-byte-aligned offsets (offset 73 → 76) — fixes incorrect width/height reads on strict-alignment architectures
- [ ] Add a round-trip pack/unpack test for `UPDATE_SIZE_STRUCT` asserting exact `width` and `height` values survive serialization

### Validation
- [ ] All existing tests pass (`uv run pytest`)
- [ ] Linting and type checks pass (`uv run ruff check src/` and `uv run mypy src/`)
- [ ] Manual test: `update_canvas_state(canvas_id, title="New Title")` does not reset canvas size
- [ ] Manual test: `update_canvas_state(canvas_id, width=1024, height=768)` does not blank the title
- [ ] Round-trip test passes: pack then unpack `UPDATE_SIZE` yields identical width and height on both x86-64 and ARM64

## Done Definition
- No references to `UPDATE_STATE` or `UPDATE_STATE_STRUCT` remain in `src/`
- `CommandType` enum has `UPDATE_TITLE = 3`, `UPDATE_SIZE = 4`, `SHUTDOWN = 5` (already correct in command_types.py)
- `update_canvas_state` MCP tool sends the correct minimal command(s) based on which parameters are provided
- `pyproject.toml` has `ecosystem` optional-dependencies group
- All existing tests pass without modification (or with minimal test updates if tests directly referenced `UPDATE_STATE`)

## Parallel work
- BE: structs.py + canvas.py IPC fix can run alongside INFRA: pyproject.toml ecosystem extras
- BE: server/main.py tool update can start once structs.py pack/unpack is done

## Phase dependencies
- Requires: none (this is the prerequisite for both MCP Render Fix and MCP System State Reporter)

## Complexity
- Backend: S
- Frontend: N/A
- Infra: S

## Risks
- The `unpack_command` function in structs.py currently references `UPDATE_STATE_STRUCT` which does not exist as a defined struct (it was renamed but the unpack path was not updated). This is a latent bug that will cause a `NameError` at runtime if any IPC message with command type 3 is received through the unpack path.
- Existing tests may assert on `UPDATE_STATE` by name. These need updating but the scope is small.
- Adding padding bytes to `UPDATE_SIZE_STRUCT` changes the wire format (total size 81 → 84 bytes). Since shared memory regions are re-created fresh on each process start, this is not a rolling-upgrade concern. All consumers must be updated atomically (they are in the same repo).
