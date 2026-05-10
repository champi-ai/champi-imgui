# MCP Tools API Reference

Complete listing of all MCP tools for the Champi-Gen-UI server.

---

## 1. Canvas Management (7 tools)

### create_canvas
Create a new ImGui canvas for rendering UI.

```python
{
    "name": "create_canvas",
    "description": "Create a new canvas for rendering ImGui UI",
    "inputSchema": {
        "type": "object",
        "properties": {
            "canvas_id": {"type": "string", "description": "Unique canvas identifier"},
            "width": {"type": "integer", "default": 1280},
            "height": {"type": "integer", "default": 720},
            "mode": {"type": "string", "enum": ["standard", "docking", "multi_viewport", "fullscreen", "overlay"], "default": "standard"},
            "title": {"type": "string", "default": "ImGui Canvas"}
        },
        "required": ["canvas_id"]
    }
}
```

### update_canvas
Modify canvas properties.

### clear_canvas
Reset canvas to empty state.

### get_canvas_state
Retrieve current canvas state and all widgets.

### set_canvas_mode
Switch between canvas rendering modes.

### resize_canvas
Adjust canvas dimensions.

### capture_canvas
Take screenshot or export canvas.

---

## 2. Basic Widgets (25 tools)

### add_button
```python
{
    "name": "add_button",
    "description": "Add a clickable button to the canvas",
    "inputSchema": {
        "type": "object",
        "properties": {
            "canvas_id": {"type": "string"},
            "widget_id": {"type": "string"},
            "label": {"type": "string"},
            "position": {"type": "array", "items": {"type": "number"}, "minItems": 2, "maxItems": 2},
            "size": {"type": "array", "items": {"type": "number"}, "minItems": 2, "maxItems": 2},
            "callback": {"type": "string", "description": "Callback function name"}
        },
        "required": ["canvas_id", "widget_id", "label"]
    }
}
```

### add_text
Add static text label.

### add_input_text
Add text input field.

### add_checkbox
Add checkbox widget.

### add_radio_button
Add radio button.

### add_slider_int
Add integer slider.

### add_slider_float
Add float slider.

### add_drag_int
Add integer drag control.

### add_drag_float
Add float drag control.

### add_combo
Add dropdown combo box.

### add_list_box
Add scrollable list.

### add_color_picker
Add color picker widget.

### add_tree_node
Add collapsible tree node.

### add_tab_bar
Add tab container.

### add_menu
Add menu item.

### add_tooltip
Add hover tooltip.

### add_progress_bar
Add progress indicator.

### add_separator
Add horizontal separator.

### add_spacing
Add vertical spacing.

### add_image
Display image texture.

### add_small_button
Add compact button.

### add_arrow_button
Add directional arrow button.

### add_input_int
Add integer input field.

### add_input_float
Add float input field.

### add_selectable
Add selectable item.

---

## 3. Container Widgets (5 tools)

### add_window
```python
{
    "name": "add_window",
    "description": "Add a standalone window container",
    "inputSchema": {
        "type": "object",
        "properties": {
            "canvas_id": {"type": "string"},
            "window_id": {"type": "string"},
            "title": {"type": "string"},
            "position": {"type": "array", "items": {"type": "number"}},
            "size": {"type": "array", "items": {"type": "number"}},
            "flags": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["canvas_id", "window_id", "title"]
    }
}
```

### add_child_window
Add embedded child region.

### add_group
Add layout group.

### add_panel
Add custom panel.

### add_collapsing_header
Add collapsible section header.

---

## 4. Layout Tools (10 tools)

### set_layout_horizontal
Arrange widgets horizontally.

### set_layout_vertical
Arrange widgets vertically.

### set_layout_grid
Create grid layout.

### set_layout_stack
Stack widgets.

### add_indent
Add indentation.

### set_item_width
Set widget width.

### align_text
Align text content.

### center_widget
Center widget in container.

### set_cursor_position
Manually position cursor.

### get_content_region_avail
Get available space.

---

## 5. Styling & Theming (12 tools)

### set_color_scheme
```python
{
    "name": "set_color_scheme",
    "description": "Apply a color theme to the canvas",
    "inputSchema": {
        "type": "object",
        "properties": {
            "canvas_id": {"type": "string"},
            "theme": {"type": "string", "enum": ["dark", "light", "classic", "dracula", "nord", "gruvbox"]}
        },
        "required": ["canvas_id", "theme"]
    }
}
```

### set_widget_style
Style individual widget.

### set_font
Change font family.

### set_font_size
Adjust font size.

### set_spacing
Configure padding/margins.

### apply_rounded_corners
Enable rounded corners.

### set_transparency
Set widget transparency.

### set_border_color
Configure border color.

### set_background_color
Set background color.

### push_style_var
Push style variable.

### pop_style_var
Pop style variable.

### get_style
Get current style settings.

---

## 6. Animation Tools (10 tools)

### create_animation
```python
{
    "name": "create_animation",
    "description": "Create keyframe-based animation",
    "inputSchema": {
        "type": "object",
        "properties": {
            "animation_id": {"type": "string"},
            "keyframes": {"type": "array", "items": {"type": "integer"}},
            "values": {"type": "array", "items": {"type": "number"}},
            "duration": {"type": "number"},
            "easing": {"type": "string", "enum": ["linear", "ease_in", "ease_out", "ease_in_out", "cubic", "bounce", "elastic"]}
        },
        "required": ["animation_id", "keyframes", "values"]
    }
}
```

### animate_value
Interpolate animated value.

### play_animation
Start animation playback.

### pause_animation
Pause animation.

### stop_animation
Stop animation.

### set_easing_function
Configure interpolation.

### create_transition
Create state transition.

### set_animation_loop
Enable/disable looping.

### get_animation_state
Query animation status.

### delete_animation
Remove animation.

---

## 7. File Dialog Tools (5 tools)

### open_file_dialog
```python
{
    "name": "open_file_dialog",
    "description": "Open file selection dialog",
    "inputSchema": {
        "type": "object",
        "properties": {
            "title": {"type": "string", "default": "Open File"},
            "initial_path": {"type": "string"},
            "filters": {"type": "array", "items": {"type": "string"}},
            "allow_multiple": {"type": "boolean", "default": false}
        }
    }
}
```

### open_dir_dialog
Open directory picker.

### save_file_dialog
Open save file dialog.

### set_file_filters
Configure file type filters.

### get_selected_files
Retrieve selected files.

---

## 8. Notification Tools (7 tools)

### show_notification
```python
{
    "name": "show_notification",
    "description": "Show toast notification",
    "inputSchema": {
        "type": "object",
        "properties": {
            "type": {"type": "string", "enum": ["success", "warning", "error", "info"]},
            "message": {"type": "string"},
            "title": {"type": "string"},
            "duration": {"type": "integer", "default": 3000}
        },
        "required": ["type", "message"]
    }
}
```

### show_success
Show success notification.

### show_warning
Show warning notification.

### show_error
Show error notification.

### show_info
Show info notification.

### clear_notifications
Clear all notifications.

### set_notification_position
Set notification position.

---

## 9. Table Tools (10 tools)

### create_table
```python
{
    "name": "create_table",
    "description": "Create data table widget",
    "inputSchema": {
        "type": "object",
        "properties": {
            "canvas_id": {"type": "string"},
            "table_id": {"type": "string"},
            "columns": {"type": "integer"},
            "rows": {"type": "array", "items": {"type": "array"}},
            "headers": {"type": "array", "items": {"type": "string"}},
            "flags": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["canvas_id", "table_id", "columns"]
    }
}
```

### table_add_row
Add row to table.

### table_set_cell
Set cell value.

### table_get_cell
Get cell value.

### table_setup_column
Configure column.

### table_sort
Sort table data.

### table_filter
Filter table rows.

### table_set_column_width
Set column width.

### table_enable_sorting
Enable sortable columns.

### table_enable_resizing
Enable column resizing.

---

## 10. Plotting Tools (15 tools)

### add_line_plot
```python
{
    "name": "add_line_plot",
    "description": "Create line chart",
    "inputSchema": {
        "type": "object",
        "properties": {
            "canvas_id": {"type": "string"},
            "plot_id": {"type": "string"},
            "x_data": {"type": "array", "items": {"type": "number"}},
            "y_data": {"type": "array", "items": {"type": "number"}},
            "label": {"type": "string"},
            "color": {"type": "array", "items": {"type": "number"}}
        },
        "required": ["canvas_id", "plot_id", "x_data", "y_data"]
    }
}
```

### add_scatter_plot
Create scatter plot.

### add_bar_chart
Create bar chart.

### add_histogram
Create histogram.

### add_heatmap
Create heat map.

### add_pie_chart
Create pie chart.

### add_area_plot
Create filled area plot.

### add_stem_plot
Create stem plot.

### add_error_bars
Add error bars.

### add_candlestick
Create candlestick chart.

### plot_set_limits
Set axis limits.

### plot_set_labels
Set axis labels.

### plot_set_legend
Configure legend.

### plot_add_annotation
Add text annotation.

### plot_enable_crosshair
Enable crosshair cursor.

---

## 11. Node Editor Tools (10 tools)

### create_node_editor
```python
{
    "name": "create_node_editor",
    "description": "Create node graph editor",
    "inputSchema": {
        "type": "object",
        "properties": {
            "canvas_id": {"type": "string"},
            "editor_id": {"type": "string"},
            "style": {"type": "string", "default": "default"}
        },
        "required": ["canvas_id", "editor_id"]
    }
}
```

### add_node
Add node to graph.

### add_node_input
Add input pin to node.

### add_node_output
Add output pin to node.

### add_link
Connect nodes.

### remove_node
Delete node.

### remove_link
Delete connection.

### get_node_connections
Query node connections.

### set_node_position
Position node.

### get_selected_nodes
Get selected nodes.

---

## 12. Text Editor Tools (8 tools)

### create_code_editor
```python
{
    "name": "create_code_editor",
    "description": "Create syntax-highlighted code editor",
    "inputSchema": {
        "type": "object",
        "properties": {
            "canvas_id": {"type": "string"},
            "editor_id": {"type": "string"},
            "language": {"type": "string", "default": "python"},
            "read_only": {"type": "boolean", "default": false}
        },
        "required": ["canvas_id", "editor_id"]
    }
}
```

### set_editor_text
Set editor content.

### get_editor_text
Get editor content.

### set_editor_language
Change syntax highlighting.

### set_editor_readonly
Toggle read-only mode.

### editor_add_breakpoint
Add breakpoint marker.

### editor_goto_line
Jump to line number.

### editor_find_replace
Find and replace text.

---

## 13. Memory Editor Tools (5 tools)

### add_memory_editor
Create hex editor widget.

### set_memory_data
Load data into editor.

### set_memory_readonly
Toggle read-only mode.

### highlight_memory_range
Highlight byte range.

### get_memory_selection
Get selected bytes.

---

## 14. Input Handling Tools (10 tools)

### register_key_callback
Register keyboard event handler.

### register_mouse_callback
Register mouse event handler.

### register_click_callback
Register click handler.

### set_drag_drop_source
Enable drag source.

### set_drag_drop_target
Enable drop target.

### capture_input_state
Poll input state.

### is_key_pressed
Check key state.

### is_mouse_clicked
Check mouse button.

### get_mouse_position
Get cursor position.

### set_keyboard_focus
Set input focus.

---

## 15. Drawing Tools (15 tools)

### draw_line
Draw line on canvas.

### draw_rect
Draw rectangle.

### draw_circle
Draw circle.

### draw_polygon
Draw polygon.

### draw_text
Draw text.

### draw_image
Draw image texture.

### draw_bezier_curve
Draw bezier curve.

### draw_arrow
Draw arrow.

### set_clip_rect
Set clipping region.

### push_draw_layer
Create draw layer.

### pop_draw_layer
Remove draw layer.

### get_draw_list
Get canvas draw list.

### draw_grid
Draw grid lines.

### draw_crosshair
Draw crosshair.

### clear_drawings
Clear all drawings.

---

## 16. Data Binding Tools (8 tools)

### bind_data_source
Connect external data source.

### create_live_chart
Create real-time chart.

### update_widget_data
Update widget dynamically.

### watch_variable
Watch variable changes.

### bind_widget_property
Bind widget to data.

### unbind_widget
Remove data binding.

### refresh_data
Refresh bound data.

### get_bound_data
Query bound data.

---

## 17. Export/Import Tools (8 tools)

### export_ui_json
```python
{
    "name": "export_ui_json",
    "description": "Export UI definition as JSON",
    "inputSchema": {
        "type": "object",
        "properties": {
            "canvas_id": {"type": "string"},
            "file_path": {"type": "string"}
        },
        "required": ["canvas_id"]
    }
}
```

### import_ui_json
Load UI from JSON.

### generate_code
Export to Python code.

### create_template
Save as template.

### load_template
Load UI template.

### list_templates
List available templates.

### delete_template
Remove template.

### export_screenshot
Save canvas image.

---

## 18. Custom Widgets (10 tools)

### add_knob
Add rotary knob.

### add_toggle
Add toggle switch.

### add_spinner
Add loading spinner.

### add_date_picker
Add date selector.

### add_time_picker
Add time selector.

### add_gradient_editor
Add gradient editor.

### add_color_gradient
Display color gradient.

### add_spin_input
Add spin input.

### add_slider_2d
Add 2D slider.

### add_slider_3d
Add 3D slider.

---

## 19. Advanced Features (8 tools)

### enable_docking
Enable window docking.

### enable_multi_viewport
Enable multi-viewport.

### create_viewport
Create new viewport.

### set_viewport_properties
Configure viewport.

### enable_keyboard_nav
Enable keyboard navigation.

### enable_gamepad_nav
Enable gamepad navigation.

### set_ini_filename
Set layout save file.

### load_layout
Load saved layout.

---

## 20. Utility Tools (7 tools)

### get_widget_bounds
Get widget dimensions.

### is_widget_hovered
Check hover state.

### is_widget_focused
Check focus state.

### set_widget_visible
Show/hide widget.

### delete_widget
Remove widget.

### get_all_widgets
List all widgets.

### get_widget_property
Get widget property.

---

## Summary

**Total MCP Tools: 200+**

Organized into 20 categories:
1. Canvas Management (7)
2. Basic Widgets (25)
3. Container Widgets (5)
4. Layout Tools (10)
5. Styling & Theming (12)
6. Animation Tools (10)
7. File Dialog Tools (5)
8. Notification Tools (7)
9. Table Tools (10)
10. Plotting Tools (15)
11. Node Editor Tools (10)
12. Text Editor Tools (8)
13. Memory Editor Tools (5)
14. Input Handling Tools (10)
15. Drawing Tools (15)
16. Data Binding Tools (8)
17. Export/Import Tools (8)
18. Custom Widgets (10)
19. Advanced Features (8)
20. Utility Tools (7)

All tools return structured responses with:
- `success`: Boolean indicating operation success
- `data`: Result data or widget state
- `error`: Error message if applicable
