# Phase 0: Image Widget

## Goal
Display images from file paths on an ImGui canvas via MCP tools.

## Deliverables

### Backend
- [ ] `ImageWidget` in `widgets/display.py` — loads PNG/JPG via OpenGL, caches texture ID, renders with `imgui.image()`
- [ ] Texture loading utility (OpenGL `glGenTextures` + `glTexImage2D`) using PIL/Pillow for decode
- [ ] `add_image` MCP tool in `server/main.py` following existing pattern
- [ ] `update_image` MCP tool to change file path or size at runtime
- [ ] Register `"image"` in WidgetFactory

### Frontend
- [ ] N/A (no separate frontend — ImGui is the UI)

### Infrastructure
- [ ] Add `Pillow` to project dependencies in `pyproject.toml`
- [ ] Unit tests for ImageWidget (texture loading mock, render call)
- [ ] Integration test: create canvas, add image widget, verify state serialization

## Done Definition
- `add_image` MCP tool creates a widget that renders an image from a file path
- Image displays at correct size in the ImGui window
- Changing the image path via `update_image` swaps the displayed image
- `uv run pytest tests/` passes, `uv run ruff check src/` passes

## Parallel work
- Texture loading utility can be developed independently from MCP tool wiring
- Tests can be written alongside widget implementation

## Phase dependencies
- Requires: none

## Complexity
- Backend: M
- Frontend: N/A
- Infra: S

## Risks
- OpenGL context must be active when loading textures — texture creation must happen on render thread via `queue_command()`
- imgui_bundle's OpenGL bindings may differ from raw PyOpenGL — need to verify `imgui.image()` accepts standard GL texture IDs
