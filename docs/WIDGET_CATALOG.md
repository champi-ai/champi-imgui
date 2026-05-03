# Widget Catalog - Complete Reference

## Basic Input Widgets

### Button
- **add_button**: Standard clickable button
- **add_small_button**: Compact button variant
- **add_arrow_button**: Directional arrow button
- **add_invisible_button**: Clickable area without visual

### Text Widgets
- **add_text**: Static text label
- **add_text_colored**: Colored text
- **add_text_disabled**: Grayed-out text
- **add_text_wrapped**: Auto-wrapping text
- **add_bullet_text**: Bulleted text
- **add_label_text**: Label-value pair

### Input Fields
- **add_input_text**: Single-line text input
- **add_input_text_multiline**: Multi-line text area
- **add_input_text_with_hint**: Input with placeholder
- **add_input_int**: Integer input
- **add_input_float**: Float input
- **add_input_double**: Double precision input
- **add_input_scalar**: Generic scalar input

---

## Selection Widgets

### Checkbox & Radio
- **add_checkbox**: Boolean checkbox
- **add_checkbox_flags**: Multi-flag checkbox
- **add_radio_button**: Radio button (single)
- **add_radio_button_group**: Radio button group

### Combo & List
- **add_combo**: Dropdown combo box
- **add_combo_simple**: Simple string combo
- **add_list_box**: Scrollable list
- **add_selectable**: Selectable item
- **add_selectable_with_bool**: Selectable with state

---

## Slider & Drag Widgets

### Sliders
- **add_slider_int**: Integer slider
- **add_slider_float**: Float slider
- **add_slider_angle**: Angle slider (degrees/radians)
- **add_slider_int2/3/4**: Multi-component sliders
- **add_slider_float2/3/4**: Vector sliders
- **add_v_slider**: Vertical slider

### Drag Controls
- **add_drag_int**: Integer drag control
- **add_drag_float**: Float drag control
- **add_drag_int2/3/4**: Multi-component drag
- **add_drag_float2/3/4**: Vector drag

---

## Color Widgets

- **add_color_edit3**: RGB color picker
- **add_color_edit4**: RGBA color picker
- **add_color_picker3**: RGB picker dialog
- **add_color_picker4**: RGBA picker dialog
- **add_color_button**: Color preview button

---

## Tree & Hierarchy Widgets

- **add_tree_node**: Collapsible tree node
- **add_tree_node_ex**: Tree with flags
- **add_collapsing_header**: Collapsible section
- **add_tree_push**: Manual tree depth

---

## Menu & Navigation

### Menus
- **add_menu_bar**: Main menu bar
- **add_menu**: Menu item
- **add_menu_item**: Menu entry
- **add_menu_item_checkable**: Checkable menu

### Tabs
- **add_tab_bar**: Tab container
- **add_tab_item**: Tab page
- **add_tab_item_button**: Tab with button

---

## Container Widgets

### Windows
- **add_window**: Standalone window
- **add_child_window**: Embedded child region
- **add_child_frame**: Framed child region

### Groups & Panels
- **add_group**: Layout group
- **add_indent**: Indented block
- **add_panel**: Custom panel

---

## Table Widgets

- **begin_table**: Start table
- **table_next_row**: New table row
- **table_next_column**: Next column
- **table_set_column_index**: Jump to column
- **table_setup_column**: Configure column
- **table_headers_row**: Header row

---

## Plotting Widgets (ImPlot)

### Line Plots
- **add_line_plot**: Line chart
- **add_scatter_plot**: Scatter plot
- **add_stairs_plot**: Step chart
- **add_shaded_plot**: Filled area

### Bar Charts
- **add_bar_chart**: Vertical bars
- **add_bar_chart_h**: Horizontal bars
- **add_bar_group**: Grouped bars

### Specialized Plots
- **add_pie_chart**: Pie chart
- **add_heatmap**: Heat map
- **add_histogram**: Histogram
- **add_error_bars**: Error bar plot
- **add_stem_plot**: Stem plot
- **add_digital_plot**: Digital signal

---

## Custom Extended Widgets

### Knobs (Third-party)
- **add_knob**: Rotary knob
- **add_knob_float**: Float knob
- **add_knob_int**: Integer knob

### Toggles
- **add_toggle**: Toggle switch
- **add_toggle_animated**: Animated toggle

### Spinners
- **add_spinner**: Loading spinner
- **add_spinner_dots**: Dot spinner
- **add_spinner_bars**: Bar spinner

### Date/Time
- **add_date_picker**: Date selector
- **add_time_picker**: Time selector
- **add_calendar**: Calendar widget

### Gradients
- **add_gradient_editor**: Gradient editor
- **add_gradient_bar**: Gradient display

---

## Node Editor Widgets

- **create_node_editor**: Node graph canvas
- **add_node**: Graph node
- **add_node_input**: Input pin
- **add_node_output**: Output pin
- **add_link**: Node connection
- **add_node_group**: Node group

---

## Text Editor Widgets

- **create_text_editor**: Code editor
- **create_markdown_editor**: Markdown editor
- **set_syntax_highlighting**: Enable syntax
- **set_editor_language**: Language mode
- **add_breakpoint**: Editor breakpoint

---

## File Dialog Widgets

### ImGuiFD
- **open_file_dialog**: File picker
- **open_dir_dialog**: Directory picker
- **save_file_dialog**: Save dialog

### Filters
- **add_file_filter**: File type filter
- **set_default_path**: Default directory

---

## Notification Widgets

- **show_notification**: Generic toast
- **show_success**: Success notification
- **show_warning**: Warning notification
- **show_error**: Error notification
- **show_info**: Info notification
- **set_notification_duration**: Set timeout
- **set_notification_position**: Position config

---

## Memory/Hex Editor

- **add_memory_editor**: Hex editor widget
- **set_memory_data**: Load data
- **set_memory_readonly**: Read-only mode
- **highlight_memory_range**: Highlight bytes

---

## Tooltip & Popup Widgets

### Tooltips
- **add_tooltip**: Hover tooltip
- **add_tooltip_text**: Simple text tooltip
- **begin_tooltip**: Custom tooltip content

### Popups
- **add_popup**: Generic popup
- **add_modal_popup**: Modal dialog
- **add_context_menu**: Right-click menu
- **add_popup_menu**: Popup menu

---

## Image & Texture Widgets

- **add_image**: Display image
- **add_image_button**: Clickable image
- **add_texture**: Load texture
- **set_texture_filtering**: Filter mode

---

## Progress & Status Widgets

- **add_progress_bar**: Progress indicator
- **add_loading_indicator**: Loading animation
- **add_status_bar**: Status bar

---

## Separator & Spacing

- **add_separator**: Horizontal line
- **add_vertical_separator**: Vertical line
- **add_spacing**: Vertical space
- **add_dummy**: Empty space
- **add_newline**: Force new line

---

## Drag & Drop

- **begin_drag_drop_source**: Drag source
- **begin_drag_drop_target**: Drop target
- **set_drag_drop_payload**: Data payload
- **accept_drag_drop_payload**: Accept drop

---

## Total Widget Count: 150+

This catalog covers:
- ✅ All ImGui core widgets
- ✅ ImPlot visualization widgets
- ✅ Third-party extensions (knobs, toggles, spinners)
- ✅ File dialogs (ImGuiFD)
- ✅ Notifications (imgui-notify)
- ✅ Node editors
- ✅ Text/code editors
- ✅ Memory/hex editors
- ✅ Custom community widgets
