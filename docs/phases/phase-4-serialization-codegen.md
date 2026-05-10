# Phase 4: Serialization, Code Generation & Templates (Stage 8)

## Goal
Add JSON export/import, Python code generation, and a template save/load/list/delete system — with MCP tools and tests — making the system fully self-contained and completing Stage 8.

## Deliverables

### Backend

#### Serialization
- [ ] `src/champi_imgui/core/serialization.py`
  - Source: `/home/diva/git/champi-gen-ui/src/champi_gen_ui/core/serialization.py` (~432 lines)
  - Classes: UIExporter, UIImporter, TemplateManager

  UIExporter:
  - `export_to_json(canvas, filepath: str) -> bool` — write `canvas.serialize()` to file as indented JSON
  - `export_canvas_state(canvas) -> str` — return JSON string

  UIImporter:
  - `import_from_json(filepath: str, canvas_manager: CanvasManager) -> Canvas | None`
  - Reads JSON, calls `canvas_manager.create_canvas()`, then recreates widgets via the WidgetFactory using `widget_type` and stored properties from each widget's serialized dict

  TemplateManager:
  - `__init__(template_dir: str = "templates")` — creates dir if missing
  - `save_template(name, canvas, description) -> bool` — writes `{"name", "description", "canvas": canvas.serialize()}` to `{template_dir}/{name}.json`
  - `load_template(name, canvas_manager) -> Canvas | None` — reads template file, delegates to UIImporter
  - `list_templates() -> list[dict]` — returns `[{"name", "description"}]` for all `.json` files in template_dir
  - `delete_template(name) -> bool` — removes `{template_dir}/{name}.json`

#### Code generation
- [ ] `src/champi_imgui/core/codegen.py`
  - Source: `/home/diva/git/champi-gen-ui/src/champi_gen_ui/core/codegen.py` (~364 lines)
  - Classes: CodeGenerator, TemplateCodeGenerator

  CodeGenerator:
  - `generate_canvas_code(canvas) -> str` — generates a complete, runnable Python script that recreates the canvas and all its widgets using champi_imgui imports
  - `generate_widget_code_snippet(widget_type, widget_id, **props) -> str` — generates a single widget construction line
  - Generated code uses `champi_imgui` imports (not `champi_gen_ui`)

  TemplateCodeGenerator:
  - `generate_component_template(name: str, widgets: list[str]) -> str` — generates a Python class wrapping the widget set as a reusable component

#### Server integration (`src/champi_imgui/server/main.py`)
Add global manager instantiation:
```python
template_manager = TemplateManager()
```

Add MCP tools (source reference: `/home/diva/git/champi-gen-ui/src/champi_gen_ui/server/main.py`):

Export/import tools:
- [ ] `export_canvas_json(canvas_id: str, filepath: str)` — calls `UIExporter.export_to_json()`
- [ ] `export_canvas_python(canvas_id: str, filepath: str)` — generates code and writes to file
- [ ] `import_canvas_json(filepath: str)` — calls `UIImporter.import_from_json()`, returns new canvas state
- [ ] `get_canvas_json(canvas_id: str)` — returns canvas JSON string inline (no file write)

Code generation tools:
- [ ] `generate_canvas_code(canvas_id: str)` — returns generated Python code as string in response
- [ ] `generate_widget_snippet(widget_type: str, widget_id: str, **props)` — returns single widget line
- [ ] `generate_component_template(name: str, widgets: list[str])` — returns template class code

Template tools:
- [ ] `save_template(name: str, canvas_id: str, description: str = "")`
- [ ] `load_template(name: str)` — loads and creates canvas, returns canvas state
- [ ] `list_templates()` — returns list of available templates with names and descriptions
- [ ] `delete_template(name: str)`

### Infrastructure
- [ ] `tests/test_serialization.py` — UIExporter, UIImporter round-trip tests (export then import, verify widget count and properties match)
- [ ] `tests/test_codegen.py` — CodeGenerator output tests (verify generated code is valid Python, contains correct class names and widget IDs)
- [ ] `tests/test_template_manager.py` — TemplateManager save/load/list/delete lifecycle test
- [ ] `tests/test_serialization_mcp_tools.py` — MCP tool integration tests for all 11 new tools

## Migration rules
1. Replace every `from champi_gen_ui.` with `from champi_imgui.`
2. Replace `champi_gen_ui` in generated code strings inside `CodeGenerator` with `champi_imgui` — these are string literals inside the generator, not imports
3. `UIImporter` must use the WidgetFactory that is attached to the canvas's widget_registry, not a standalone factory — the factory must have all widget types registered before import runs
4. `export_canvas_python` writes to disk — the MCP tool must validate filepath is writable and return a clear error if not
5. Template files are stored relative to the process working directory unless an absolute path is given — document this in the tool docstring

## Verification steps
```bash
uv run ruff check src/
uv run ruff format --check src/
uv run mypy src/
uv run pytest tests/
```

End-to-end smoke test after all tools pass:
```bash
uv run champi-imgui serve &
# Connect MCP client, create a canvas, add widgets, export to JSON, import back, verify widget count matches
```

## Parallel work
- BE: UIExporter + UIImporter can be implemented in parallel with BE: CodeGenerator + TemplateCodeGenerator
- Tests for serialization and codegen can be written in parallel with implementation
- MCP tools can be added after both codegen and serialization modules are stable

## Phase dependencies
- Requires: Phase 3 complete (all managers instantiated in server, canvas.serialize() includes widget state that UIImporter needs to reconstruct)

## Complexity
- Backend: M
- Frontend: N/A
- Infra: M

## Risks
- UIImporter round-trip fidelity: widgets must serialize ALL state needed for reconstruction. If a widget stores state outside `self.properties` (e.g., `self.value` set directly), the serializer must capture it. Review each widget class's `serialize()` output against `__init__` parameters before writing the importer.
- Generated Python code must use correct widget class names — these may differ between source and migrated repo if any class was renamed during migration
- Template directory defaults to a relative path; this will break if the MCP server is launched from different working directories. Consider making it configurable or defaulting to `~/.champi-imgui/templates/`
