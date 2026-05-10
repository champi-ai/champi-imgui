"""Comprehensive tests for color widgets.

Tests cover all 5 color widgets:
- ColorEdit3Widget, ColorEdit4Widget
- ColorPicker3Widget, ColorPickerWidget
- ColorButtonWidget
"""

from champi_imgui.core.state import WidgetState
from champi_imgui.widgets.color import (
    ColorButtonWidget,
    ColorEdit3Widget,
    ColorEdit4Widget,
    ColorPicker3Widget,
    ColorPickerWidget,
)

# ==============================================================================
# ColorEdit3Widget Tests
# ==============================================================================


def test_color_edit3_widget_creation():
    """Test ColorEdit3Widget creation with default values."""
    widget = ColorEdit3Widget("color3-1")

    assert widget.widget_id == "color3-1"
    assert isinstance(widget.state, WidgetState)
    assert widget.state.widget_type == "ColorEdit3Widget"
    assert widget.state.properties["label"] == "Color"
    assert widget.state.properties["color"] == (1.0, 1.0, 1.0)
    assert widget._color == [1.0, 1.0, 1.0]


def test_color_edit3_widget_with_color():
    """Test ColorEdit3Widget with custom color."""
    widget = ColorEdit3Widget("color3-2", label="RGB", color=(0.5, 0.25, 0.75), flags=1)

    assert widget.state.properties["label"] == "RGB"
    assert widget.state.properties["color"] == (0.5, 0.25, 0.75)
    assert widget.state.properties["flags"] == 1
    assert widget._color == [0.5, 0.25, 0.75]


def test_color_edit3_widget_get_color():
    """Test ColorEdit3Widget get_color method."""
    widget = ColorEdit3Widget("color3-3", color=(0.1, 0.2, 0.3))

    assert widget.get_color() == (0.1, 0.2, 0.3)


def test_color_edit3_widget_set_color():
    """Test ColorEdit3Widget set_color method."""
    widget = ColorEdit3Widget("color3-4")

    widget.set_color((0.9, 0.8, 0.7))
    assert widget.get_color() == (0.9, 0.8, 0.7)
    assert widget.state.properties["color"] == (0.9, 0.8, 0.7)


# ==============================================================================
# ColorEdit4Widget Tests
# ==============================================================================


def test_color_edit4_widget_creation():
    """Test ColorEdit4Widget creation with default values."""
    widget = ColorEdit4Widget("color4-1")

    assert widget.widget_id == "color4-1"
    assert widget.state.widget_type == "ColorEdit4Widget"
    assert widget.state.properties["label"] == "Color"
    assert widget.state.properties["color"] == (1.0, 1.0, 1.0, 1.0)
    assert widget._color == [1.0, 1.0, 1.0, 1.0]


def test_color_edit4_widget_with_color():
    """Test ColorEdit4Widget with custom color."""
    widget = ColorEdit4Widget(
        "color4-2", label="RGBA", color=(0.5, 0.25, 0.75, 0.5), flags=2
    )

    assert widget.state.properties["label"] == "RGBA"
    assert widget.state.properties["color"] == (0.5, 0.25, 0.75, 0.5)
    assert widget.state.properties["flags"] == 2
    assert widget._color == [0.5, 0.25, 0.75, 0.5]


def test_color_edit4_widget_get_color():
    """Test ColorEdit4Widget get_color method."""
    widget = ColorEdit4Widget("color4-3", color=(0.1, 0.2, 0.3, 0.4))

    assert widget.get_color() == (0.1, 0.2, 0.3, 0.4)


def test_color_edit4_widget_set_color():
    """Test ColorEdit4Widget set_color method."""
    widget = ColorEdit4Widget("color4-4")

    widget.set_color((0.9, 0.8, 0.7, 0.6))
    assert widget.get_color() == (0.9, 0.8, 0.7, 0.6)
    assert widget.state.properties["color"] == (0.9, 0.8, 0.7, 0.6)


# ==============================================================================
# ColorPicker3Widget Tests
# ==============================================================================


def test_color_picker3_widget_creation():
    """Test ColorPicker3Widget creation."""
    widget = ColorPicker3Widget("picker3-1")

    assert widget.widget_id == "picker3-1"
    assert widget.state.widget_type == "ColorPicker3Widget"
    assert widget.state.properties["label"] == "Color Picker"
    assert widget.state.properties["color"] == (1.0, 1.0, 1.0)
    assert widget._color == [1.0, 1.0, 1.0]


def test_color_picker3_widget_with_color():
    """Test ColorPicker3Widget with custom color."""
    widget = ColorPicker3Widget(
        "picker3-2", label="Pick RGB", color=(0.2, 0.4, 0.6), flags=4
    )

    assert widget.state.properties["label"] == "Pick RGB"
    assert widget.state.properties["color"] == (0.2, 0.4, 0.6)
    assert widget.state.properties["flags"] == 4


def test_color_picker3_widget_get_color():
    """Test ColorPicker3Widget get_color method."""
    widget = ColorPicker3Widget("picker3-3", color=(0.3, 0.3, 0.3))

    assert widget.get_color() == (0.3, 0.3, 0.3)


def test_color_picker3_widget_set_color():
    """Test ColorPicker3Widget set_color method."""
    widget = ColorPicker3Widget("picker3-4")

    widget.set_color((0.5, 0.5, 0.5))
    assert widget.get_color() == (0.5, 0.5, 0.5)
    assert widget.state.properties["color"] == (0.5, 0.5, 0.5)


# ==============================================================================
# ColorPickerWidget Tests
# ==============================================================================


def test_color_picker_widget_creation():
    """Test ColorPickerWidget creation."""
    widget = ColorPickerWidget("picker4-1")

    assert widget.widget_id == "picker4-1"
    assert widget.state.widget_type == "ColorPickerWidget"
    assert widget.state.properties["label"] == "Color Picker"
    assert widget.state.properties["color"] == (1.0, 1.0, 1.0, 1.0)
    assert widget._color == [1.0, 1.0, 1.0, 1.0]


def test_color_picker_widget_with_color():
    """Test ColorPickerWidget with custom color."""
    widget = ColorPickerWidget(
        "picker4-2", label="Pick RGBA", color=(0.2, 0.4, 0.6, 0.8), flags=8
    )

    assert widget.state.properties["label"] == "Pick RGBA"
    assert widget.state.properties["color"] == (0.2, 0.4, 0.6, 0.8)
    assert widget.state.properties["flags"] == 8


def test_color_picker_widget_with_ref_col():
    """Test ColorPickerWidget with reference color."""
    widget = ColorPickerWidget(
        "picker4-3", color=(0.5, 0.5, 0.5, 1.0), ref_col=[0.0, 0.0, 0.0, 1.0]
    )

    assert widget.state.properties["ref_col"] == [0.0, 0.0, 0.0, 1.0]


def test_color_picker_widget_get_color():
    """Test ColorPickerWidget get_color method."""
    widget = ColorPickerWidget("picker4-4", color=(0.3, 0.3, 0.3, 0.3))

    assert widget.get_color() == (0.3, 0.3, 0.3, 0.3)


def test_color_picker_widget_set_color():
    """Test ColorPickerWidget set_color method."""
    widget = ColorPickerWidget("picker4-5")

    widget.set_color((0.5, 0.5, 0.5, 0.5))
    assert widget.get_color() == (0.5, 0.5, 0.5, 0.5)
    assert widget.state.properties["color"] == (0.5, 0.5, 0.5, 0.5)


# ==============================================================================
# ColorButtonWidget Tests
# ==============================================================================


def test_color_button_widget_creation():
    """Test ColorButtonWidget creation."""
    widget = ColorButtonWidget("btn-color-1")

    assert widget.widget_id == "btn-color-1"
    assert widget.state.widget_type == "ColorButtonWidget"
    assert widget.state.properties["color"] == (1.0, 1.0, 1.0, 1.0)
    assert widget._color == [1.0, 1.0, 1.0, 1.0]


def test_color_button_widget_with_color():
    """Test ColorButtonWidget with custom color."""
    widget = ColorButtonWidget("btn-color-2", color=(0.8, 0.2, 0.2, 1.0), flags=16)

    assert widget.state.properties["color"] == (0.8, 0.2, 0.2, 1.0)
    assert widget.state.properties["flags"] == 16
    assert widget._color == [0.8, 0.2, 0.2, 1.0]


def test_color_button_widget_with_size():
    """Test ColorButtonWidget with custom size."""
    widget = ColorButtonWidget("btn-color-3", size=(50.0, 50.0))

    assert widget.state.properties["size"] == (50.0, 50.0)


def test_color_button_widget_get_color():
    """Test ColorButtonWidget get_color method."""
    widget = ColorButtonWidget("btn-color-4", color=(0.1, 0.2, 0.3, 0.4))

    assert widget.get_color() == (0.1, 0.2, 0.3, 0.4)


def test_color_button_widget_set_color():
    """Test ColorButtonWidget set_color method."""
    widget = ColorButtonWidget("btn-color-5")

    widget.set_color((0.9, 0.8, 0.7, 0.6))
    assert widget.get_color() == (0.9, 0.8, 0.7, 0.6)
    assert widget.state.properties["color"] == (0.9, 0.8, 0.7, 0.6)


# ==============================================================================
# Edge Cases and Coverage
# ==============================================================================


def test_widget_visibility_affects_render():
    """Test that invisible widgets respect visibility flag."""
    color_edit3 = ColorEdit3Widget("vis-1")
    color_edit4 = ColorEdit4Widget("vis-2")
    color_picker3 = ColorPicker3Widget("vis-3")
    color_picker4 = ColorPickerWidget("vis-4")
    color_button = ColorButtonWidget("vis-5")

    # Set invisible
    color_edit3.set_visible(False)
    color_edit4.set_visible(False)
    color_picker3.set_visible(False)
    color_picker4.set_visible(False)
    color_button.set_visible(False)

    assert color_edit3.state.visible is False
    assert color_edit4.state.visible is False
    assert color_picker3.state.visible is False
    assert color_picker4.state.visible is False
    assert color_button.state.visible is False


def test_all_color_widgets_have_state():
    """Test that all color widgets have proper state."""
    widgets = [
        ColorEdit3Widget("w1"),
        ColorEdit4Widget("w2"),
        ColorPicker3Widget("w3"),
        ColorPickerWidget("w4"),
        ColorButtonWidget("w5"),
    ]

    for widget in widgets:
        assert isinstance(widget.state, WidgetState)
        assert widget.state.widget_id is not None
        assert widget.state.widget_type is not None
