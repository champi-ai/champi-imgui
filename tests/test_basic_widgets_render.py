"""Render tests for basic widgets using mocks.

These tests verify render() method behavior by mocking imgui calls.
They ensure render methods handle visibility, call correct ImGui functions,
and trigger callbacks appropriately.
"""

from unittest.mock import patch

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
# Button Render Tests
# ==============================================================================


@patch("champi_imgui.widgets.basic.imgui")
def test_button_widget_render(mock_imgui):
    """Test ButtonWidget render method."""
    mock_imgui.button.return_value = True
    widget = ButtonWidget("btn-1", label="Click")

    result = widget.render()

    assert result is True
    mock_imgui.button.assert_called_once()


@patch("champi_imgui.widgets.basic.imgui")
def test_button_widget_render_with_size(mock_imgui):
    """Test ButtonWidget render with size."""
    mock_imgui.button.return_value = False
    widget = ButtonWidget("btn-2", label="Button", size=(100.0, 50.0))

    result = widget.render()

    assert result is False
    mock_imgui.button.assert_called_once()


@patch("champi_imgui.widgets.basic.imgui")
def test_button_widget_render_invisible(mock_imgui):
    """Test ButtonWidget render when invisible."""
    widget = ButtonWidget("btn-3")
    widget.set_visible(False)

    result = widget.render()

    assert result is False
    mock_imgui.button.assert_not_called()


@patch("champi_imgui.widgets.basic.imgui")
def test_button_widget_callback_on_click(mock_imgui):
    """Test ButtonWidget triggers callback on click."""
    mock_imgui.button.return_value = True
    widget = ButtonWidget("btn-4")

    callback_triggered = []

    def on_click():
        callback_triggered.append(True)

    widget.register_callback("on_click", on_click)
    widget.render()

    assert len(callback_triggered) == 1


@patch("champi_imgui.widgets.basic.imgui")
def test_small_button_widget_render(mock_imgui):
    """Test SmallButtonWidget render method."""
    mock_imgui.small_button.return_value = True
    widget = SmallButtonWidget("small-1", label="Small")

    result = widget.render()

    assert result is True
    mock_imgui.small_button.assert_called_once_with("Small")


@patch("champi_imgui.widgets.basic.imgui")
def test_small_button_widget_render_invisible(mock_imgui):
    """Test SmallButtonWidget render when invisible."""
    widget = SmallButtonWidget("small-2")
    widget.set_visible(False)

    result = widget.render()

    assert result is False
    mock_imgui.small_button.assert_not_called()


@patch("champi_imgui.widgets.basic.imgui")
def test_arrow_button_widget_render(mock_imgui):
    """Test ArrowButtonWidget render method."""
    mock_imgui.arrow_button.return_value = True
    widget = ArrowButtonWidget("arrow-1", direction=1)

    result = widget.render()

    assert result is True
    mock_imgui.arrow_button.assert_called_once_with("arrow-1", 1)


@patch("champi_imgui.widgets.basic.imgui")
def test_arrow_button_widget_render_invisible(mock_imgui):
    """Test ArrowButtonWidget render when invisible."""
    widget = ArrowButtonWidget("arrow-2")
    widget.set_visible(False)

    result = widget.render()

    assert result is False
    mock_imgui.arrow_button.assert_not_called()


@patch("champi_imgui.widgets.basic.imgui")
def test_invisible_button_widget_render(mock_imgui):
    """Test InvisibleButtonWidget render method."""
    mock_imgui.invisible_button.return_value = True
    widget = InvisibleButtonWidget("inv-1", size=(200.0, 100.0))

    result = widget.render()

    assert result is True
    mock_imgui.invisible_button.assert_called_once()


@patch("champi_imgui.widgets.basic.imgui")
def test_invisible_button_widget_render_invisible(mock_imgui):
    """Test InvisibleButtonWidget render when invisible."""
    widget = InvisibleButtonWidget("inv-2")
    widget.set_visible(False)

    result = widget.render()

    assert result is False
    mock_imgui.invisible_button.assert_not_called()


# ==============================================================================
# Text Render Tests
# ==============================================================================


@patch("champi_imgui.widgets.basic.imgui")
def test_text_widget_render(mock_imgui):
    """Test TextWidget render method."""
    widget = TextWidget("text-1", text="Hello")

    widget.render()

    mock_imgui.text.assert_called_once_with("Hello")


@patch("champi_imgui.widgets.basic.imgui")
def test_text_widget_render_invisible(mock_imgui):
    """Test TextWidget render when invisible."""
    widget = TextWidget("text-2", text="Hidden")
    widget.set_visible(False)

    widget.render()

    mock_imgui.text.assert_not_called()


@patch("champi_imgui.widgets.basic.imgui")
def test_text_colored_widget_render(mock_imgui):
    """Test TextColoredWidget render method."""
    widget = TextColoredWidget("colored-1", text="Red", color=(1.0, 0.0, 0.0, 1.0))

    widget.render()

    mock_imgui.text_colored.assert_called_once()


@patch("champi_imgui.widgets.basic.imgui")
def test_text_colored_widget_render_invisible(mock_imgui):
    """Test TextColoredWidget render when invisible."""
    widget = TextColoredWidget("colored-2")
    widget.set_visible(False)

    widget.render()

    mock_imgui.text_colored.assert_not_called()


@patch("champi_imgui.widgets.basic.imgui")
def test_text_disabled_widget_render(mock_imgui):
    """Test TextDisabledWidget render method."""
    widget = TextDisabledWidget("disabled-1", text="Disabled")

    widget.render()

    mock_imgui.text_disabled.assert_called_once_with("Disabled")


@patch("champi_imgui.widgets.basic.imgui")
def test_text_disabled_widget_render_invisible(mock_imgui):
    """Test TextDisabledWidget render when invisible."""
    widget = TextDisabledWidget("disabled-2")
    widget.set_visible(False)

    widget.render()

    mock_imgui.text_disabled.assert_not_called()


@patch("champi_imgui.widgets.basic.imgui")
def test_text_wrapped_widget_render(mock_imgui):
    """Test TextWrappedWidget render method."""
    widget = TextWrappedWidget("wrapped-1", text="Long text")

    widget.render()

    mock_imgui.text_wrapped.assert_called_once_with("Long text")


@patch("champi_imgui.widgets.basic.imgui")
def test_text_wrapped_widget_render_invisible(mock_imgui):
    """Test TextWrappedWidget render when invisible."""
    widget = TextWrappedWidget("wrapped-2")
    widget.set_visible(False)

    widget.render()

    mock_imgui.text_wrapped.assert_not_called()


@patch("champi_imgui.widgets.basic.imgui")
def test_bullet_text_widget_render(mock_imgui):
    """Test BulletTextWidget render method."""
    widget = BulletTextWidget("bullet-text-1", text="Bullet")

    widget.render()

    mock_imgui.bullet_text.assert_called_once_with("Bullet")


@patch("champi_imgui.widgets.basic.imgui")
def test_bullet_text_widget_render_invisible(mock_imgui):
    """Test BulletTextWidget render when invisible."""
    widget = BulletTextWidget("bullet-text-2")
    widget.set_visible(False)

    widget.render()

    mock_imgui.bullet_text.assert_not_called()


@patch("champi_imgui.widgets.basic.imgui")
def test_bullet_widget_render(mock_imgui):
    """Test BulletWidget render method."""
    widget = BulletWidget("bullet-1")

    widget.render()

    mock_imgui.bullet.assert_called_once()


@patch("champi_imgui.widgets.basic.imgui")
def test_bullet_widget_render_invisible(mock_imgui):
    """Test BulletWidget render when invisible."""
    widget = BulletWidget("bullet-2")
    widget.set_visible(False)

    widget.render()

    mock_imgui.bullet.assert_not_called()


@patch("champi_imgui.widgets.basic.imgui")
def test_label_text_widget_render(mock_imgui):
    """Test LabelTextWidget render method."""
    widget = LabelTextWidget("label-1", label="Name", text="John")

    widget.render()

    mock_imgui.label_text.assert_called_once_with("Name", "John")


@patch("champi_imgui.widgets.basic.imgui")
def test_label_text_widget_render_invisible(mock_imgui):
    """Test LabelTextWidget render when invisible."""
    widget = LabelTextWidget("label-2")
    widget.set_visible(False)

    widget.render()

    mock_imgui.label_text.assert_not_called()


# ==============================================================================
# InputTextWidget Render Tests
# ==============================================================================


@patch("champi_imgui.widgets.basic.imgui")
def test_input_text_widget_render(mock_imgui):
    """Test InputTextWidget render method."""
    mock_imgui.input_text.return_value = (False, "test")
    widget = InputTextWidget("input-1", label="Name", value="test")

    result = widget.render()

    assert result == "test"
    mock_imgui.input_text.assert_called_once()


@patch("champi_imgui.widgets.basic.imgui")
def test_input_text_widget_render_invisible(mock_imgui):
    """Test InputTextWidget render when invisible."""
    widget = InputTextWidget("input-2", value="hidden")
    widget.set_visible(False)

    result = widget.render()

    assert result == "hidden"
    mock_imgui.input_text.assert_not_called()


@patch("champi_imgui.widgets.basic.imgui")
def test_input_text_widget_render_with_hint(mock_imgui):
    """Test InputTextWidget render with hint."""
    mock_imgui.input_text_with_hint.return_value = (False, "")
    widget = InputTextWidget("input-3", label="Email", hint="user@example.com")

    widget.render()

    mock_imgui.input_text_with_hint.assert_called_once()


@patch("champi_imgui.widgets.basic.imgui")
def test_input_text_widget_render_multiline(mock_imgui):
    """Test InputTextWidget render in multiline mode."""
    mock_imgui.input_text_multiline.return_value = (False, "")
    widget = InputTextWidget(
        "input-4", label="Description", multiline=True, size=(300.0, 100.0)
    )

    widget.render()

    mock_imgui.input_text_multiline.assert_called_once()


@patch("champi_imgui.widgets.basic.imgui")
def test_input_text_widget_value_changed(mock_imgui):
    """Test InputTextWidget triggers callback on value change."""
    mock_imgui.input_text.return_value = (True, "new value")
    widget = InputTextWidget("input-5", value="old")

    callback_values = []

    def on_change(value):
        callback_values.append(value)

    widget.register_callback("on_change", on_change)
    result = widget.render()

    assert result == "new value"
    assert widget.state.properties["value"] == "new value"
    assert callback_values == ["new value"]


# ==============================================================================
# CheckboxWidget Render Tests
# ==============================================================================


@patch("champi_imgui.widgets.basic.imgui")
def test_checkbox_widget_render(mock_imgui):
    """Test CheckboxWidget render method."""
    mock_imgui.checkbox.return_value = (False, False)
    widget = CheckboxWidget("check-1", label="Accept")

    result = widget.render()

    assert result is False
    mock_imgui.checkbox.assert_called_once_with("Accept", False)


@patch("champi_imgui.widgets.basic.imgui")
def test_checkbox_widget_render_invisible(mock_imgui):
    """Test CheckboxWidget render when invisible."""
    widget = CheckboxWidget("check-2", checked=True)
    widget.set_visible(False)

    result = widget.render()

    assert result is True
    mock_imgui.checkbox.assert_not_called()


@patch("champi_imgui.widgets.basic.imgui")
def test_checkbox_widget_changed(mock_imgui):
    """Test CheckboxWidget triggers callback on state change."""
    mock_imgui.checkbox.return_value = (True, True)
    widget = CheckboxWidget("check-3", label="Agree", checked=False)

    callback_states = []

    def on_change(checked):
        callback_states.append(checked)

    widget.register_callback("on_change", on_change)
    result = widget.render()

    assert result is True
    assert widget.state.properties["checked"] is True
    assert callback_states == [True]
