"""Comprehensive tests for input widgets.

Tests cover all 9 input widgets:
- InputIntWidget, InputFloatWidget, InputDoubleWidget, InputScalarWidget
- RadioButtonWidget, ComboWidget, ListBoxWidget
- SelectableWidget, CheckboxFlagsWidget
"""

from champi_imgui.core.state import WidgetState
from champi_imgui.widgets.input import (
    CheckboxFlagsWidget,
    ComboWidget,
    InputDoubleWidget,
    InputFloatWidget,
    InputIntWidget,
    InputScalarWidget,
    ListBoxWidget,
    RadioButtonWidget,
    SelectableWidget,
)

# ==============================================================================
# InputIntWidget Tests
# ==============================================================================


def test_input_int_widget_creation():
    """Test InputIntWidget creation with default values."""
    widget = InputIntWidget("int-1")

    assert widget.widget_id == "int-1"
    assert isinstance(widget.state, WidgetState)
    assert widget.state.widget_type == "InputIntWidget"
    assert widget.state.properties["label"] == "Input Int"
    assert widget.state.properties["value"] == 0
    assert widget._value == 0


def test_input_int_widget_with_value():
    """Test InputIntWidget with custom value."""
    widget = InputIntWidget("int-2", label="Age", value=25, step=1, step_fast=10)

    assert widget.state.properties["label"] == "Age"
    assert widget.state.properties["value"] == 25
    assert widget.state.properties["step"] == 1
    assert widget.state.properties["step_fast"] == 10
    assert widget._value == 25


def test_input_int_widget_get_value():
    """Test InputIntWidget get_value method."""
    widget = InputIntWidget("int-3", value=100)

    assert widget.get_value() == 100


def test_input_int_widget_set_value():
    """Test InputIntWidget set_value method."""
    widget = InputIntWidget("int-4", value=0)

    widget.set_value(50)
    assert widget.get_value() == 50
    assert widget.state.properties["value"] == 50


# ==============================================================================
# InputFloatWidget Tests
# ==============================================================================


def test_input_float_widget_creation():
    """Test InputFloatWidget creation."""
    widget = InputFloatWidget("float-1")

    assert widget.widget_id == "float-1"
    assert widget.state.widget_type == "InputFloatWidget"
    assert widget.state.properties["value"] == 0.0
    assert widget._value == 0.0


def test_input_float_widget_with_value():
    """Test InputFloatWidget with custom value."""
    widget = InputFloatWidget(
        "float-2",
        label="Price",
        value=19.99,
        step=0.1,
        step_fast=1.0,
        format_str="%.2f",
    )

    assert widget.state.properties["label"] == "Price"
    assert widget.state.properties["value"] == 19.99
    assert widget.state.properties["step"] == 0.1
    assert widget.state.properties["step_fast"] == 1.0
    assert widget.state.properties["format"] == "%.2f"


def test_input_float_widget_get_set_value():
    """Test InputFloatWidget get/set value."""
    widget = InputFloatWidget("float-3", value=1.5)

    assert widget.get_value() == 1.5

    widget.set_value(2.5)
    assert widget.get_value() == 2.5
    assert widget.state.properties["value"] == 2.5


# ==============================================================================
# InputDoubleWidget Tests
# ==============================================================================


def test_input_double_widget_creation():
    """Test InputDoubleWidget creation."""
    widget = InputDoubleWidget("double-1")

    assert widget.widget_id == "double-1"
    assert widget.state.widget_type == "InputDoubleWidget"
    assert widget.state.properties["format"] == "%.6f"


def test_input_double_widget_with_value():
    """Test InputDoubleWidget with custom value."""
    widget = InputDoubleWidget(
        "double-2", label="Precision", value=3.141592653589793, format_str="%.10f"
    )

    assert widget.state.properties["label"] == "Precision"
    assert widget.state.properties["value"] == 3.141592653589793
    assert widget.state.properties["format"] == "%.10f"


def test_input_double_widget_get_set_value():
    """Test InputDoubleWidget get/set value."""
    widget = InputDoubleWidget("double-3", value=1.0)

    assert widget.get_value() == 1.0

    widget.set_value(2.71828)
    assert widget.get_value() == 2.71828


# ==============================================================================
# InputScalarWidget Tests
# ==============================================================================


def test_input_scalar_widget_creation():
    """Test InputScalarWidget creation."""
    widget = InputScalarWidget("scalar-1")

    assert widget.widget_id == "scalar-1"
    assert widget.state.widget_type == "InputScalarWidget"
    assert widget._value == 0.0


def test_input_scalar_widget_with_value():
    """Test InputScalarWidget with custom value."""
    widget = InputScalarWidget("scalar-2", label="Custom", value=42.0)

    assert widget.state.properties["label"] == "Custom"
    assert widget.state.properties["value"] == 42.0


def test_input_scalar_widget_get_value():
    """Test InputScalarWidget get_value."""
    widget = InputScalarWidget("scalar-3", value=123.45)

    assert widget.get_value() == 123.45


# ==============================================================================
# RadioButtonWidget Tests
# ==============================================================================


def test_radio_button_widget_creation():
    """Test RadioButtonWidget creation."""
    widget = RadioButtonWidget("radio-1")

    assert widget.widget_id == "radio-1"
    assert widget.state.widget_type == "RadioButtonWidget"
    assert widget.state.properties["label"] == "Radio"
    assert widget.state.properties["active"] is False
    assert widget._active is False


def test_radio_button_widget_with_active():
    """Test RadioButtonWidget with active state."""
    widget = RadioButtonWidget("radio-2", label="Option A", active=True)

    assert widget.state.properties["label"] == "Option A"
    assert widget.state.properties["active"] is True
    assert widget._active is True


def test_radio_button_widget_is_active():
    """Test RadioButtonWidget is_active method."""
    widget = RadioButtonWidget("radio-3", active=True)

    assert widget.is_active() is True


def test_radio_button_widget_set_active():
    """Test RadioButtonWidget set_active method."""
    widget = RadioButtonWidget("radio-4", active=False)

    widget.set_active(True)
    assert widget.is_active() is True
    assert widget.state.properties["active"] is True


# ==============================================================================
# ComboWidget Tests
# ==============================================================================


def test_combo_widget_creation():
    """Test ComboWidget creation."""
    widget = ComboWidget("combo-1")

    assert widget.widget_id == "combo-1"
    assert widget.state.widget_type == "ComboWidget"
    assert widget.state.properties["label"] == "Combo"
    assert widget.state.properties["items"] == []
    assert widget.state.properties["current_item"] == 0


def test_combo_widget_with_items():
    """Test ComboWidget with items."""
    items = ["Option 1", "Option 2", "Option 3"]
    widget = ComboWidget("combo-2", label="Select", items=items, current_item=1)

    assert widget.state.properties["label"] == "Select"
    assert widget.state.properties["items"] == items
    assert widget.state.properties["current_item"] == 1
    assert widget._current_item == 1


def test_combo_widget_get_current_item():
    """Test ComboWidget get_current_item."""
    widget = ComboWidget("combo-3", items=["A", "B", "C"], current_item=2)

    assert widget.get_current_item() == 2


def test_combo_widget_get_current_value():
    """Test ComboWidget get_current_value."""
    items = ["Red", "Green", "Blue"]
    widget = ComboWidget("combo-4", items=items, current_item=1)

    assert widget.get_current_value() == "Green"


def test_combo_widget_get_current_value_empty():
    """Test ComboWidget get_current_value with empty items."""
    widget = ComboWidget("combo-5", items=[])

    assert widget.get_current_value() is None


def test_combo_widget_set_items():
    """Test ComboWidget set_items method."""
    widget = ComboWidget("combo-6", items=["A", "B"])

    widget.set_items(["X", "Y", "Z"])
    assert widget.state.properties["items"] == ["X", "Y", "Z"]


# ==============================================================================
# ListBoxWidget Tests
# ==============================================================================


def test_listbox_widget_creation():
    """Test ListBoxWidget creation."""
    widget = ListBoxWidget("list-1")

    assert widget.widget_id == "list-1"
    assert widget.state.widget_type == "ListBoxWidget"
    assert widget.state.properties["label"] == "ListBox"
    assert widget.state.properties["items"] == []


def test_listbox_widget_with_items():
    """Test ListBoxWidget with items."""
    items = ["Item 1", "Item 2", "Item 3"]
    widget = ListBoxWidget("list-2", label="Choose", items=items, current_item=2)

    assert widget.state.properties["label"] == "Choose"
    assert widget.state.properties["items"] == items
    assert widget.state.properties["current_item"] == 2


def test_listbox_widget_get_current_item():
    """Test ListBoxWidget get_current_item."""
    widget = ListBoxWidget("list-3", items=["A", "B", "C"], current_item=1)

    assert widget.get_current_item() == 1


def test_listbox_widget_get_current_value():
    """Test ListBoxWidget get_current_value."""
    items = ["Apple", "Banana", "Cherry"]
    widget = ListBoxWidget("list-4", items=items, current_item=2)

    assert widget.get_current_value() == "Cherry"


def test_listbox_widget_height_in_items():
    """Test ListBoxWidget height_in_items property."""
    widget = ListBoxWidget("list-5", items=["A", "B"], height_in_items=5)

    assert widget.state.properties["height_in_items"] == 5


# ==============================================================================
# SelectableWidget Tests
# ==============================================================================


def test_selectable_widget_creation():
    """Test SelectableWidget creation."""
    widget = SelectableWidget("sel-1")

    assert widget.widget_id == "sel-1"
    assert widget.state.widget_type == "SelectableWidget"
    assert widget.state.properties["label"] == "Selectable"
    assert widget.state.properties["selected"] is False
    assert widget._selected is False


def test_selectable_widget_with_selected():
    """Test SelectableWidget with selected state."""
    widget = SelectableWidget("sel-2", label="Item", selected=True)

    assert widget.state.properties["label"] == "Item"
    assert widget.state.properties["selected"] is True
    assert widget._selected is True


def test_selectable_widget_is_selected():
    """Test SelectableWidget is_selected method."""
    widget = SelectableWidget("sel-3", selected=True)

    assert widget.is_selected() is True


def test_selectable_widget_set_selected():
    """Test SelectableWidget set_selected method."""
    widget = SelectableWidget("sel-4", selected=False)

    widget.set_selected(True)
    assert widget.is_selected() is True
    assert widget.state.properties["selected"] is True


def test_selectable_widget_with_size():
    """Test SelectableWidget with size."""
    widget = SelectableWidget("sel-5", size=(200.0, 30.0))

    assert widget.state.properties["size"] == (200.0, 30.0)


# ==============================================================================
# CheckboxFlagsWidget Tests
# ==============================================================================


def test_checkbox_flags_widget_creation():
    """Test CheckboxFlagsWidget creation."""
    widget = CheckboxFlagsWidget("flags-1")

    assert widget.widget_id == "flags-1"
    assert widget.state.widget_type == "CheckboxFlagsWidget"
    assert widget.state.properties["label"] == "Checkbox Flags"
    assert widget.state.properties["flags"] == 0
    assert widget._flags == 0


def test_checkbox_flags_widget_with_flags():
    """Test CheckboxFlagsWidget with custom flags."""
    widget = CheckboxFlagsWidget("flags-2", label="Options", flags=5, flags_value=2)

    assert widget.state.properties["label"] == "Options"
    assert widget.state.properties["flags"] == 5
    assert widget.state.properties["flags_value"] == 2


def test_checkbox_flags_widget_get_flags():
    """Test CheckboxFlagsWidget get_flags method."""
    widget = CheckboxFlagsWidget("flags-3", flags=7)

    assert widget.get_flags() == 7


def test_checkbox_flags_widget_set_flags():
    """Test CheckboxFlagsWidget set_flags method."""
    widget = CheckboxFlagsWidget("flags-4", flags=0)

    widget.set_flags(15)
    assert widget.get_flags() == 15
    assert widget.state.properties["flags"] == 15


# ==============================================================================
# Edge Cases and Coverage
# ==============================================================================


def test_widget_visibility_affects_render():
    """Test that invisible widgets respect visibility flag."""
    int_input = InputIntWidget("vis-1")
    combo = ComboWidget("vis-2")
    selectable = SelectableWidget("vis-3")

    # Set invisible
    int_input.set_visible(False)
    combo.set_visible(False)
    selectable.set_visible(False)

    assert int_input.state.visible is False
    assert combo.state.visible is False
    assert selectable.state.visible is False


def test_all_input_widgets_have_state():
    """Test that all input widgets have proper state."""
    widgets = [
        InputIntWidget("w1"),
        InputFloatWidget("w2"),
        InputDoubleWidget("w3"),
        InputScalarWidget("w4"),
        RadioButtonWidget("w5"),
        ComboWidget("w6"),
        ListBoxWidget("w7"),
        SelectableWidget("w8"),
        CheckboxFlagsWidget("w9"),
    ]

    for widget in widgets:
        assert isinstance(widget.state, WidgetState)
        assert widget.state.widget_id is not None
        assert widget.state.widget_type is not None
