"""Comprehensive tests for progress widgets.

Tests cover all 3 progress widgets:
- ProgressBarWidget
- LoadingIndicatorWidget
- StatusBarWidget
"""

from champi_imgui.core.state import WidgetState
from champi_imgui.widgets.progress import (
    LoadingIndicatorWidget,
    ProgressBarWidget,
    StatusBarWidget,
)

# ==============================================================================
# ProgressBarWidget Tests
# ==============================================================================


def test_progress_bar_widget_creation():
    """Test ProgressBarWidget creation with default values."""
    widget = ProgressBarWidget("progress-1")

    assert widget.widget_id == "progress-1"
    assert isinstance(widget.state, WidgetState)
    assert widget.state.widget_type == "ProgressBarWidget"
    assert widget.state.properties["fraction"] == 0.0
    assert widget.state.properties["size"] == (-1.0, 0.0)
    assert widget.state.properties["overlay"] is None
    assert widget._fraction == 0.0


def test_progress_bar_widget_with_fraction():
    """Test ProgressBarWidget with custom fraction."""
    widget = ProgressBarWidget("progress-2", fraction=0.5, overlay="50%")

    assert widget.state.properties["fraction"] == 0.5
    assert widget.state.properties["overlay"] == "50%"
    assert widget._fraction == 0.5


def test_progress_bar_widget_with_size():
    """Test ProgressBarWidget with custom size."""
    widget = ProgressBarWidget("progress-3", size=(200.0, 20.0))

    assert widget.state.properties["size"] == (200.0, 20.0)


def test_progress_bar_widget_get_fraction():
    """Test ProgressBarWidget get_fraction method."""
    widget = ProgressBarWidget("progress-4", fraction=0.75)

    assert widget.get_fraction() == 0.75


def test_progress_bar_widget_set_fraction():
    """Test ProgressBarWidget set_fraction method."""
    widget = ProgressBarWidget("progress-5")

    widget.set_fraction(0.8)
    assert widget.get_fraction() == 0.8
    assert widget.state.properties["fraction"] == 0.8


def test_progress_bar_widget_set_fraction_clamps():
    """Test ProgressBarWidget set_fraction clamps to 0.0-1.0."""
    widget = ProgressBarWidget("progress-6")

    # Test clamping to 1.0
    widget.set_fraction(1.5)
    assert widget.get_fraction() == 1.0

    # Test clamping to 0.0
    widget.set_fraction(-0.5)
    assert widget.get_fraction() == 0.0


# ==============================================================================
# LoadingIndicatorWidget Tests
# ==============================================================================


def test_loading_indicator_widget_creation():
    """Test LoadingIndicatorWidget creation."""
    widget = LoadingIndicatorWidget("loading-1")

    assert widget.widget_id == "loading-1"
    assert widget.state.widget_type == "LoadingIndicatorWidget"
    assert widget.state.properties["label"] == "Loading"
    assert widget.state.properties["radius"] == 10.0
    assert widget.state.properties["thickness"] == 3.0
    assert widget.state.properties["color"] == (1.0, 1.0, 1.0, 1.0)


def test_loading_indicator_widget_with_custom_props():
    """Test LoadingIndicatorWidget with custom properties."""
    widget = LoadingIndicatorWidget(
        "loading-2",
        label="Please Wait",
        radius=15.0,
        thickness=5.0,
        color=(0.5, 0.5, 1.0, 1.0),
    )

    assert widget.state.properties["label"] == "Please Wait"
    assert widget.state.properties["radius"] == 15.0
    assert widget.state.properties["thickness"] == 5.0
    assert widget.state.properties["color"] == (0.5, 0.5, 1.0, 1.0)


# ==============================================================================
# StatusBarWidget Tests
# ==============================================================================


def test_status_bar_widget_creation():
    """Test StatusBarWidget creation."""
    widget = StatusBarWidget("status-1")

    assert widget.widget_id == "status-1"
    assert widget.state.widget_type == "StatusBarWidget"
    assert widget.state.properties["text"] == "Ready"
    assert widget.state.properties["show_progress"] is False
    assert widget.state.properties["progress_fraction"] == 0.0
    assert widget._text == "Ready"
    assert widget._progress_fraction == 0.0


def test_status_bar_widget_with_text():
    """Test StatusBarWidget with custom text."""
    widget = StatusBarWidget("status-2", text="Processing...")

    assert widget.state.properties["text"] == "Processing..."
    assert widget._text == "Processing..."


def test_status_bar_widget_with_progress():
    """Test StatusBarWidget with progress enabled."""
    widget = StatusBarWidget(
        "status-3", text="Loading", show_progress=True, progress_fraction=0.6
    )

    assert widget.state.properties["show_progress"] is True
    assert widget.state.properties["progress_fraction"] == 0.6
    assert widget._progress_fraction == 0.6


def test_status_bar_widget_get_text():
    """Test StatusBarWidget get_text method."""
    widget = StatusBarWidget("status-4", text="Done")

    assert widget.get_text() == "Done"


def test_status_bar_widget_set_text():
    """Test StatusBarWidget set_text method."""
    widget = StatusBarWidget("status-5")

    widget.set_text("Working...")
    assert widget.get_text() == "Working..."
    assert widget.state.properties["text"] == "Working..."


def test_status_bar_widget_get_progress_fraction():
    """Test StatusBarWidget get_progress_fraction method."""
    widget = StatusBarWidget("status-6", progress_fraction=0.4)

    assert widget.get_progress_fraction() == 0.4


def test_status_bar_widget_set_progress_fraction():
    """Test StatusBarWidget set_progress_fraction method."""
    widget = StatusBarWidget("status-7")

    widget.set_progress_fraction(0.7)
    assert widget.get_progress_fraction() == 0.7
    assert widget.state.properties["progress_fraction"] == 0.7


def test_status_bar_widget_set_progress_fraction_clamps():
    """Test StatusBarWidget set_progress_fraction clamps to 0.0-1.0."""
    widget = StatusBarWidget("status-8")

    # Test clamping to 1.0
    widget.set_progress_fraction(2.0)
    assert widget.get_progress_fraction() == 1.0

    # Test clamping to 0.0
    widget.set_progress_fraction(-1.0)
    assert widget.get_progress_fraction() == 0.0


def test_status_bar_widget_set_show_progress():
    """Test StatusBarWidget set_show_progress method."""
    widget = StatusBarWidget("status-9", show_progress=False)

    widget.set_show_progress(True)
    assert widget.state.properties["show_progress"] is True


# ==============================================================================
# Edge Cases and Coverage
# ==============================================================================


def test_widget_visibility_affects_render():
    """Test that invisible widgets respect visibility flag."""
    progress_bar = ProgressBarWidget("vis-1")
    loading_indicator = LoadingIndicatorWidget("vis-2")
    status_bar = StatusBarWidget("vis-3")

    # Set invisible
    progress_bar.set_visible(False)
    loading_indicator.set_visible(False)
    status_bar.set_visible(False)

    assert progress_bar.state.visible is False
    assert loading_indicator.state.visible is False
    assert status_bar.state.visible is False


def test_all_progress_widgets_have_state():
    """Test that all progress widgets have proper state."""
    widgets = [
        ProgressBarWidget("w1"),
        LoadingIndicatorWidget("w2"),
        StatusBarWidget("w3"),
    ]

    for widget in widgets:
        assert isinstance(widget.state, WidgetState)
        assert widget.state.widget_id is not None
        assert widget.state.widget_type is not None
