"""Comprehensive tests for slider and drag control widgets.

Tests cover all 4 slider widgets:
- SliderIntWidget
- SliderFloatWidget
- DragIntWidget
- DragFloatWidget
"""

from champi_imgui.core.state import WidgetState
from champi_imgui.widgets.slider import (
    DragFloatWidget,
    DragIntWidget,
    SliderFloatWidget,
    SliderIntWidget,
)

# ==============================================================================
# SliderIntWidget Tests
# ==============================================================================


def test_slider_int_widget_creation():
    """Test SliderIntWidget creation with default values."""
    widget = SliderIntWidget("slider-int-1")

    assert widget.widget_id == "slider-int-1"
    assert isinstance(widget.state, WidgetState)
    assert widget.state.widget_type == "SliderIntWidget"
    assert widget.state.properties["label"] == "Slider"
    assert widget.state.properties["value"] == 0
    assert widget.state.properties["v_min"] == 0
    assert widget.state.properties["v_max"] == 100
    assert widget._value == 0


def test_slider_int_widget_with_custom_values():
    """Test SliderIntWidget with custom values."""
    widget = SliderIntWidget("slider-int-2", label="Volume", value=50, v_min=0, v_max=200)

    assert widget.state.properties["label"] == "Volume"
    assert widget.state.properties["value"] == 50
    assert widget.state.properties["v_min"] == 0
    assert widget.state.properties["v_max"] == 200
    assert widget._value == 50


def test_slider_int_widget_get_value():
    """Test SliderIntWidget get_value method."""
    widget = SliderIntWidget("slider-int-3", value=42)

    assert widget.get_value() == 42


def test_slider_int_widget_set_value():
    """Test SliderIntWidget set_value method."""
    widget = SliderIntWidget("slider-int-4")

    widget.set_value(75)
    assert widget.get_value() == 75
    assert widget.state.properties["value"] == 75


def test_slider_int_widget_with_format():
    """Test SliderIntWidget stores custom format string."""
    widget = SliderIntWidget("slider-int-5", format="%d%%")

    assert widget.state.properties["format"] == "%d%%"


def test_slider_int_widget_visibility():
    """Test SliderIntWidget respects visibility flag."""
    widget = SliderIntWidget("slider-int-6", value=10)

    widget.set_visible(False)
    assert widget.state.visible is False
    # render() returns current value when hidden
    assert widget.render() == 10


# ==============================================================================
# SliderFloatWidget Tests
# ==============================================================================


def test_slider_float_widget_creation():
    """Test SliderFloatWidget creation with default values."""
    widget = SliderFloatWidget("slider-float-1")

    assert widget.widget_id == "slider-float-1"
    assert isinstance(widget.state, WidgetState)
    assert widget.state.widget_type == "SliderFloatWidget"
    assert widget.state.properties["label"] == "Slider"
    assert widget.state.properties["value"] == 0.0
    assert widget.state.properties["v_min"] == 0.0
    assert widget.state.properties["v_max"] == 1.0
    assert widget._value == 0.0


def test_slider_float_widget_with_custom_values():
    """Test SliderFloatWidget with custom values."""
    widget = SliderFloatWidget(
        "slider-float-2", label="Opacity", value=0.5, v_min=0.0, v_max=1.0
    )

    assert widget.state.properties["label"] == "Opacity"
    assert widget.state.properties["value"] == 0.5
    assert widget.state.properties["v_min"] == 0.0
    assert widget.state.properties["v_max"] == 1.0
    assert widget._value == 0.5


def test_slider_float_widget_get_value():
    """Test SliderFloatWidget get_value method."""
    widget = SliderFloatWidget("slider-float-3", value=0.75)

    assert widget.get_value() == 0.75


def test_slider_float_widget_set_value():
    """Test SliderFloatWidget set_value method."""
    widget = SliderFloatWidget("slider-float-4")

    widget.set_value(0.33)
    assert widget.get_value() == 0.33
    assert widget.state.properties["value"] == 0.33


def test_slider_float_widget_with_format():
    """Test SliderFloatWidget stores custom format string."""
    widget = SliderFloatWidget("slider-float-5", format="%.2f")

    assert widget.state.properties["format"] == "%.2f"


def test_slider_float_widget_visibility():
    """Test SliderFloatWidget respects visibility flag."""
    widget = SliderFloatWidget("slider-float-6", value=0.5)

    widget.set_visible(False)
    assert widget.state.visible is False
    assert widget.render() == 0.5


# ==============================================================================
# DragIntWidget Tests
# ==============================================================================


def test_drag_int_widget_creation():
    """Test DragIntWidget creation with default values."""
    widget = DragIntWidget("drag-int-1")

    assert widget.widget_id == "drag-int-1"
    assert isinstance(widget.state, WidgetState)
    assert widget.state.widget_type == "DragIntWidget"
    assert widget.state.properties["label"] == "Drag"
    assert widget.state.properties["value"] == 0
    assert widget.state.properties["v_speed"] == 1.0
    assert widget.state.properties["v_min"] == 0
    assert widget.state.properties["v_max"] == 0
    assert widget._value == 0


def test_drag_int_widget_with_custom_values():
    """Test DragIntWidget with custom values."""
    widget = DragIntWidget(
        "drag-int-2", label="Count", value=10, v_speed=2.0, v_min=-100, v_max=100
    )

    assert widget.state.properties["label"] == "Count"
    assert widget.state.properties["value"] == 10
    assert widget.state.properties["v_speed"] == 2.0
    assert widget.state.properties["v_min"] == -100
    assert widget.state.properties["v_max"] == 100
    assert widget._value == 10


def test_drag_int_widget_get_value():
    """Test DragIntWidget get_value method."""
    widget = DragIntWidget("drag-int-3", value=5)

    assert widget.get_value() == 5


def test_drag_int_widget_set_value():
    """Test DragIntWidget set_value method."""
    widget = DragIntWidget("drag-int-4")

    widget.set_value(99)
    assert widget.get_value() == 99
    assert widget.state.properties["value"] == 99


def test_drag_int_widget_visibility():
    """Test DragIntWidget respects visibility flag."""
    widget = DragIntWidget("drag-int-5", value=7)

    widget.set_visible(False)
    assert widget.state.visible is False
    assert widget.render() == 7


# ==============================================================================
# DragFloatWidget Tests
# ==============================================================================


def test_drag_float_widget_creation():
    """Test DragFloatWidget creation with default values."""
    widget = DragFloatWidget("drag-float-1")

    assert widget.widget_id == "drag-float-1"
    assert isinstance(widget.state, WidgetState)
    assert widget.state.widget_type == "DragFloatWidget"
    assert widget.state.properties["label"] == "Drag"
    assert widget.state.properties["value"] == 0.0
    assert widget.state.properties["v_speed"] == 0.01
    assert widget.state.properties["v_min"] == 0.0
    assert widget.state.properties["v_max"] == 0.0
    assert widget._value == 0.0


def test_drag_float_widget_with_custom_values():
    """Test DragFloatWidget with custom values."""
    widget = DragFloatWidget(
        "drag-float-2", label="Scale", value=1.5, v_speed=0.1, v_min=0.0, v_max=10.0
    )

    assert widget.state.properties["label"] == "Scale"
    assert widget.state.properties["value"] == 1.5
    assert widget.state.properties["v_speed"] == 0.1
    assert widget.state.properties["v_min"] == 0.0
    assert widget.state.properties["v_max"] == 10.0
    assert widget._value == 1.5


def test_drag_float_widget_get_value():
    """Test DragFloatWidget get_value method."""
    widget = DragFloatWidget("drag-float-3", value=3.14)

    assert widget.get_value() == 3.14


def test_drag_float_widget_set_value():
    """Test DragFloatWidget set_value method."""
    widget = DragFloatWidget("drag-float-4")

    widget.set_value(2.71)
    assert widget.get_value() == 2.71
    assert widget.state.properties["value"] == 2.71


def test_drag_float_widget_with_format():
    """Test DragFloatWidget stores custom format string."""
    widget = DragFloatWidget("drag-float-5", format="%.1f")

    assert widget.state.properties["format"] == "%.1f"


def test_drag_float_widget_visibility():
    """Test DragFloatWidget respects visibility flag."""
    widget = DragFloatWidget("drag-float-6", value=1.0)

    widget.set_visible(False)
    assert widget.state.visible is False
    assert widget.render() == 1.0


# ==============================================================================
# Cross-widget Tests
# ==============================================================================


def test_all_slider_widgets_have_state():
    """Test that all slider widgets have proper WidgetState."""
    widgets = [
        SliderIntWidget("w1"),
        SliderFloatWidget("w2"),
        DragIntWidget("w3"),
        DragFloatWidget("w4"),
    ]

    for widget in widgets:
        assert isinstance(widget.state, WidgetState)
        assert widget.state.widget_id is not None
        assert widget.state.widget_type is not None


def test_all_slider_widgets_are_visible_by_default():
    """Test that all slider widgets start visible."""
    widgets = [
        SliderIntWidget("w1"),
        SliderFloatWidget("w2"),
        DragIntWidget("w3"),
        DragFloatWidget("w4"),
    ]

    for widget in widgets:
        assert widget.state.visible is True


def test_slider_widgets_callback_registration():
    """Test that slider widgets can register callbacks."""
    widget = SliderIntWidget("cb-test")
    callback_called = []

    widget.register_callback("on_change", lambda v: callback_called.append(v))

    assert "on_change" in widget._callbacks


def test_drag_float_widget_callback_registration():
    """Test that DragFloatWidget can register callbacks."""
    widget = DragFloatWidget("cb-test-2")
    callback_called = []

    widget.register_callback("on_change", lambda v: callback_called.append(v))

    assert "on_change" in widget._callbacks
