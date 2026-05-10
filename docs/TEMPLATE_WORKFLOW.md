# Template Workflow Guide

## Overview

This guide explains how to save and reuse UI templates in champi-gen-ui. Templates allow you to save complete UI designs and load them later for reuse or modification.

## When to Save Templates

**Templates should only be saved when the author is done creating their UI.**

Save a template when:
- ✅ All widgets have been added and positioned
- ✅ Layout is finalized
- ✅ Styling and theming is complete
- ✅ The UI is tested and working
- ✅ You want to reuse this design later

**Do NOT save templates:**
- ❌ During active development/iteration
- ❌ When still experimenting with layouts
- ❌ Before testing the UI
- ❌ For temporary/throwaway designs

## Workflow

### 1. Create Your UI

Use MCP tools to build your interface:

```python
# Create canvas
create_canvas(
    canvas_id="my_dashboard",
    width=1280,
    height=720,
    title="Analytics Dashboard"
)

# Add widgets
add_text(
    canvas_id="my_dashboard",
    widget_id="title",
    text="Sales Analytics",
    position=[10, 10]
)

add_button(
    canvas_id="my_dashboard",
    widget_id="refresh_btn",
    label="Refresh Data",
    position=[10, 50]
)

add_line_chart(
    canvas_id="my_dashboard",
    widget_id="sales_chart",
    title="Monthly Sales",
    x_data=[1, 2, 3, 4, 5],
    y_data=[100, 150, 120, 180, 200]
)

# ... add more widgets
```

### 2. Test Your UI

Verify everything works:
- All widgets appear correctly
- Layout looks good
- Interactions work as expected
- No errors in console

### 3. Save as Template

**Only when you're completely done**, save the template:

```python
save_template(
    name="analytics_dashboard",
    canvas_id="my_dashboard",
    description="Complete analytics dashboard with sales charts, filters, and data tables"
)
```

**Result:**
```json
{
  "success": true,
  "data": {
    "message": "Saved template: analytics_dashboard"
  }
}
```

The template is saved to: `./templates/analytics_dashboard.json`

### 4. Load Template Later

When you need to reuse the design:

```python
load_template(name="analytics_dashboard")
```

**Result:**
```json
{
  "success": true,
  "data": {
    "canvas_id": "my_dashboard",
    "widgets": [...],
    "mode": "standard",
    ...
  }
}
```

## Template Management

### List All Templates

```python
list_templates()
```

**Response:**
```json
{
  "success": true,
  "data": {
    "templates": [
      {
        "name": "analytics_dashboard",
        "description": "Complete analytics dashboard...",
        "created": "2025-10-19T02:30:00Z",
        "widget_count": 15
      },
      {
        "name": "login_form",
        "description": "User login form with validation",
        "created": "2025-10-18T14:20:00Z",
        "widget_count": 5
      }
    ]
  }
}
```

### Delete Template

```python
delete_template(name="old_template")
```

**Response:**
```json
{
  "success": true,
  "data": {
    "message": "Deleted template: old_template"
  }
}
```

## Best Practices

### 1. Use Descriptive Names

**Good:**
```python
save_template("ecommerce_product_grid", canvas_id, "Product grid with filters and pagination")
save_template("user_settings_panel", canvas_id, "Settings panel with tabs and form inputs")
save_template("analytics_realtime_dashboard", canvas_id, "Real-time analytics with live charts")
```

**Bad:**
```python
save_template("test", canvas_id, "")
save_template("ui1", canvas_id, "some stuff")
save_template("template", canvas_id, "template")
```

### 2. Add Meaningful Descriptions

Include:
- Purpose of the UI
- Key features/widgets
- Use cases
- Any special configurations

**Example:**
```python
save_template(
    name="customer_support_dashboard",
    canvas_id="support_ui",
    description="""
    Customer support dashboard with:
    - Ticket list with status filters
    - Real-time chat widget
    - Customer info panel
    - Response templates dropdown
    - Analytics charts (response time, satisfaction)
    Use for customer service teams handling support tickets.
    """
)
```

### 3. Organize by Category

Use naming conventions:
```python
# Dashboards
save_template("dashboard_analytics", ...)
save_template("dashboard_admin", ...)
save_template("dashboard_sales", ...)

# Forms
save_template("form_login", ...)
save_template("form_registration", ...)
save_template("form_checkout", ...)

# Components
save_template("component_navbar", ...)
save_template("component_sidebar", ...)
save_template("component_footer", ...)
```

### 4. Version Your Templates

For significant changes:
```python
save_template("dashboard_v1", ...)
save_template("dashboard_v2", ...)
save_template("dashboard_v3", ...)
```

Or use dates:
```python
save_template("dashboard_2025_10_19", ...)
```

### 5. Document Widget Dependencies

In the description, note any special requirements:
```python
save_template(
    name="advanced_charting_panel",
    canvas_id="charts",
    description="""
    Advanced charting panel with multiple chart types.

    Dependencies:
    - Requires ImPlot extension
    - Uses custom color theme 'dark_charts'
    - Expects data binding to 'analytics.data' path

    Widgets: 5 line charts, 2 bar charts, 1 heatmap
    """
)
```

## Template File Structure

Templates are saved as JSON files in `./templates/`:

```json
{
  "template_name": "analytics_dashboard",
  "description": "Complete analytics dashboard with sales charts",
  "canvas_id": "my_dashboard",
  "size": [1280, 720],
  "mode": "standard",
  "title": "Analytics Dashboard",
  "theme": "dark",
  "widgets": [
    {
      "widget_id": "title",
      "type": "text",
      "properties": {
        "text": "Sales Analytics",
        "color": [0.2, 0.8, 0.2, 1.0]
      },
      "position": [10, 10],
      "visible": true
    },
    {
      "widget_id": "sales_chart",
      "type": "line_chart",
      "properties": {
        "title": "Monthly Sales",
        "x_data": [1, 2, 3, 4, 5],
        "y_data": [100, 150, 120, 180, 200]
      },
      "position": [10, 100],
      "visible": true
    }
  ]
}
```

## Advanced Usage

### Programmatic Template Creation

```python
# Create base template
create_canvas(canvas_id="base", title="Base Template")
add_text(canvas_id="base", widget_id="header", text="Header")
add_separator(canvas_id="base", widget_id="sep1")
save_template("base_layout", "base", "Reusable base layout")

# Load and customize
loaded = load_template("base_layout")
add_button(canvas_id="base", widget_id="action", label="Action")
save_template("base_with_action", "base", "Base layout with action button")
```

### Template Composition

```python
# Save individual components
save_template("navbar", "nav_canvas", "Navigation bar")
save_template("sidebar", "side_canvas", "Sidebar menu")
save_template("footer", "foot_canvas", "Footer")

# Combine them
load_template("navbar")
load_template("sidebar")
load_template("footer")
# Position and arrange
save_template("complete_layout", "main", "Full page layout")
```

## Error Handling

### Template Already Exists

```python
save_template("existing", canvas_id, "description")
# Overwrites the existing template
```

### Canvas Not Found

```python
save_template("new", "nonexistent_canvas", "")
# Returns: {"success": false, "error": "Canvas nonexistent_canvas not found"}
```

### Invalid Template Name

```python
load_template("does_not_exist")
# Returns: {"success": false, "error": "Template not found: does_not_exist"}
```

## Summary

**Key Principles:**

1. **Build first, save last** - Only save when UI is complete
2. **Be descriptive** - Use clear names and detailed descriptions
3. **Organize systematically** - Use naming conventions
4. **Document dependencies** - Note special requirements
5. **Test before saving** - Ensure everything works

**Workflow:**
1. Create UI with MCP tools
2. Test and refine
3. Save template when done
4. Reuse later with load_template

Templates enable you to build a library of reusable UI patterns that can be quickly deployed and customized for different applications.
