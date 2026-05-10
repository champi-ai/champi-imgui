# Phase 3: Advanced Features (Stage 7)

## Goal
Add themes, layout management, data binding, and extensions (animation, notifications, file dialogs) — with MCP tools and tests for each — completing Stage 7.

## Deliverables

### Backend

#### Themes subsystem
- [ ] `src/champi_imgui/themes/__init__.py`
- [ ] `src/champi_imgui/themes/manager.py`
  - Source: `/home/diva/git/champi-gen-ui/src/champi_gen_ui/themes/manager.py` (~487 lines)
  - Classes: Theme (dataclass), ThemeManager
  - ThemeManager holds `_themes: dict[str, Theme]`, provides `register_theme()`, `apply_theme_by_name()`, `list_themes()`
  - `theme.apply()` sets ImGui style colors via `imgui.get_style()`
- [ ] `src/champi_imgui/themes/presets.py`
  - Source: `/home/diva/git/champi-gen-ui/src/champi_gen_ui/themes/presets.py` (~357 lines)
  - `THEME_PRESETS: dict[str, Theme]` — 9 themes: dark, light, cherry, nord, dracula, gruvbox, solarized_dark, monokai, material
  - Called at server startup to register all presets into ThemeManager

#### Layout subsystem
- [ ] `src/champi_imgui/layout/__init__.py`
- [ ] `src/champi_imgui/layout/manager.py`
  - Source: `/home/diva/git/champi-gen-ui/src/champi_gen_ui/layout/manager.py` (~178 lines)
  - Classes: LayoutMode (Enum: HORIZONTAL, VERTICAL, GRID, STACK, FREE), LayoutManager
  - LayoutManager: `set_mode()`, `set_spacing()`, `apply()` (calls imgui same-line / spacing calls)

#### Data binding
- [ ] `src/champi_imgui/core/binding.py`
  - Source: `/home/diva/git/champi-gen-ui/src/champi_gen_ui/core/binding.py` (~459 lines)
  - Classes: DataStore, BindingManager, ValidationManager
  - DataStore: path-based key/value store (`set(path, value)`, `get(path, default)`) with dot-notation paths
  - BindingManager: `bind(source_path, target_widget, target_property, bidirectional)`, `unbind()`, `update_all()` (called in render loop)
  - ValidationManager: validates widget values against registered rules

#### Extensions
- [ ] `src/champi_imgui/extensions/__init__.py`
- [ ] `src/champi_imgui/extensions/animation.py`
  - Source: `/home/diva/git/champi-gen-ui/src/champi_gen_ui/extensions/animation.py` (~478 lines)
  - Classes: EasingFunction (Enum), Animation (dataclass with keyframes), AnimationManager
  - AnimationManager: `create()`, `start()`, `stop()`, `get_value()` (interpolated), `update()` (called in render loop)
- [ ] `src/champi_imgui/extensions/notification.py`
  - Source: `/home/diva/git/champi-gen-ui/src/champi_gen_ui/extensions/notification.py` (~288 lines)
  - Classes: NotificationType (Enum: INFO, SUCCESS, WARNING, ERROR), Notification (dataclass), NotificationManager
  - NotificationManager: `add()`, `render()` (called in render loop, draws toast overlays), `clear()`
- [ ] `src/champi_imgui/extensions/file_dialog.py`
  - Source: `/home/diva/git/champi-gen-ui/src/champi_gen_ui/extensions/file_dialog.py` (~312 lines)
  - Classes: FileDialogWidget (extends Widget), MessageDialog (extends Widget)
  - Modes: open_file, open_folder, save_file
  - `selected_path` property holds result after user interaction

#### Server integration (`src/champi_imgui/server/main.py`)
Add global manager instantiation at module level:
```python
theme_manager = ThemeManager()
layout_manager = LayoutManager()
data_store = DataStore()
binding_manager = BindingManager(data_store)
animation_manager = AnimationManager()
notification_manager = NotificationManager()
```
Register preset themes at startup.

Add MCP tools (source reference: `/home/diva/git/champi-gen-ui/src/champi_gen_ui/server/main.py`):

Theme tools:
- [ ] `apply_theme(theme_name: str)`
- [ ] `list_themes()`

Layout tools:
- [ ] `set_layout_mode(mode: str)`
- [ ] `set_layout_spacing(spacing: float)`

Extension widget tools:
- [ ] `add_file_dialog(canvas_id, widget_id, button_label, mode)`
- [ ] `show_message_dialog(canvas_id, widget_id, title, message, buttons)`

Notification tools:
- [ ] `show_notification(title, message, type, duration)`
- [ ] `clear_notifications()`

Animation tools:
- [ ] `create_animation(name, start_value, end_value, duration, easing, loop)`
- [ ] `start_animation(name)`
- [ ] `stop_animation(name)`
- [ ] `get_animation_value(name)`

Data binding tools:
- [ ] `set_data(path, value)`
- [ ] `get_data(path, default)`
- [ ] `bind_data(source_path, target_widget, target_property, bidirectional)`
- [ ] `unbind_data(source_path, target_widget)`

### Infrastructure
- [ ] `tests/test_theme_manager.py`
- [ ] `tests/test_layout_manager.py`
- [ ] `tests/test_data_binding.py`
- [ ] `tests/test_animation.py`
- [ ] `tests/test_notifications.py`
- [ ] `tests/test_file_dialog.py`
- [ ] `tests/test_advanced_mcp_tools.py`

## Migration rules
1. Replace every `from champi_gen_ui.` with `from champi_imgui.`
2. Theme `apply()` must be called via `canvas.queue_command()` because it calls `imgui.get_style()` which requires the render thread
3. `BindingManager.update_all()` and `AnimationManager.update()` must be called inside the canvas render loop (hook into `Canvas.render()` or `process_commands()`)
4. `NotificationManager.render()` must be called inside the render loop after all widgets are rendered
5. DataStore paths use dot-notation: `"user.name"`, `"settings.theme"`

## Verification steps
```bash
uv run ruff check src/
uv run ruff format --check src/
uv run mypy src/
uv run pytest tests/
```

## Parallel work
- BE: themes + layout can be implemented simultaneously with BE: data binding
- BE: animation + notification + file_dialog can be implemented in parallel
- Tests for each subsystem can be written in parallel with implementation
- Server MCP tool additions can be done after each subsystem is stable (not all at once)

## Phase dependencies
- Requires: Phase 2 complete (all widget modules on main, factory registrations working, canvas IPC confirmed stable)

## Complexity
- Backend: XL
- Frontend: N/A
- Infra: M

## Risks
- Theme application requires calling ImGui style APIs from the render thread — never call `theme.apply()` directly from an MCP tool without `queue_command()`
- Animation timing depends on wall-clock time; `AnimationManager.update()` must receive the current timestamp, not frame count
- File dialog widget may depend on OS file picker APIs not available on all platforms — check `imgui_bundle` for native file dialog support vs custom implementation
- BindingManager bidirectional binding creates potential infinite update loops — review source implementation carefully before porting
