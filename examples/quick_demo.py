"""
Quick UI Demo - A simple interactive UI to demonstrate Champi-Gen-UI
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
from champi_gen_ui.widgets.display import (
    BulletTextWidget,
    ProgressBarWidget,
    TextColoredWidget,
)
from champi_gen_ui.widgets.plotting import BarChartWidget, LineChartWidget
from champi_gen_ui.widgets.slider import SliderFloatWidget, SliderIntWidget


def main():
    """Run a quick demo UI."""
    print("\n" + "=" * 70)
    print("🎨 CHAMPI-GEN-UI - Interactive Demo")
    print("=" * 70)

    # Create managers
    manager = CanvasManager()
    theme_manager = ThemeManager()

    # Register themes
    for _name, theme in THEME_PRESETS.items():
        theme_manager.register_theme(theme)

    # Apply Dracula theme
    try:
        theme_manager.apply_theme_by_name("Dracula")
        print("✓ Applied Dracula theme")
    except Exception as e:
        print(f"⚠ Using default theme: {e}")

    # Create canvas
    print("✓ Creating canvas...")
    canvas = manager.create_canvas(
        canvas_id="quick_demo",
        width=900,
        height=700,
        mode=CanvasMode.STANDARD,
        title="🎨 Champi-Gen-UI Quick Demo",
    )

    # Register widget types
    registry = canvas.widget_registry
    registry.factory.register("button", ButtonWidget)
    registry.factory.register("text", TextWidget)
    registry.factory.register("input_text", InputTextWidget)
    registry.factory.register("checkbox", CheckboxWidget)
    registry.factory.register("slider_float", SliderFloatWidget)
    registry.factory.register("slider_int", SliderIntWidget)
    registry.factory.register("color_picker", ColorPickerWidget)
    print("✓ Registered widget types")

    # === UI CREATION ===
    print("✓ Building UI...")

    # Title
    title = TextColoredWidget(
        "title",
        text="🎨 Welcome to Champi-Gen-UI!",
        color=(0.5, 0.8, 1.0, 1.0),
    )
    canvas.add_widget(title)

    # Description
    desc = registry.factory.create(
        "text",
        "desc",
        text="A powerful UI generation system using ImGui and Python",
    )
    canvas.add_widget(desc)

    # === INTERACTIVE SECTION ===
    section1 = TextColoredWidget(
        "section1",
        text="📝 Interactive Controls",
        color=(1.0, 0.8, 0.2, 1.0),
    )
    canvas.add_widget(section1)

    # Name input
    name_input = registry.factory.create(
        "input_text",
        "name_input",
        label="Your Name",
        value="",
        hint="Enter your name...",
    )
    canvas.add_widget(name_input)

    # Email input
    email_input = registry.factory.create(
        "input_text",
        "email_input",
        label="Email",
        value="",
        hint="your@email.com",
    )
    canvas.add_widget(email_input)

    # Checkbox
    checkbox = registry.factory.create(
        "checkbox",
        "subscribe_check",
        label="Subscribe to newsletter",
        checked=True,
    )
    canvas.add_widget(checkbox)

    # === SLIDERS ===
    section2 = TextColoredWidget(
        "section2",
        text="🎚️ Sliders & Controls",
        color=(0.2, 1.0, 0.6, 1.0),
    )
    canvas.add_widget(section2)

    # Volume slider
    volume_slider = registry.factory.create(
        "slider_float",
        "volume",
        label="Volume",
        value=0.75,
        v_min=0.0,
        v_max=1.0,
    )
    canvas.add_widget(volume_slider)

    # Brightness slider
    brightness_slider = registry.factory.create(
        "slider_int",
        "brightness",
        label="Brightness",
        value=85,
        v_min=0,
        v_max=100,
    )
    canvas.add_widget(brightness_slider)

    # Color picker
    color_picker = registry.factory.create(
        "color_picker",
        "theme_color",
        label="Theme Color",
        color=(0.5, 0.3, 0.9, 1.0),
    )
    canvas.add_widget(color_picker)

    # === PROGRESS BARS ===
    section3 = TextColoredWidget(
        "section3",
        text="📊 Progress & Metrics",
        color=(1.0, 0.5, 0.8, 1.0),
    )
    canvas.add_widget(section3)

    # CPU usage
    cpu_label = registry.factory.create("text", "cpu_label", text="CPU Usage:")
    canvas.add_widget(cpu_label)

    cpu_progress = ProgressBarWidget("cpu_bar", fraction=0.67, overlay="67%")
    canvas.add_widget(cpu_progress)

    # Memory usage
    mem_label = registry.factory.create("text", "mem_label", text="Memory Usage:")
    canvas.add_widget(mem_label)

    mem_progress = ProgressBarWidget("mem_bar", fraction=0.43, overlay="43%")
    canvas.add_widget(mem_progress)

    # === DATA VISUALIZATION ===
    section4 = TextColoredWidget(
        "section4",
        text="📈 Data Visualization",
        color=(0.3, 0.9, 1.0, 1.0),
    )
    canvas.add_widget(section4)

    # Line chart
    line_chart = LineChartWidget(
        "performance_chart",
        title="Performance Over Time",
        x_data=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        y_data=[20, 35, 28, 45, 52, 48, 65, 58, 72, 68],
    )
    canvas.add_widget(line_chart)

    # Bar chart
    bar_chart = BarChartWidget(
        "resources_chart",
        title="Resource Usage",
        values=[67.0, 43.0, 89.0, 52.0],
        labels=["CPU", "Memory", "Disk", "Network"],
    )
    canvas.add_widget(bar_chart)

    # === FEATURES LIST ===
    section5 = TextColoredWidget(
        "section5",
        text="✨ Features",
        color=(1.0, 1.0, 0.3, 1.0),
    )
    canvas.add_widget(section5)

    features = [
        "200+ MCP Tools for UI generation",
        "150+ Widget types from ImGui",
        "Multiple themes (Dracula, Nord, Material, etc.)",
        "Data binding and animations",
        "Export to JSON or Python code",
    ]

    for i, feature in enumerate(features):
        bullet = BulletTextWidget(f"feature_{i}", text=feature)
        canvas.add_widget(bullet)

    # === BUTTONS ===
    def on_click():
        print("🎉 Button clicked!")

    def on_refresh():
        print("🔄 Refreshing data...")

    def on_export():
        print("💾 Exporting UI...")

    click_btn = registry.factory.create(
        "button",
        "click_btn",
        label="Click Me! 🎯",
        size=[150, 40],
    )
    click_btn.register_callback("on_click", on_click)
    canvas.add_widget(click_btn)

    refresh_btn = registry.factory.create(
        "button",
        "refresh_btn",
        label="Refresh Data 🔄",
        size=[150, 40],
    )
    refresh_btn.register_callback("on_click", on_refresh)
    canvas.add_widget(refresh_btn)

    export_btn = registry.factory.create(
        "button",
        "export_btn",
        label="Export UI 💾",
        size=[150, 40],
    )
    export_btn.register_callback("on_click", on_export)
    canvas.add_widget(export_btn)

    # Status
    status = TextColoredWidget(
        "status",
        text="✓ All systems operational | Press Ctrl+C to exit",
        color=(0.3, 1.0, 0.3, 1.0),
    )
    canvas.add_widget(status)

    # Print summary
    print(f"\n{'─' * 70}")
    print("🎨 UI Created Successfully!")
    print(f"{'─' * 70}")
    print(f"  Canvas ID: {canvas.state.canvas_id}")
    print(f"  Mode: {canvas.state.mode.value}")
    print(f"  Size: {canvas.state.size[0]}x{canvas.state.size[1]}")
    print(f"  Widgets: {len(canvas.widget_registry.get_all())}")
    print(f"{'─' * 70}")
    print("\n🎮 Interact with the UI:")
    print("  • Fill in the name and email fields")
    print("  • Adjust the volume and brightness sliders")
    print("  • Pick your favorite color")
    print("  • Click the buttons to see console output")
    print("  • View the live charts and progress bars")
    print(f"\n{'─' * 70}")
    print("Press Ctrl+C to exit")
    print(f"{'─' * 70}\n")

    # Run the canvas
    try:
        canvas.run()
    except KeyboardInterrupt:
        print("\n\n" + "=" * 70)
        print("👋 Thank you for trying Champi-Gen-UI!")
        print("=" * 70)


if __name__ == "__main__":
    main()
