"""
Test script to verify MCP-driven UI rendering works correctly.

This simulates what an LLM would do via MCP tools to create a UI.
"""

import time

from champi_gen_ui.core.canvas import CanvasManager
from champi_gen_ui.core.state import CanvasMode
from champi_gen_ui.widgets.basic import (
    ButtonWidget,
    CheckboxWidget,
    InputTextWidget,
    TextWidget,
)
from champi_gen_ui.widgets.slider import SliderFloatWidget
from loguru import logger

# Create canvas manager
canvas_manager = CanvasManager()


def test_mcp_rendering():
    """Test that MCP tools create visible UI."""
    logger.info("Starting MCP rendering test...")

    # Step 1: Create a canvas (should auto-start)
    logger.info("Creating canvas...")
    canvas = canvas_manager.create_canvas(
        canvas_id="test_canvas",
        width=800,
        height=600,
        mode=CanvasMode.STANDARD,
        title="MCP Test UI",
        auto_start=True,
    )

    # Register widget types
    registry = canvas.widget_registry
    registry.factory.register("button", ButtonWidget)
    registry.factory.register("text", TextWidget)
    registry.factory.register("input_text", InputTextWidget)
    registry.factory.register("checkbox", CheckboxWidget)
    registry.factory.register("slider_float", SliderFloatWidget)

    logger.info(f"Canvas created and running: {canvas._running}")

    # Give the canvas time to initialize
    time.sleep(0.5)

    # Step 2: Add widgets directly to canvas
    logger.info("Adding widgets...")

    # Title
    title = registry.factory.create(
        "text",
        "title",
        text="MCP Rendering Test",
        color=(0.2, 0.8, 0.2, 1.0),
    )
    title.set_position(10, 10)
    canvas.add_widget(title)

    # Description
    desc = registry.factory.create(
        "text",
        "desc",
        text="This UI was created programmatically!",
    )
    desc.set_position(10, 40)
    canvas.add_widget(desc)

    # Button
    button = registry.factory.create(
        "button",
        "btn1",
        label="Click Me!",
        size=[120, 30],
    )
    button.set_position(10, 70)
    canvas.add_widget(button)

    # Input field
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

    logger.info("Widgets added! UI should be visible now.")

    # Get canvas state
    canvas = canvas_manager.get_canvas("test_canvas")
    if canvas:
        logger.info(f"Canvas running: {canvas._running}")
        logger.info(f"Widget count: {len(canvas.widget_registry.get_all())}")
        logger.info(f"Widgets: {list(canvas.widget_registry.get_all().keys())}")

    # Keep test running for 30 seconds to view the UI
    logger.info("Test will run for 30 seconds. Check that the UI window is visible!")
    logger.info("The window should show:")
    logger.info("  - Title text in green")
    logger.info("  - Description text")
    logger.info("  - Button labeled 'Click Me!'")
    logger.info("  - Input field with hint text")
    logger.info("  - Checkbox")
    logger.info("  - Slider")

    try:
        time.sleep(30)
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")

    # Cleanup
    logger.info("Stopping canvas...")
    canvas_manager.stop_all()
    logger.info("Test complete!")


if __name__ == "__main__":
    test_mcp_rendering()
