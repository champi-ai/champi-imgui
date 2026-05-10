"""
Interactive Dashboard Demo using Champi-Gen-UI.

This example creates a comprehensive dashboard with various widgets including:
- Text displays and headers
- Interactive controls (buttons, sliders, checkboxes)
- Data visualization (line charts, progress bars)
- Color customization
"""

from champi_gen_ui.core.canvas import CanvasManager
from champi_gen_ui.core.state import CanvasMode
from champi_gen_ui.themes.manager import ThemeManager
from champi_gen_ui.themes.presets import THEME_PRESETS
from champi_gen_ui.widgets.basic import (
    ButtonWidget,
    CheckboxWidget,
    ColorPickerWidget,
    InputTextWidget,
    TextWidget,
)
from champi_gen_ui.widgets.container import (
    CollapsingHeaderWidget,
    SeparatorWidget,
    WindowWidget,
)
from champi_gen_ui.widgets.display import (
    BulletTextWidget,
    HelpMarkerWidget,
    ProgressBarWidget,
    TextColoredWidget,
)
from champi_gen_ui.widgets.menu import (
    SelectableWidget,
    TreeNodeWidget,
)
from champi_gen_ui.widgets.plotting import BarChartWidget, LineChartWidget
from champi_gen_ui.widgets.slider import SliderFloatWidget, SliderIntWidget


def main():
    """Run the dashboard demo."""
    print("=" * 60)
    print("Champi-Gen-UI Dashboard Demo")
    print("=" * 60)

    # Create canvas manager and theme manager
    manager = CanvasManager()
    theme_manager = ThemeManager()

    # Register theme presets
    for _name, theme in THEME_PRESETS.items():
        theme_manager.register_theme(theme)

    # Apply a nice theme
    theme_manager.apply_theme_by_name("nord")

    # Create a docking canvas for flexible layout
    canvas = manager.create_canvas(
        canvas_id="dashboard",
        width=1280,
        height=800,
        mode=CanvasMode.DOCKING,
        title="Champi-Gen-UI - Interactive Dashboard Demo",
    )

    # Register all widget types
    registry = canvas.widget_registry
    registry.factory.register("button", ButtonWidget)
    registry.factory.register("text", TextWidget)
    registry.factory.register("input_text", InputTextWidget)
    registry.factory.register("checkbox", CheckboxWidget)
    registry.factory.register("slider_float", SliderFloatWidget)
    registry.factory.register("slider_int", SliderIntWidget)
    registry.factory.register("color_picker", ColorPickerWidget)

    # === MAIN WINDOW ===
    main_window = WindowWidget(
        "main_window", title="Dashboard Overview", closable=False
    )
    main_window.set_position(10, 30)
    canvas.add_widget(main_window)

    # Title Section
    title = registry.factory.create(
        "text",
        "title",
        text="Dashboard Analytics",
        color=(0.3, 0.7, 1.0, 1.0),
    )
    canvas.add_widget(title)

    # Subtitle
    subtitle = TextColoredWidget(
        "subtitle",
        text="Real-time monitoring and controls",
        color=(0.7, 0.7, 0.7, 1.0),
    )
    canvas.add_widget(subtitle)

    # Separator
    separator1 = SeparatorWidget("sep1")
    canvas.add_widget(separator1)

    # === STATISTICS SECTION ===
    stats_header = CollapsingHeaderWidget(
        "stats_header", label="Statistics", default_open=True
    )
    canvas.add_widget(stats_header)

    # Bullet points for stats
    stat1 = BulletTextWidget("stat1", text="Active Users: 1,234")
    canvas.add_widget(stat1)

    stat2 = BulletTextWidget("stat2", text="Server Uptime: 99.9%")
    canvas.add_widget(stat2)

    stat3 = BulletTextWidget("stat3", text="Response Time: 45ms")
    canvas.add_widget(stat3)

    # Help marker
    help_marker = HelpMarkerWidget(
        "help1",
        text="These statistics are updated in real-time from the server monitoring system.",
        marker="(?)",
    )
    canvas.add_widget(help_marker)

    # Separator
    separator2 = SeparatorWidget("sep2")
    canvas.add_widget(separator2)

    # === PERFORMANCE METRICS ===
    metrics_header = CollapsingHeaderWidget(
        "metrics_header", label="Performance Metrics", default_open=True
    )
    canvas.add_widget(metrics_header)

    # CPU Usage Progress Bar
    cpu_label = registry.factory.create(
        "text",
        "cpu_label",
        text="CPU Usage:",
    )
    canvas.add_widget(cpu_label)

    cpu_progress = ProgressBarWidget("cpu_progress", fraction=0.65, overlay="65%")
    canvas.add_widget(cpu_progress)

    # Memory Usage Progress Bar
    memory_label = registry.factory.create(
        "text",
        "memory_label",
        text="Memory Usage:",
    )
    canvas.add_widget(memory_label)

    memory_progress = ProgressBarWidget("memory_progress", fraction=0.42, overlay="42%")
    canvas.add_widget(memory_progress)

    # Disk Usage Progress Bar
    disk_label = registry.factory.create(
        "text",
        "disk_label",
        text="Disk Usage:",
    )
    canvas.add_widget(disk_label)

    disk_progress = ProgressBarWidget("disk_progress", fraction=0.78, overlay="78%")
    canvas.add_widget(disk_progress)

    # Separator
    separator3 = SeparatorWidget("sep3")
    canvas.add_widget(separator3)

    # === CONTROLS SECTION ===
    controls_header = CollapsingHeaderWidget(
        "controls_header", label="Control Panel", default_open=True
    )
    canvas.add_widget(controls_header)

    # Enable monitoring checkbox
    monitoring_check = registry.factory.create(
        "checkbox",
        "monitoring_check",
        label="Enable Real-time Monitoring",
        checked=True,
    )
    canvas.add_widget(monitoring_check)

    # Auto-refresh checkbox
    refresh_check = registry.factory.create(
        "checkbox",
        "refresh_check",
        label="Auto-refresh Dashboard",
        checked=True,
    )
    canvas.add_widget(refresh_check)

    # Refresh rate slider
    refresh_rate = registry.factory.create(
        "slider_int",
        "refresh_rate",
        label="Refresh Rate (seconds)",
        value=5,
        v_min=1,
        v_max=60,
    )
    canvas.add_widget(refresh_rate)

    # Alert threshold slider
    alert_threshold = registry.factory.create(
        "slider_float",
        "alert_threshold",
        label="Alert Threshold",
        value=0.85,
        v_min=0.0,
        v_max=1.0,
    )
    canvas.add_widget(alert_threshold)

    # Action buttons
    def on_refresh_click():
        print("Dashboard refreshed!")

    def on_export_click():
        print("Data exported!")

    def on_reset_click():
        print("Settings reset!")

    refresh_button = registry.factory.create(
        "button",
        "refresh_btn",
        label="Refresh Now",
        size=[120, 30],
    )
    refresh_button.register_callback("on_click", on_refresh_click)
    canvas.add_widget(refresh_button)

    export_button = registry.factory.create(
        "button",
        "export_btn",
        label="Export Data",
        size=[120, 30],
    )
    export_button.register_callback("on_click", on_export_click)
    canvas.add_widget(export_button)

    reset_button = registry.factory.create(
        "button",
        "reset_btn",
        label="Reset Settings",
        size=[120, 30],
    )
    reset_button.register_callback("on_click", on_reset_click)
    canvas.add_widget(reset_button)

    # === CHART WINDOW ===
    chart_window = WindowWidget(
        "chart_window", title="Performance Charts", closable=False
    )
    chart_window.set_position(450, 30)
    canvas.add_widget(chart_window)

    # Line chart for performance over time
    performance_data_x = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    performance_data_y = [45, 52, 48, 65, 58, 71, 68, 75, 72, 78, 82]

    line_chart = LineChartWidget(
        "line_chart",
        title="Response Time (ms)",
        x_data=performance_data_x,
        y_data=performance_data_y,
    )
    canvas.add_widget(line_chart)

    # Bar chart for resource comparison
    resource_labels = ["CPU", "Memory", "Disk", "Network"]
    resource_values = [65.0, 42.0, 78.0, 35.0]

    bar_chart = BarChartWidget(
        "bar_chart",
        title="Resource Utilization (%)",
        values=resource_values,
        labels=resource_labels,
    )
    canvas.add_widget(bar_chart)

    # === SETTINGS WINDOW ===
    settings_window = WindowWidget("settings_window", title="Settings", closable=True)
    settings_window.set_position(900, 30)
    canvas.add_widget(settings_window)

    # Theme selection
    theme_label = registry.factory.create(
        "text",
        "theme_label",
        text="Theme Selection:",
    )
    canvas.add_widget(theme_label)

    # Theme options as selectables
    theme_dark = SelectableWidget("theme_dark", label="Dark (default)", selected=False)
    canvas.add_widget(theme_dark)

    theme_light = SelectableWidget("theme_light", label="Light", selected=False)
    canvas.add_widget(theme_light)

    theme_nord = SelectableWidget("theme_nord", label="Nord (active)", selected=True)
    canvas.add_widget(theme_nord)

    theme_dracula = SelectableWidget("theme_dracula", label="Dracula", selected=False)
    canvas.add_widget(theme_dracula)

    # Color customization
    color_sep = SeparatorWidget("color_sep")
    canvas.add_widget(color_sep)

    accent_color = registry.factory.create(
        "color_picker",
        "accent_color",
        label="Accent Color",
        color=(0.3, 0.7, 1.0, 1.0),
    )
    canvas.add_widget(accent_color)

    # User settings tree
    tree_sep = SeparatorWidget("tree_sep")
    canvas.add_widget(tree_sep)

    user_settings = TreeNodeWidget(
        "user_settings", label="User Preferences", default_open=True
    )
    canvas.add_widget(user_settings)

    # Input for username
    username_input = registry.factory.create(
        "input_text",
        "username",
        label="Username",
        value="admin",
        hint="Enter username...",
    )
    canvas.add_widget(username_input)

    # Email input
    email_input = registry.factory.create(
        "input_text",
        "email",
        label="Email",
        value="admin@example.com",
        hint="Enter email...",
    )
    canvas.add_widget(email_input)

    # === STATUS BAR ===
    status_sep = SeparatorWidget("status_sep")
    canvas.add_widget(status_sep)

    status_text = TextColoredWidget(
        "status",
        text="Status: System running normally | Last updated: Just now",
        color=(0.3, 1.0, 0.3, 1.0),
    )
    canvas.add_widget(status_text)

    # Print summary
    print("\nCanvas created successfully!")
    print(f"  Canvas ID: {canvas.state.canvas_id}")
    print(f"  Mode: {canvas.state.mode.value}")
    print(f"  Size: {canvas.state.size[0]}x{canvas.state.size[1]}")
    print(f"  Widgets: {len(canvas.widget_registry.get_all())}")
    print("\nActive theme: Nord")
    print("\nDashboard Features:")
    print("  ✓ Real-time statistics")
    print("  ✓ Performance metrics with progress bars")
    print("  ✓ Interactive controls (checkboxes, sliders)")
    print("  ✓ Data visualization (line & bar charts)")
    print("  ✓ Theme customization")
    print("  ✓ Docking layout support")
    print("\nPress Ctrl+C to exit")
    print("=" * 60)

    # Run the canvas
    try:
        canvas.run()
    except KeyboardInterrupt:
        print("\nShutting down dashboard...")
        print("Goodbye!")


if __name__ == "__main__":
    main()
