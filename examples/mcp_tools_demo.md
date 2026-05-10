# MCP Tools Demo

This document demonstrates how to use the Champi-Gen-UI MCP server tools to create UIs through natural language.

## How It Works

1. Start the MCP server: `champi-gen-ui serve`
2. Connect your LLM to the MCP server
3. Use natural language to create UIs

## Example Interactions

### Example 1: Simple Hello World UI

**User:** "Create a simple UI with a title that says 'Hello World' and a button that says 'Click Me'"

**MCP Tools Executed:**
```json
// Create canvas
create_canvas(
  canvas_id="hello_world",
  width=800,
  height=600,
  mode="standard",
  title="Hello World Demo"
)

// Add title text
add_text(
  canvas_id="hello_world",
  widget_id="title",
  text="Hello World",
  color=[0.2, 0.8, 0.2, 1.0],
  position=[20, 20]
)

// Add button
add_button(
  canvas_id="hello_world",
  widget_id="btn1",
  label="Click Me",
  size=[120, 40],
  position=[20, 60]
)
```

### Example 2: Dashboard with Charts

**User:** "Create a dashboard with performance metrics showing CPU, Memory, and Disk usage as progress bars, and a line chart showing response times"

**MCP Tools Executed:**
```json
// Create docking canvas for flexible layout
create_canvas(
  canvas_id="dashboard",
  width=1280,
  height=800,
  mode="docking",
  title="Performance Dashboard"
)

// Apply theme
apply_theme(theme_name="nord")

// Add title
add_text(
  canvas_id="dashboard",
  widget_id="title",
  text="Performance Dashboard",
  color=[0.3, 0.7, 1.0, 1.0],
  position=[10, 10]
)

// Add CPU progress bar
add_text(
  canvas_id="dashboard",
  widget_id="cpu_label",
  text="CPU Usage:",
  position=[10, 50]
)

add_progress_bar(
  canvas_id="dashboard",
  widget_id="cpu_progress",
  fraction=0.65,
  overlay="65%"
)

// Add Memory progress bar
add_text(
  canvas_id="dashboard",
  widget_id="memory_label",
  text="Memory Usage:",
  position=[10, 90]
)

add_progress_bar(
  canvas_id="dashboard",
  widget_id="memory_progress",
  fraction=0.42,
  overlay="42%"
)

// Add Disk progress bar
add_text(
  canvas_id="dashboard",
  widget_id="disk_label",
  text="Disk Usage:",
  position=[10, 130]
)

add_progress_bar(
  canvas_id="dashboard",
  widget_id="disk_progress",
  fraction=0.78,
  overlay="78%"
)

// Add line chart for response times
add_line_chart(
  canvas_id="dashboard",
  widget_id="response_chart",
  title="Response Time (ms)",
  x_data=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
  y_data=[45, 52, 48, 65, 58, 71, 68, 75, 72, 78, 82]
)
```

### Example 3: Settings Panel

**User:** "Create a settings panel with theme selection, sliders for adjusting values, and color pickers"

**MCP Tools Executed:**
```json
// Create canvas
create_canvas(
  canvas_id="settings",
  width=600,
  height=800,
  mode="standard",
  title="Settings Panel"
)

// Add collapsing header for theme section
add_collapsing_header(
  canvas_id="settings",
  widget_id="theme_header",
  label="Theme Settings",
  default_open=true
)

// Add theme selectables
add_selectable(
  canvas_id="settings",
  widget_id="theme_dark",
  label="Dark Theme",
  selected=true
)

add_selectable(
  canvas_id="settings",
  widget_id="theme_light",
  label="Light Theme",
  selected=false
)

add_selectable(
  canvas_id="settings",
  widget_id="theme_nord",
  label="Nord Theme",
  selected=false
)

// Add separator
add_separator(
  canvas_id="settings",
  widget_id="sep1"
)

// Add slider for volume
add_slider_float(
  canvas_id="settings",
  widget_id="volume_slider",
  label="Volume",
  value=0.75,
  v_min=0.0,
  v_max=1.0
)

// Add slider for brightness
add_slider_int(
  canvas_id="settings",
  widget_id="brightness_slider",
  label="Brightness",
  value=80,
  v_min=0,
  v_max=100
)

// Add color picker for accent color
add_color_picker(
  canvas_id="settings",
  widget_id="accent_color",
  label="Accent Color",
  color=[0.3, 0.7, 1.0, 1.0]
)

// Add checkboxes
add_checkbox(
  canvas_id="settings",
  widget_id="auto_save",
  label="Auto-save settings",
  checked=true
)

add_checkbox(
  canvas_id="settings",
  widget_id="notifications",
  label="Enable notifications",
  checked=false
)
```

### Example 4: Data Visualization

**User:** "Create a data visualization UI with different chart types: line chart, bar chart, scatter plot, and pie chart"

**MCP Tools Executed:**
```json
// Create large canvas
create_canvas(
  canvas_id="viz",
  width=1600,
  height=900,
  mode="docking",
  title="Data Visualization"
)

// Add line chart
add_line_chart(
  canvas_id="viz",
  widget_id="line_chart",
  title="Sales Trend",
  x_data=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
  y_data=[120, 135, 128, 145, 152, 168, 175, 182, 198, 215, 225, 240]
)

// Add bar chart
add_bar_chart(
  canvas_id="viz",
  widget_id="bar_chart",
  title="Quarterly Revenue",
  values=[125000, 148000, 165000, 182000],
  labels=["Q1", "Q2", "Q3", "Q4"]
)

// Add scatter plot
add_scatter_plot(
  canvas_id="viz",
  widget_id="scatter_plot",
  title="User Engagement",
  x_data=[10, 20, 30, 40, 50, 60, 70, 80, 90],
  y_data=[15, 25, 35, 42, 55, 65, 72, 85, 95]
)

// Add pie chart
add_pie_chart(
  canvas_id="viz",
  widget_id="pie_chart",
  values=[35, 25, 20, 15, 5],
  labels=["Direct", "Organic", "Referral", "Social", "Other"]
)

// Add controls
add_button(
  canvas_id="viz",
  widget_id="refresh_btn",
  label="Refresh Data",
  size=[150, 40]
)

add_button(
  canvas_id="viz",
  widget_id="export_btn",
  label="Export Charts",
  size=[150, 40]
)
```

### Example 5: Interactive Form

**User:** "Create a user registration form with input fields for name, email, password, a checkbox for terms acceptance, and a submit button"

**MCP Tools Executed:**
```json
// Create canvas
create_canvas(
  canvas_id="registration",
  width=500,
  height=600,
  mode="standard",
  title="User Registration"
)

// Apply theme
apply_theme(theme_name="material")

// Add header
add_text(
  canvas_id="registration",
  widget_id="header",
  text="Create Account",
  color=[0.2, 0.6, 1.0, 1.0]
)

// Add name input
add_input_text(
  canvas_id="registration",
  widget_id="name_input",
  label="Full Name",
  value="",
  hint="Enter your full name"
)

// Add email input
add_input_text(
  canvas_id="registration",
  widget_id="email_input",
  label="Email",
  value="",
  hint="your@email.com"
)

// Add password input
add_input_text(
  canvas_id="registration",
  widget_id="password_input",
  label="Password",
  value="",
  hint="Enter password"
)

// Add separator
add_separator(
  canvas_id="registration",
  widget_id="sep1"
)

// Add terms checkbox
add_checkbox(
  canvas_id="registration",
  widget_id="terms_check",
  label="I agree to the Terms and Conditions",
  checked=false
)

// Add privacy checkbox
add_checkbox(
  canvas_id="registration",
  widget_id="privacy_check",
  label="I accept the Privacy Policy",
  checked=false
)

// Add separator
add_separator(
  canvas_id="registration",
  widget_id="sep2"
)

// Add submit button
add_button(
  canvas_id="registration",
  widget_id="submit_btn",
  label="Create Account",
  size=[200, 40]
)

// Add help marker
add_help_marker(
  canvas_id="registration",
  widget_id="help1",
  text="All fields are required. Password must be at least 8 characters.",
  marker="(?)"
)
```

## Advanced Features

### Animations

```json
// Create animation for a widget
create_animation(
  name="fade_in",
  start_value=0.0,
  end_value=1.0,
  duration=1.5,
  easing="ease_in_out_cubic",
  loop=false
)

// Start the animation
start_animation(name="fade_in")

// Get current animation value
get_animation_value(name="fade_in")
```

### Data Binding

```json
// Set data in store
set_data(path="user.name", value="John Doe")
set_data(path="user.email", value="john@example.com")

// Bind data to widget
bind_data(
  source_path="user.name",
  target_widget="name_input",
  target_property="value",
  bidirectional=true
)
```

### Notifications

```json
// Show notification
show_notification(
  title="Success",
  message="Profile updated successfully!",
  type="success",
  duration=3.0
)

// Show different notification types
show_notification(
  title="Warning",
  message="Low disk space",
  type="warning",
  duration=5.0
)

show_notification(
  title="Error",
  message="Failed to connect to server",
  type="error",
  duration=5.0
)
```

### File Dialogs

```json
// Add file dialog button
add_file_dialog(
  canvas_id="main",
  widget_id="file_dialog",
  button_label="Open File...",
  mode="open_file",
  title="Select a file",
  filters=["*.txt", "*.py", "*.json"]
)

// Show message dialog
show_message_dialog(
  title="Confirmation",
  message="Are you sure you want to delete this file?",
  type="warning"
)
```

### Layout Management

```json
// Set layout mode
set_layout_mode(mode="vertical")

// Set spacing
set_layout_spacing(spacing=10.0)
```

### Export/Import

```json
// Export canvas to JSON
export_canvas_json(
  canvas_id="dashboard",
  filepath="dashboard.json"
)

// Export canvas to Python code
export_canvas_python(
  canvas_id="dashboard",
  filepath="dashboard.py"
)

// Import canvas from JSON
import_canvas_json(filepath="dashboard.json")

// Generate code for canvas
generate_canvas_code(canvas_id="dashboard")
```

### Templates

```json
// Save canvas as template
save_template(
  name="dashboard_template",
  canvas_id="dashboard",
  description="Standard dashboard layout with charts"
)

// Load template
load_template(name="dashboard_template")

// List templates
list_templates()

// Delete template
delete_template(name="old_template")
```

## Available Themes

- `dark` - Default dark theme
- `light` - Light theme
- `cherry` - Cherry red theme
- `nord` - Nord color scheme
- `dracula` - Dracula theme
- `gruvbox` - Gruvbox theme
- `solarized_dark` - Solarized dark theme
- `monokai` - Monokai theme
- `material` - Material design theme

## Canvas Modes

- `standard` - Traditional window-based UI
- `docking` - Dockable window layout (recommended for dashboards)
- `multi_viewport` - Multiple windows support
- `fullscreen` - Immersive full-screen mode
- `overlay` - Transparent overlay mode

## Tips for LLMs

1. **Always create a canvas first** before adding widgets
2. **Use appropriate canvas modes**: `docking` for dashboards, `standard` for simple UIs
3. **Apply themes early** for consistent styling
4. **Use positions** to layout widgets manually, or use layout managers
5. **Group related widgets** under collapsing headers or windows
6. **Add separators** between sections for visual clarity
7. **Use help markers** to provide tooltips
8. **Choose appropriate chart types** based on the data
9. **Set widget sizes** explicitly for buttons and inputs
10. **Use data binding** for reactive UIs

## Common Patterns

### Dashboard Pattern
```
1. Create docking canvas
2. Apply theme
3. Create main window
4. Add title and subtitle
5. Add collapsing headers for sections
6. Add progress bars, charts, and metrics
7. Add control panel with checkboxes and sliders
8. Add action buttons
9. Add status bar at bottom
```

### Form Pattern
```
1. Create standard canvas
2. Add header text
3. Add input fields
4. Add validation indicators
5. Add checkboxes for agreements
6. Add separator
7. Add submit button
8. Add help markers
```

### Visualization Pattern
```
1. Create large docking canvas
2. Add multiple chart widgets
3. Add legend/labels
4. Add data controls (sliders, dropdowns)
5. Add export buttons
6. Use tooltips for data points
```
