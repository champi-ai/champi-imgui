"""Comprehensive tests for display and visualization widgets.

Tests cover all 4 display widgets:
- PlotLinesWidget
- TextColoredWidget
- BulletTextWidget
- HelpMarkerWidget
"""

from champi_imgui.core.state import WidgetState
from champi_imgui.widgets.display import (
    BulletTextWidget,
    HelpMarkerWidget,
    PlotLinesWidget,
    TextColoredWidget,
)

# ==============================================================================
# PlotLinesWidget Tests
# ==============================================================================


def test_plot_lines_widget_creation_defaults():
    """Test PlotLinesWidget creation with default values."""
    widget = PlotLinesWidget("plot-1")

    assert widget.widget_id == "plot-1"
    assert isinstance(widget.state, WidgetState)
    assert widget.state.widget_type == "PlotLinesWidget"
    assert widget.state.properties["label"] == "Plot"
    assert widget.state.properties["values"] == []
    assert widget.state.properties["overlay_text"] is None
    assert widget.state.properties["scale_min"] is None
    assert widget.state.properties["scale_max"] is None
    assert widget.state.properties["graph_size"] == (0, 0)


def test_plot_lines_widget_creation_custom():
    """Test PlotLinesWidget creation with custom values."""
    values = [0.1, 0.5, 0.9, 0.3]
    widget = PlotLinesWidget(
        "plot-2",
        label="Signal",
        values=values,
        overlay_text="avg: 0.45",
        scale_min=0.0,
        scale_max=1.0,
        graph_size=(200, 80),
    )

    assert widget.state.properties["label"] == "Signal"
    assert widget.state.properties["values"] == values
    assert widget.state.properties["overlay_text"] == "avg: 0.45"
    assert widget.state.properties["scale_min"] == 0.0
    assert widget.state.properties["scale_max"] == 1.0
    assert widget.state.properties["graph_size"] == (200, 80)


def test_plot_lines_widget_none_values_becomes_empty():
    """Test PlotLinesWidget converts None values to empty list."""
    widget = PlotLinesWidget("plot-3", values=None)

    assert widget.state.properties["values"] == []


def test_plot_lines_widget_get_values():
    """Test PlotLinesWidget get_values returns a copy."""
    values = [1.0, 2.0, 3.0]
    widget = PlotLinesWidget("plot-4", values=values)

    result = widget.get_values()
    assert result == values
    # Returned list is a copy — mutations don't affect widget
    result.append(4.0)
    assert widget.get_values() == values


def test_plot_lines_widget_set_values():
    """Test PlotLinesWidget set_values updates stored values."""
    widget = PlotLinesWidget("plot-5")
    new_values = [0.2, 0.4, 0.6, 0.8, 1.0]

    widget.set_values(new_values)

    assert widget.state.properties["values"] == new_values
    assert widget.get_values() == new_values


def test_plot_lines_widget_set_values_is_copy():
    """Test PlotLinesWidget set_values stores an independent copy."""
    widget = PlotLinesWidget("plot-6")
    original = [1.0, 2.0]
    widget.set_values(original)
    original.append(3.0)

    assert widget.get_values() == [1.0, 2.0]


def test_plot_lines_widget_visibility():
    """Test PlotLinesWidget respects visibility flag."""
    widget = PlotLinesWidget("plot-7", values=[1.0, 2.0])

    widget.set_visible(False)
    assert widget.state.visible is False
    # render() returns None silently when hidden
    assert widget.render() is None


def test_plot_lines_widget_serialize():
    """Test PlotLinesWidget serializes correctly."""
    widget = PlotLinesWidget("plot-8", label="Data", values=[1.0, 2.0])

    data = widget.serialize()
    assert data["widget_id"] == "plot-8"
    assert data["widget_type"] == "PlotLinesWidget"
    assert data["properties"]["label"] == "Data"
    assert data["properties"]["values"] == [1.0, 2.0]


# ==============================================================================
# TextColoredWidget Tests
# ==============================================================================


def test_text_colored_widget_creation_defaults():
    """Test TextColoredWidget creation with default values."""
    widget = TextColoredWidget("colored-1")

    assert widget.widget_id == "colored-1"
    assert isinstance(widget.state, WidgetState)
    assert widget.state.widget_type == "TextColoredWidget"
    assert widget.state.properties["text"] == ""
    assert widget.state.properties["color"] == (1.0, 1.0, 1.0, 1.0)


def test_text_colored_widget_creation_custom():
    """Test TextColoredWidget creation with custom text and color."""
    color = (1.0, 0.0, 0.0, 1.0)
    widget = TextColoredWidget("colored-2", text="Error!", color=color)

    assert widget.state.properties["text"] == "Error!"
    assert widget.state.properties["color"] == color


def test_text_colored_widget_visibility():
    """Test TextColoredWidget respects visibility flag."""
    widget = TextColoredWidget("colored-3", text="Hidden")

    widget.set_visible(False)
    assert widget.state.visible is False
    assert widget.render() is None


def test_text_colored_widget_update_text():
    """Test TextColoredWidget text can be updated via state properties."""
    widget = TextColoredWidget("colored-4", text="Original")

    widget.state.properties["text"] = "Updated"
    assert widget.state.properties["text"] == "Updated"


def test_text_colored_widget_update_color():
    """Test TextColoredWidget color can be updated via state properties."""
    widget = TextColoredWidget("colored-5", color=(1.0, 1.0, 1.0, 1.0))

    new_color = (0.0, 1.0, 0.0, 0.8)
    widget.state.properties["color"] = new_color
    assert widget.state.properties["color"] == new_color


def test_text_colored_widget_serialize():
    """Test TextColoredWidget serializes correctly."""
    color = (0.5, 0.5, 0.5, 1.0)
    widget = TextColoredWidget("colored-6", text="Gray", color=color)

    data = widget.serialize()
    assert data["widget_id"] == "colored-6"
    assert data["widget_type"] == "TextColoredWidget"
    assert data["properties"]["text"] == "Gray"
    assert data["properties"]["color"] == color


# ==============================================================================
# BulletTextWidget Tests
# ==============================================================================


def test_bullet_text_widget_creation_defaults():
    """Test BulletTextWidget creation with default values."""
    widget = BulletTextWidget("bullet-1")

    assert widget.widget_id == "bullet-1"
    assert isinstance(widget.state, WidgetState)
    assert widget.state.widget_type == "BulletTextWidget"
    assert widget.state.properties["text"] == ""


def test_bullet_text_widget_creation_custom():
    """Test BulletTextWidget creation with custom text."""
    widget = BulletTextWidget("bullet-2", text="First item")

    assert widget.state.properties["text"] == "First item"


def test_bullet_text_widget_visibility():
    """Test BulletTextWidget respects visibility flag."""
    widget = BulletTextWidget("bullet-3", text="Hidden item")

    widget.set_visible(False)
    assert widget.state.visible is False
    assert widget.render() is None


def test_bullet_text_widget_update_text():
    """Test BulletTextWidget text can be updated."""
    widget = BulletTextWidget("bullet-4", text="Old")

    widget.state.properties["text"] = "New"
    assert widget.state.properties["text"] == "New"


def test_bullet_text_widget_serialize():
    """Test BulletTextWidget serializes correctly."""
    widget = BulletTextWidget("bullet-5", text="Item A")

    data = widget.serialize()
    assert data["widget_id"] == "bullet-5"
    assert data["widget_type"] == "BulletTextWidget"
    assert data["properties"]["text"] == "Item A"


# ==============================================================================
# HelpMarkerWidget Tests
# ==============================================================================


def test_help_marker_widget_creation_defaults():
    """Test HelpMarkerWidget creation with default values."""
    widget = HelpMarkerWidget("help-1")

    assert widget.widget_id == "help-1"
    assert isinstance(widget.state, WidgetState)
    assert widget.state.widget_type == "HelpMarkerWidget"
    assert widget.state.properties["description"] == ""
    assert widget.state.properties["marker"] == "(?)"


def test_help_marker_widget_creation_custom():
    """Test HelpMarkerWidget creation with custom description and marker."""
    widget = HelpMarkerWidget(
        "help-2",
        description="Hover for details",
        marker="[?]",
    )

    assert widget.state.properties["description"] == "Hover for details"
    assert widget.state.properties["marker"] == "[?]"


def test_help_marker_widget_visibility():
    """Test HelpMarkerWidget respects visibility flag."""
    widget = HelpMarkerWidget("help-3", description="Some help text")

    widget.set_visible(False)
    assert widget.state.visible is False
    assert widget.render() is None


def test_help_marker_widget_update_description():
    """Test HelpMarkerWidget description can be updated."""
    widget = HelpMarkerWidget("help-4", description="Old description")

    widget.state.properties["description"] = "New description"
    assert widget.state.properties["description"] == "New description"


def test_help_marker_widget_update_marker():
    """Test HelpMarkerWidget marker string can be updated."""
    widget = HelpMarkerWidget("help-5")

    widget.state.properties["marker"] = "[i]"
    assert widget.state.properties["marker"] == "[i]"


def test_help_marker_widget_serialize():
    """Test HelpMarkerWidget serializes correctly."""
    widget = HelpMarkerWidget("help-6", description="Click for info", marker="(?)")

    data = widget.serialize()
    assert data["widget_id"] == "help-6"
    assert data["widget_type"] == "HelpMarkerWidget"
    assert data["properties"]["description"] == "Click for info"
    assert data["properties"]["marker"] == "(?)"


# ==============================================================================
# Module import tests
# ==============================================================================


def test_display_widgets_importable_from_package():
    """Test that display widgets are importable from the widgets package."""
    import champi_imgui.widgets as pkg

    assert pkg.PlotLinesWidget is PlotLinesWidget
    assert pkg.HelpMarkerWidget is HelpMarkerWidget
