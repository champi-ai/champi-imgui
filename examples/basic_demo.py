"""
Basic demo showing how to use champi-gen-ui.

This example creates a simple UI with various widgets.
"""

from champi_gen_ui.core.canvas import CanvasManager
from champi_gen_ui.core.state import CanvasMode
from champi_gen_ui.widgets.basic import (
    ButtonWidget,
    CheckboxWidget,
    ColorPickerWidget,
    InputTextWidget,
    TextWidget,
)
from champi_gen_ui.widgets.slider import SliderFloatWidget


def main():
    """Run the basic demo."""
    # Create canvas manager
    manager = CanvasManager()

    # Create a canvas
    canvas = manager.create_canvas(
        canvas_id="demo",
        width=600,
        height=400,
        mode=CanvasMode.STANDARD,
        title="Champi-Gen-UI Basic Demo",
    )

    # Register widget types
    registry = canvas.widget_registry
    registry.factory.register("button", ButtonWidget)
    registry.factory.register("text", TextWidget)
    registry.factory.register("input_text", InputTextWidget)
    registry.factory.register("checkbox", CheckboxWidget)
    registry.factory.register("slider_float", SliderFloatWidget)
    registry.factory.register("color_picker", ColorPickerWidget)

    # Add widgets
    # Title text
    title = registry.factory.create(
        "text",
        "title",
        text="Welcome to Champi-Gen-UI!",
        color=(0.2, 0.8, 0.2, 1.0),
    )
    title.set_position(10, 10)
    canvas.add_widget(title)

    # Description text
    desc = registry.factory.create(
        "text",
        "desc",
        text="This is a demo of the basic widgets.",
    )
    desc.set_position(10, 40)
    canvas.add_widget(desc)

    # Button with callback
    def on_button_click():
        print("Button clicked!")

    button = registry.factory.create(
        "button",
        "btn1",
        label="Click Me!",
        size=[120, 30],
    )
    button.set_position(10, 70)
    button.register_callback("on_click", on_button_click)
    canvas.add_widget(button)

    # Input text
    input_field = registry.factory.create(
        "input_text",
        "input1",
        label="Name",
        value="",
        hint="Enter your name...",
    )
    input_field.set_position(10, 110)
    canvas.add_widget(input_field)

    # Checkbox
    checkbox = registry.factory.create(
        "checkbox",
        "check1",
        label="Enable feature",
        checked=False,
    )
    checkbox.set_position(10, 140)
    canvas.add_widget(checkbox)

    # Slider
    slider = registry.factory.create(
        "slider_float",
        "slider1",
        label="Volume",
        value=0.5,
        v_min=0.0,
        v_max=1.0,
    )
    slider.set_position(10, 170)
    canvas.add_widget(slider)

    # Color picker
    color_picker = registry.factory.create(
        "color_picker",
        "color1",
        label="Theme Color",
        color=(0.2, 0.5, 0.8, 1.0),
    )
    color_picker.set_position(10, 200)
    canvas.add_widget(color_picker)

    # Status text at bottom
    status = registry.factory.create(
        "text",
        "status",
        text="Status: Ready",
        color=(0.7, 0.7, 0.7, 1.0),
    )
    status.set_position(10, 350)
    canvas.add_widget(status)

    print(f"Canvas created with {len(canvas.widget_registry.get_all())} widgets")
    print("Press Ctrl+C to exit")

    # Run the canvas
    canvas.run()


if __name__ == "__main__":
    main()
