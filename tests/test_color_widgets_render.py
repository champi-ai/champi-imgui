"""Render tests for color widgets using mocks.

These tests verify render() method behavior by mocking imgui calls.
They ensure render methods handle visibility, call correct ImGui functions,
and trigger callbacks appropriately.
"""

from unittest.mock import MagicMock, patch

from champi_imgui.widgets.color import (
    ColorButtonWidget,
    ColorEdit3Widget,
    ColorEdit4Widget,
    ColorPicker3Widget,
    ColorPickerWidget,
)

# ==============================================================================
# ColorEdit3Widget Render Tests
# ==============================================================================


@patch("champi_imgui.widgets.color.imgui")
def test_color_edit3_widget_render(mock_imgui):
    """Test ColorEdit3Widget render method."""
    mock_imgui.color_edit3.return_value = (False, [0.5, 0.5, 0.5])
    widget = ColorEdit3Widget("color3-1", color=(0.5, 0.5, 0.5))

    result = widget.render()

    assert result == (0.5, 0.5, 0.5)
    mock_imgui.color_edit3.assert_called_once()


@patch("champi_imgui.widgets.color.imgui")
def test_color_edit3_widget_render_invisible(mock_imgui):
    """Test ColorEdit3Widget render when invisible."""
    widget = ColorEdit3Widget("color3-2", color=(0.1, 0.2, 0.3))
    widget.set_visible(False)

    result = widget.render()

    assert result == (0.1, 0.2, 0.3)
    mock_imgui.color_edit3.assert_not_called()


@patch("champi_imgui.widgets.color.imgui")
def test_color_edit3_widget_color_changed(mock_imgui):
    """Test ColorEdit3Widget triggers callback on color change."""
    mock_imgui.color_edit3.return_value = (True, [0.9, 0.8, 0.7])
    widget = ColorEdit3Widget("color3-3", color=(0.5, 0.5, 0.5))

    callback_colors = []

    def on_change(color):
        callback_colors.append(color)

    widget.register_callback("on_change", on_change)
    result = widget.render()

    assert result == (0.9, 0.8, 0.7)
    assert widget.state.properties["color"] == (0.9, 0.8, 0.7)
    assert callback_colors == [(0.9, 0.8, 0.7)]


# ==============================================================================
# ColorEdit4Widget Render Tests
# ==============================================================================


@patch("champi_imgui.widgets.color.imgui")
def test_color_edit4_widget_render(mock_imgui):
    """Test ColorEdit4Widget render method."""
    mock_imgui.color_edit4.return_value = (False, [0.5, 0.5, 0.5, 1.0])
    widget = ColorEdit4Widget("color4-1", color=(0.5, 0.5, 0.5, 1.0))

    result = widget.render()

    assert result == (0.5, 0.5, 0.5, 1.0)
    mock_imgui.color_edit4.assert_called_once()


@patch("champi_imgui.widgets.color.imgui")
def test_color_edit4_widget_render_invisible(mock_imgui):
    """Test ColorEdit4Widget render when invisible."""
    widget = ColorEdit4Widget("color4-2", color=(0.1, 0.2, 0.3, 0.4))
    widget.set_visible(False)

    result = widget.render()

    assert result == (0.1, 0.2, 0.3, 0.4)
    mock_imgui.color_edit4.assert_not_called()


@patch("champi_imgui.widgets.color.imgui")
def test_color_edit4_widget_color_changed(mock_imgui):
    """Test ColorEdit4Widget triggers callback on color change."""
    mock_imgui.color_edit4.return_value = (True, [0.9, 0.8, 0.7, 0.6])
    widget = ColorEdit4Widget("color4-3", color=(0.5, 0.5, 0.5, 1.0))

    callback_colors = []

    def on_change(color):
        callback_colors.append(color)

    widget.register_callback("on_change", on_change)
    result = widget.render()

    assert result == (0.9, 0.8, 0.7, 0.6)
    assert callback_colors == [(0.9, 0.8, 0.7, 0.6)]


# ==============================================================================
# ColorPicker3Widget Render Tests
# ==============================================================================


@patch("champi_imgui.widgets.color.imgui")
def test_color_picker3_widget_render(mock_imgui):
    """Test ColorPicker3Widget render method."""
    mock_imgui.color_picker3.return_value = (False, [0.5, 0.5, 0.5])
    widget = ColorPicker3Widget("picker3-1", color=(0.5, 0.5, 0.5))

    result = widget.render()

    assert result == (0.5, 0.5, 0.5)
    mock_imgui.color_picker3.assert_called_once()


@patch("champi_imgui.widgets.color.imgui")
def test_color_picker3_widget_render_invisible(mock_imgui):
    """Test ColorPicker3Widget render when invisible."""
    widget = ColorPicker3Widget("picker3-2", color=(0.2, 0.4, 0.6))
    widget.set_visible(False)

    result = widget.render()

    assert result == (0.2, 0.4, 0.6)
    mock_imgui.color_picker3.assert_not_called()


@patch("champi_imgui.widgets.color.imgui")
def test_color_picker3_widget_color_changed(mock_imgui):
    """Test ColorPicker3Widget triggers callback on color change."""
    mock_imgui.color_picker3.return_value = (True, [0.1, 0.3, 0.5])
    widget = ColorPicker3Widget("picker3-3", color=(0.5, 0.5, 0.5))

    callback_colors = []

    def on_change(color):
        callback_colors.append(color)

    widget.register_callback("on_change", on_change)
    result = widget.render()

    assert result == (0.1, 0.3, 0.5)
    assert callback_colors == [(0.1, 0.3, 0.5)]


# ==============================================================================
# ColorPickerWidget Render Tests
# ==============================================================================


@patch("champi_imgui.widgets.color.imgui")
def test_color_picker_widget_render(mock_imgui):
    """Test ColorPickerWidget render method."""
    # Mock ImVec4 return value
    mock_color = MagicMock()
    mock_color.x = 0.5
    mock_color.y = 0.5
    mock_color.z = 0.5
    mock_color.w = 1.0
    mock_imgui.color_picker4.return_value = (False, mock_color)
    widget = ColorPickerWidget("picker4-1", color=(0.5, 0.5, 0.5, 1.0))

    result = widget.render()

    assert result == (0.5, 0.5, 0.5, 1.0)
    mock_imgui.color_picker4.assert_called_once()


@patch("champi_imgui.widgets.color.imgui")
def test_color_picker_widget_render_invisible(mock_imgui):
    """Test ColorPickerWidget render when invisible."""
    widget = ColorPickerWidget("picker4-2", color=(0.2, 0.4, 0.6, 0.8))
    widget.set_visible(False)

    result = widget.render()

    assert result == (0.2, 0.4, 0.6, 0.8)
    mock_imgui.color_picker4.assert_not_called()


@patch("champi_imgui.widgets.color.imgui")
def test_color_picker_widget_color_changed(mock_imgui):
    """Test ColorPickerWidget triggers callback on color change."""
    # Mock ImVec4 return value
    mock_color = MagicMock()
    mock_color.x = 0.1
    mock_color.y = 0.3
    mock_color.z = 0.5
    mock_color.w = 0.7
    mock_imgui.color_picker4.return_value = (True, mock_color)
    widget = ColorPickerWidget("picker4-3", color=(0.5, 0.5, 0.5, 1.0))

    callback_colors = []

    def on_change(color):
        callback_colors.append(color)

    widget.register_callback("on_change", on_change)
    result = widget.render()

    assert result == (0.1, 0.3, 0.5, 0.7)
    assert callback_colors == [(0.1, 0.3, 0.5, 0.7)]


@patch("champi_imgui.widgets.color.imgui")
def test_color_picker_widget_with_ref_col(mock_imgui):
    """Test ColorPickerWidget render with reference color."""
    mock_color = MagicMock()
    mock_color.x = 0.5
    mock_color.y = 0.5
    mock_color.z = 0.5
    mock_color.w = 1.0
    mock_imgui.color_picker4.return_value = (False, mock_color)
    widget = ColorPickerWidget(
        "picker4-4", color=(0.5, 0.5, 0.5, 1.0), ref_col=[0.0, 0.0, 0.0, 1.0]
    )

    widget.render()

    # Verify ref_col was passed to imgui.color_picker4
    call_args = mock_imgui.color_picker4.call_args
    assert call_args is not None
    assert len(call_args[0]) == 4  # label, color, flags, ref_col


# ==============================================================================
# ColorButtonWidget Render Tests
# ==============================================================================


@patch("champi_imgui.widgets.color.imgui")
def test_color_button_widget_render(mock_imgui):
    """Test ColorButtonWidget render method."""
    mock_imgui.color_button.return_value = False
    mock_imgui.ImVec4 = MagicMock(return_value="mock_vec4")
    widget = ColorButtonWidget("btn-color-1", color=(0.8, 0.2, 0.2, 1.0))

    result = widget.render()

    assert result is False
    mock_imgui.color_button.assert_called_once()


@patch("champi_imgui.widgets.color.imgui")
def test_color_button_widget_render_invisible(mock_imgui):
    """Test ColorButtonWidget render when invisible."""
    widget = ColorButtonWidget("btn-color-2", color=(0.5, 0.5, 0.5, 1.0))
    widget.set_visible(False)

    result = widget.render()

    assert result is False
    mock_imgui.color_button.assert_not_called()


@patch("champi_imgui.widgets.color.imgui")
def test_color_button_widget_clicked(mock_imgui):
    """Test ColorButtonWidget triggers callback on click."""
    mock_imgui.color_button.return_value = True
    mock_imgui.ImVec4 = MagicMock(return_value="mock_vec4")
    widget = ColorButtonWidget("btn-color-3", color=(0.9, 0.1, 0.1, 1.0))

    callback_colors = []

    def on_click(color):
        callback_colors.append(color)

    widget.register_callback("on_click", on_click)
    result = widget.render()

    assert result is True
    assert callback_colors == [(0.9, 0.1, 0.1, 1.0)]


@patch("champi_imgui.widgets.color.imgui")
def test_color_button_widget_with_size(mock_imgui):
    """Test ColorButtonWidget render with custom size."""
    mock_imgui.color_button.return_value = False
    mock_imgui.ImVec4 = MagicMock(return_value="mock_vec4")
    mock_imgui.ImVec2 = MagicMock(return_value="mock_vec2")
    widget = ColorButtonWidget(
        "btn-color-4", color=(0.5, 0.5, 0.5, 1.0), size=(50.0, 50.0)
    )

    widget.render()

    # Verify size was passed to imgui.color_button
    call_args = mock_imgui.color_button.call_args
    assert call_args is not None
    assert len(call_args[0]) == 4  # widget_id, color_vec, flags, size
