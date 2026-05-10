"""Comprehensive tests for basic widgets.

Tests cover all 13 basic widgets:
- ButtonWidget, SmallButtonWidget, ArrowButtonWidget, InvisibleButtonWidget
- TextWidget, TextColoredWidget, TextDisabledWidget, TextWrappedWidget
- BulletTextWidget, BulletWidget, LabelTextWidget
- InputTextWidget
- CheckboxWidget
"""

from champi_imgui.core.state import WidgetState
from champi_imgui.widgets.basic import (
    ArrowButtonWidget,
    BulletTextWidget,
    BulletWidget,
    ButtonWidget,
    CheckboxWidget,
    InputTextWidget,
    InvisibleButtonWidget,
    LabelTextWidget,
    SmallButtonWidget,
    TextColoredWidget,
    TextDisabledWidget,
    TextWidget,
    TextWrappedWidget,
)

# ==============================================================================
# ButtonWidget Tests
# ==============================================================================


def test_button_widget_creation():
    """Test ButtonWidget creation with default values."""
    widget = ButtonWidget("btn-1")

    assert widget.widget_id == "btn-1"
    assert isinstance(widget.state, WidgetState)
    assert widget.state.widget_type == "ButtonWidget"
    assert widget.state.properties["label"] == "Button"


def test_button_widget_with_label():
    """Test ButtonWidget with custom label."""
    widget = ButtonWidget("btn-2", label="Click Me")

    assert widget.state.properties["label"] == "Click Me"


def test_button_widget_with_size():
    """Test ButtonWidget with custom size."""
    widget = ButtonWidget("btn-3", label="Button", size=(150.0, 40.0))

    assert widget.state.properties["size"] == (150.0, 40.0)


def test_button_widget_visibility():
    """Test ButtonWidget visibility handling."""
    widget = ButtonWidget("btn-4")

    # Default visible
    assert widget.state.visible is True

    # Set invisible
    widget.set_visible(False)
    assert widget.state.visible is False


def test_button_widget_serialization():
    """Test ButtonWidget serialization."""
    widget = ButtonWidget("btn-5", label="Serialize", size=(100.0, 30.0))

    data = widget.serialize()

    assert data["widget_id"] == "btn-5"
    assert data["widget_type"] == "ButtonWidget"
    assert data["properties"]["label"] == "Serialize"
    assert data["properties"]["size"] == (100.0, 30.0)


# ==============================================================================
# SmallButtonWidget Tests
# ==============================================================================


def test_small_button_widget_creation():
    """Test SmallButtonWidget creation."""
    widget = SmallButtonWidget("small-btn-1")

    assert widget.widget_id == "small-btn-1"
    assert widget.state.widget_type == "SmallButtonWidget"
    assert widget.state.properties["label"] == "Button"


def test_small_button_widget_custom_label():
    """Test SmallButtonWidget with custom label."""
    widget = SmallButtonWidget("small-btn-2", label="Small")

    assert widget.state.properties["label"] == "Small"


# ==============================================================================
# ArrowButtonWidget Tests
# ==============================================================================


def test_arrow_button_widget_creation():
    """Test ArrowButtonWidget creation."""
    widget = ArrowButtonWidget("arrow-1")

    assert widget.widget_id == "arrow-1"
    assert widget.state.widget_type == "ArrowButtonWidget"
    assert widget.state.properties["direction"] == 0


def test_arrow_button_widget_with_direction():
    """Test ArrowButtonWidget with custom direction."""
    widget = ArrowButtonWidget("arrow-2", direction=1)

    assert widget.state.properties["direction"] == 1


# ==============================================================================
# InvisibleButtonWidget Tests
# ==============================================================================


def test_invisible_button_widget_creation():
    """Test InvisibleButtonWidget creation."""
    widget = InvisibleButtonWidget("invisible-1")

    assert widget.widget_id == "invisible-1"
    assert widget.state.widget_type == "InvisibleButtonWidget"
    assert widget.state.properties["size"] == (100.0, 30.0)


def test_invisible_button_widget_custom_size():
    """Test InvisibleButtonWidget with custom size."""
    widget = InvisibleButtonWidget("invisible-2", size=(200.0, 50.0))

    assert widget.state.properties["size"] == (200.0, 50.0)


def test_invisible_button_widget_with_flags():
    """Test InvisibleButtonWidget with flags."""
    widget = InvisibleButtonWidget("invisible-3", flags=1)

    assert widget.state.properties["flags"] == 1


# ==============================================================================
# TextWidget Tests
# ==============================================================================


def test_text_widget_creation():
    """Test TextWidget creation."""
    widget = TextWidget("text-1")

    assert widget.widget_id == "text-1"
    assert widget.state.widget_type == "TextWidget"
    assert widget.state.properties["text"] == ""


def test_text_widget_with_text():
    """Test TextWidget with text."""
    widget = TextWidget("text-2", text="Hello World")

    assert widget.state.properties["text"] == "Hello World"


def test_text_widget_update_text():
    """Test TextWidget text update."""
    widget = TextWidget("text-3", text="Initial")

    widget.update(text="Updated")
    assert widget.state.properties["text"] == "Updated"


# ==============================================================================
# TextColoredWidget Tests
# ==============================================================================


def test_text_colored_widget_creation():
    """Test TextColoredWidget creation."""
    widget = TextColoredWidget("colored-1")

    assert widget.widget_id == "colored-1"
    assert widget.state.widget_type == "TextColoredWidget"
    assert widget.state.properties["text"] == ""
    assert widget.state.properties["color"] == (1.0, 1.0, 1.0, 1.0)


def test_text_colored_widget_with_color():
    """Test TextColoredWidget with custom color."""
    widget = TextColoredWidget("colored-2", text="Red Text", color=(1.0, 0.0, 0.0, 1.0))

    assert widget.state.properties["text"] == "Red Text"
    assert widget.state.properties["color"] == (1.0, 0.0, 0.0, 1.0)


# ==============================================================================
# TextDisabledWidget Tests
# ==============================================================================


def test_text_disabled_widget_creation():
    """Test TextDisabledWidget creation."""
    widget = TextDisabledWidget("disabled-1")

    assert widget.widget_id == "disabled-1"
    assert widget.state.widget_type == "TextDisabledWidget"
    assert widget.state.properties["text"] == ""


def test_text_disabled_widget_with_text():
    """Test TextDisabledWidget with text."""
    widget = TextDisabledWidget("disabled-2", text="Disabled")

    assert widget.state.properties["text"] == "Disabled"


# ==============================================================================
# TextWrappedWidget Tests
# ==============================================================================


def test_text_wrapped_widget_creation():
    """Test TextWrappedWidget creation."""
    widget = TextWrappedWidget("wrapped-1")

    assert widget.widget_id == "wrapped-1"
    assert widget.state.widget_type == "TextWrappedWidget"
    assert widget.state.properties["text"] == ""


def test_text_wrapped_widget_with_text():
    """Test TextWrappedWidget with long text."""
    long_text = "This is a very long text that should wrap to multiple lines."
    widget = TextWrappedWidget("wrapped-2", text=long_text)

    assert widget.state.properties["text"] == long_text


# ==============================================================================
# BulletTextWidget Tests
# ==============================================================================


def test_bullet_text_widget_creation():
    """Test BulletTextWidget creation."""
    widget = BulletTextWidget("bullet-text-1")

    assert widget.widget_id == "bullet-text-1"
    assert widget.state.widget_type == "BulletTextWidget"
    assert widget.state.properties["text"] == ""


def test_bullet_text_widget_with_text():
    """Test BulletTextWidget with text."""
    widget = BulletTextWidget("bullet-text-2", text="Bullet point")

    assert widget.state.properties["text"] == "Bullet point"


# ==============================================================================
# BulletWidget Tests
# ==============================================================================


def test_bullet_widget_creation():
    """Test BulletWidget creation."""
    widget = BulletWidget("bullet-1")

    assert widget.widget_id == "bullet-1"
    assert widget.state.widget_type == "BulletWidget"


def test_bullet_widget_serialization():
    """Test BulletWidget serialization."""
    widget = BulletWidget("bullet-2")

    data = widget.serialize()
    assert data["widget_id"] == "bullet-2"
    assert data["widget_type"] == "BulletWidget"


# ==============================================================================
# LabelTextWidget Tests
# ==============================================================================


def test_label_text_widget_creation():
    """Test LabelTextWidget creation."""
    widget = LabelTextWidget("label-1")

    assert widget.widget_id == "label-1"
    assert widget.state.widget_type == "LabelTextWidget"
    assert widget.state.properties["label"] == "Label"
    assert widget.state.properties["text"] == ""


def test_label_text_widget_with_values():
    """Test LabelTextWidget with label and text."""
    widget = LabelTextWidget("label-2", label="Name", text="John Doe")

    assert widget.state.properties["label"] == "Name"
    assert widget.state.properties["text"] == "John Doe"


# ==============================================================================
# InputTextWidget Tests
# ==============================================================================


def test_input_text_widget_creation():
    """Test InputTextWidget creation."""
    widget = InputTextWidget("input-1")

    assert widget.widget_id == "input-1"
    assert widget.state.widget_type == "InputTextWidget"
    assert widget.state.properties["label"] == "Input"
    assert widget.state.properties["value"] == ""
    assert widget._value == ""


def test_input_text_widget_with_value():
    """Test InputTextWidget with initial value."""
    widget = InputTextWidget("input-2", label="Name", value="Initial")

    assert widget.state.properties["label"] == "Name"
    assert widget.state.properties["value"] == "Initial"
    assert widget._value == "Initial"


def test_input_text_widget_get_value():
    """Test InputTextWidget get_value method."""
    widget = InputTextWidget("input-3", value="Test")

    assert widget.get_value() == "Test"


def test_input_text_widget_set_value():
    """Test InputTextWidget set_value method."""
    widget = InputTextWidget("input-4", value="Initial")

    widget.set_value("Updated")
    assert widget.get_value() == "Updated"
    assert widget.state.properties["value"] == "Updated"


def test_input_text_widget_with_hint():
    """Test InputTextWidget with hint."""
    widget = InputTextWidget("input-5", label="Email", hint="user@example.com")

    assert widget.state.properties["hint"] == "user@example.com"


def test_input_text_widget_multiline():
    """Test InputTextWidget in multiline mode."""
    widget = InputTextWidget(
        "input-6", label="Description", multiline=True, size=(300.0, 100.0)
    )

    assert widget.state.properties["multiline"] is True
    assert widget.state.properties["size"] == (300.0, 100.0)


# ==============================================================================
# CheckboxWidget Tests
# ==============================================================================


def test_checkbox_widget_creation():
    """Test CheckboxWidget creation."""
    widget = CheckboxWidget("check-1")

    assert widget.widget_id == "check-1"
    assert widget.state.widget_type == "CheckboxWidget"
    assert widget.state.properties["label"] == "Checkbox"
    assert widget.state.properties["checked"] is False
    assert widget._checked is False


def test_checkbox_widget_with_checked():
    """Test CheckboxWidget with initial checked state."""
    widget = CheckboxWidget("check-2", label="Accept", checked=True)

    assert widget.state.properties["label"] == "Accept"
    assert widget.state.properties["checked"] is True
    assert widget._checked is True


def test_checkbox_widget_get_checked():
    """Test CheckboxWidget get_checked method."""
    widget = CheckboxWidget("check-3", checked=True)

    assert widget.get_checked() is True


def test_checkbox_widget_set_checked():
    """Test CheckboxWidget set_checked method."""
    widget = CheckboxWidget("check-4", checked=False)

    widget.set_checked(True)
    assert widget.get_checked() is True
    assert widget.state.properties["checked"] is True

    widget.set_checked(False)
    assert widget.get_checked() is False
    assert widget.state.properties["checked"] is False


# ==============================================================================
# Edge Cases and Coverage
# ==============================================================================


def test_widget_visibility_affects_render():
    """Test that invisible widgets respect visibility flag."""
    button = ButtonWidget("vis-test-1")
    text = TextWidget("vis-test-2", text="Hidden")
    checkbox = CheckboxWidget("vis-test-3")

    # All widgets start visible
    assert button.state.visible is True
    assert text.state.visible is True
    assert checkbox.state.visible is True

    # Set invisible
    button.set_visible(False)
    text.set_visible(False)
    checkbox.set_visible(False)

    assert button.state.visible is False
    assert text.state.visible is False
    assert checkbox.state.visible is False


def test_widget_property_updates():
    """Test that widget property updates work correctly."""
    button = ButtonWidget("update-1", label="Initial")

    button.update(label="Updated", color="blue")
    assert button.state.properties["label"] == "Updated"
    assert button.state.properties["color"] == "blue"


def test_all_widgets_have_state():
    """Test that all widgets have proper state."""
    widgets = [
        ButtonWidget("w1"),
        SmallButtonWidget("w2"),
        ArrowButtonWidget("w3"),
        InvisibleButtonWidget("w4"),
        TextWidget("w5"),
        TextColoredWidget("w6"),
        TextDisabledWidget("w7"),
        TextWrappedWidget("w8"),
        BulletTextWidget("w9"),
        BulletWidget("w10"),
        LabelTextWidget("w11"),
        InputTextWidget("w12"),
        CheckboxWidget("w13"),
    ]

    for widget in widgets:
        assert isinstance(widget.state, WidgetState)
        assert widget.state.widget_id is not None
        assert widget.state.widget_type is not None
