"""Render tests for input widgets using mocks.

These tests verify render() method behavior by mocking imgui calls.
They ensure render methods handle visibility, call correct ImGui functions,
and trigger callbacks appropriately.
"""

from unittest.mock import patch

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
# InputIntWidget Render Tests
# ==============================================================================


@patch("champi_imgui.widgets.input.imgui")
def test_input_int_widget_render(mock_imgui):
    """Test InputIntWidget render method."""
    mock_imgui.input_int.return_value = (False, 42)
    widget = InputIntWidget("int-1", value=42)

    result = widget.render()

    assert result == 42
    mock_imgui.input_int.assert_called_once()


@patch("champi_imgui.widgets.input.imgui")
def test_input_int_widget_render_invisible(mock_imgui):
    """Test InputIntWidget render when invisible."""
    widget = InputIntWidget("int-2", value=10)
    widget.set_visible(False)

    result = widget.render()

    assert result == 10
    mock_imgui.input_int.assert_not_called()


@patch("champi_imgui.widgets.input.imgui")
def test_input_int_widget_value_changed(mock_imgui):
    """Test InputIntWidget triggers callback on value change."""
    mock_imgui.input_int.return_value = (True, 100)
    widget = InputIntWidget("int-3", value=50)

    callback_values = []

    def on_change(value):
        callback_values.append(value)

    widget.register_callback("on_change", on_change)
    result = widget.render()

    assert result == 100
    assert widget.state.properties["value"] == 100
    assert callback_values == [100]


# ==============================================================================
# InputFloatWidget Render Tests
# ==============================================================================


@patch("champi_imgui.widgets.input.imgui")
def test_input_float_widget_render(mock_imgui):
    """Test InputFloatWidget render method."""
    mock_imgui.input_float.return_value = (False, 3.14)
    widget = InputFloatWidget("float-1", value=3.14)

    result = widget.render()

    assert result == 3.14
    mock_imgui.input_float.assert_called_once()


@patch("champi_imgui.widgets.input.imgui")
def test_input_float_widget_render_invisible(mock_imgui):
    """Test InputFloatWidget render when invisible."""
    widget = InputFloatWidget("float-2", value=2.5)
    widget.set_visible(False)

    result = widget.render()

    assert result == 2.5
    mock_imgui.input_float.assert_not_called()


@patch("champi_imgui.widgets.input.imgui")
def test_input_float_widget_value_changed(mock_imgui):
    """Test InputFloatWidget triggers callback on value change."""
    mock_imgui.input_float.return_value = (True, 5.5)
    widget = InputFloatWidget("float-3", value=1.0)

    callback_values = []

    def on_change(value):
        callback_values.append(value)

    widget.register_callback("on_change", on_change)
    result = widget.render()

    assert result == 5.5
    assert callback_values == [5.5]


# ==============================================================================
# InputDoubleWidget Render Tests
# ==============================================================================


@patch("champi_imgui.widgets.input.imgui")
def test_input_double_widget_render(mock_imgui):
    """Test InputDoubleWidget render method."""
    mock_imgui.input_double.return_value = (False, 3.141592653589793)
    widget = InputDoubleWidget("double-1", value=3.141592653589793)

    result = widget.render()

    assert result == 3.141592653589793
    mock_imgui.input_double.assert_called_once()


@patch("champi_imgui.widgets.input.imgui")
def test_input_double_widget_render_invisible(mock_imgui):
    """Test InputDoubleWidget render when invisible."""
    widget = InputDoubleWidget("double-2", value=1.0)
    widget.set_visible(False)

    result = widget.render()

    assert result == 1.0
    mock_imgui.input_double.assert_not_called()


# ==============================================================================
# InputScalarWidget Render Tests
# ==============================================================================


@patch("champi_imgui.widgets.input.imgui")
def test_input_scalar_widget_render(mock_imgui):
    """Test InputScalarWidget render method."""
    mock_imgui.input_float.return_value = (False, 42.0)
    widget = InputScalarWidget("scalar-1", value=42.0)

    result = widget.render()

    assert result == 42.0
    mock_imgui.input_float.assert_called_once()


@patch("champi_imgui.widgets.input.imgui")
def test_input_scalar_widget_render_invisible(mock_imgui):
    """Test InputScalarWidget render when invisible."""
    widget = InputScalarWidget("scalar-2", value=10.0)
    widget.set_visible(False)

    result = widget.render()

    assert result == 10.0
    mock_imgui.input_float.assert_not_called()


# ==============================================================================
# RadioButtonWidget Render Tests
# ==============================================================================


@patch("champi_imgui.widgets.input.imgui")
def test_radio_button_widget_render(mock_imgui):
    """Test RadioButtonWidget render method."""
    mock_imgui.radio_button.return_value = False
    widget = RadioButtonWidget("radio-1", label="Option")

    result = widget.render()

    assert result is False
    mock_imgui.radio_button.assert_called_once_with("Option", False)


@patch("champi_imgui.widgets.input.imgui")
def test_radio_button_widget_render_invisible(mock_imgui):
    """Test RadioButtonWidget render when invisible."""
    widget = RadioButtonWidget("radio-2")
    widget.set_visible(False)

    result = widget.render()

    assert result is False
    mock_imgui.radio_button.assert_not_called()


@patch("champi_imgui.widgets.input.imgui")
def test_radio_button_widget_clicked(mock_imgui):
    """Test RadioButtonWidget triggers callback on click."""
    mock_imgui.radio_button.return_value = True
    widget = RadioButtonWidget("radio-3", active=False)

    callback_states = []

    def on_click(active):
        callback_states.append(active)

    widget.register_callback("on_click", on_click)
    result = widget.render()

    assert result is True
    assert widget._active is True
    assert callback_states == [True]


# ==============================================================================
# ComboWidget Render Tests
# ==============================================================================


@patch("champi_imgui.widgets.input.imgui")
def test_combo_widget_render(mock_imgui):
    """Test ComboWidget render method."""
    mock_imgui.combo.return_value = (False, 1)
    items = ["A", "B", "C"]
    widget = ComboWidget("combo-1", items=items, current_item=1)

    result = widget.render()

    assert result == 1
    mock_imgui.combo.assert_called_once()


@patch("champi_imgui.widgets.input.imgui")
def test_combo_widget_render_invisible(mock_imgui):
    """Test ComboWidget render when invisible."""
    widget = ComboWidget("combo-2", items=["A", "B"], current_item=0)
    widget.set_visible(False)

    result = widget.render()

    assert result == 0
    mock_imgui.combo.assert_not_called()


@patch("champi_imgui.widgets.input.imgui")
def test_combo_widget_render_empty_items(mock_imgui):
    """Test ComboWidget render with empty items."""
    widget = ComboWidget("combo-3", items=[])

    result = widget.render()

    assert result == 0
    mock_imgui.combo.assert_not_called()


@patch("champi_imgui.widgets.input.imgui")
def test_combo_widget_selection_changed(mock_imgui):
    """Test ComboWidget triggers callback on selection change."""
    mock_imgui.combo.return_value = (True, 2)
    items = ["Red", "Green", "Blue"]
    widget = ComboWidget("combo-4", items=items, current_item=0)

    callback_data = []

    def on_change(index, value):
        callback_data.append((index, value))

    widget.register_callback("on_change", on_change)
    result = widget.render()

    assert result == 2
    assert callback_data == [(2, "Blue")]


# ==============================================================================
# ListBoxWidget Render Tests
# ==============================================================================


@patch("champi_imgui.widgets.input.imgui")
def test_listbox_widget_render(mock_imgui):
    """Test ListBoxWidget render method."""
    mock_imgui.list_box.return_value = (False, 2)
    items = ["Item 1", "Item 2", "Item 3"]
    widget = ListBoxWidget("list-1", items=items, current_item=2)

    result = widget.render()

    assert result == 2
    mock_imgui.list_box.assert_called_once()


@patch("champi_imgui.widgets.input.imgui")
def test_listbox_widget_render_invisible(mock_imgui):
    """Test ListBoxWidget render when invisible."""
    widget = ListBoxWidget("list-2", items=["A"], current_item=0)
    widget.set_visible(False)

    result = widget.render()

    assert result == 0
    mock_imgui.list_box.assert_not_called()


@patch("champi_imgui.widgets.input.imgui")
def test_listbox_widget_render_empty_items(mock_imgui):
    """Test ListBoxWidget render with empty items."""
    widget = ListBoxWidget("list-3", items=[])

    result = widget.render()

    assert result == 0
    mock_imgui.list_box.assert_not_called()


@patch("champi_imgui.widgets.input.imgui")
def test_listbox_widget_selection_changed(mock_imgui):
    """Test ListBoxWidget triggers callback on selection change."""
    mock_imgui.list_box.return_value = (True, 1)
    items = ["Apple", "Banana", "Cherry"]
    widget = ListBoxWidget("list-4", items=items, current_item=0)

    callback_data = []

    def on_change(index, value):
        callback_data.append((index, value))

    widget.register_callback("on_change", on_change)
    result = widget.render()

    assert result == 1
    assert callback_data == [(1, "Banana")]


# ==============================================================================
# SelectableWidget Render Tests
# ==============================================================================


@patch("champi_imgui.widgets.input.imgui")
def test_selectable_widget_render(mock_imgui):
    """Test SelectableWidget render method."""
    mock_imgui.selectable.return_value = (False, False)
    widget = SelectableWidget("sel-1", label="Item")

    result = widget.render()

    assert result is False
    mock_imgui.selectable.assert_called_once()


@patch("champi_imgui.widgets.input.imgui")
def test_selectable_widget_render_invisible(mock_imgui):
    """Test SelectableWidget render when invisible."""
    widget = SelectableWidget("sel-2", selected=True)
    widget.set_visible(False)

    result = widget.render()

    assert result is True
    mock_imgui.selectable.assert_not_called()


@patch("champi_imgui.widgets.input.imgui")
def test_selectable_widget_render_with_size(mock_imgui):
    """Test SelectableWidget render with size."""
    mock_imgui.selectable.return_value = (False, False)
    widget = SelectableWidget("sel-3", size=(200.0, 30.0))

    widget.render()

    mock_imgui.selectable.assert_called_once()


@patch("champi_imgui.widgets.input.imgui")
def test_selectable_widget_clicked(mock_imgui):
    """Test SelectableWidget triggers callback on click."""
    mock_imgui.selectable.return_value = (True, True)
    widget = SelectableWidget("sel-4", selected=False)

    callback_states = []

    def on_click(selected):
        callback_states.append(selected)

    widget.register_callback("on_click", on_click)
    result = widget.render()

    assert result is True
    assert callback_states == [True]


# ==============================================================================
# CheckboxFlagsWidget Render Tests
# ==============================================================================


@patch("champi_imgui.widgets.input.imgui")
def test_checkbox_flags_widget_render(mock_imgui):
    """Test CheckboxFlagsWidget render method."""
    mock_imgui.checkbox_flags.return_value = (False, 5)
    widget = CheckboxFlagsWidget("flags-1", flags=5, flags_value=2)

    result = widget.render()

    assert result == 5
    mock_imgui.checkbox_flags.assert_called_once_with("Checkbox Flags", 5, 2)


@patch("champi_imgui.widgets.input.imgui")
def test_checkbox_flags_widget_render_invisible(mock_imgui):
    """Test CheckboxFlagsWidget render when invisible."""
    widget = CheckboxFlagsWidget("flags-2", flags=3)
    widget.set_visible(False)

    result = widget.render()

    assert result == 3
    mock_imgui.checkbox_flags.assert_not_called()


@patch("champi_imgui.widgets.input.imgui")
def test_checkbox_flags_widget_changed(mock_imgui):
    """Test CheckboxFlagsWidget triggers callback on change."""
    mock_imgui.checkbox_flags.return_value = (True, 7)
    widget = CheckboxFlagsWidget("flags-3", flags=5, flags_value=2)

    callback_values = []

    def on_change(flags):
        callback_values.append(flags)

    widget.register_callback("on_change", on_change)
    result = widget.render()

    assert result == 7
    assert callback_values == [7]
