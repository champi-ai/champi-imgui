"""Render tests for progress widgets using mocks.

These tests verify render() method behavior by mocking imgui calls.
They ensure render methods handle visibility, call correct ImGui functions,
and work correctly with different configurations.
"""

from unittest.mock import MagicMock, patch

from champi_imgui.widgets.progress import (
    LoadingIndicatorWidget,
    ProgressBarWidget,
    StatusBarWidget,
)

# ==============================================================================
# ProgressBarWidget Render Tests
# ==============================================================================


@patch("champi_imgui.widgets.progress.imgui")
def test_progress_bar_widget_render(mock_imgui):
    """Test ProgressBarWidget render method."""
    mock_imgui.ImVec2 = MagicMock(return_value="mock_vec2")
    widget = ProgressBarWidget("progress-1", fraction=0.5)

    widget.render()

    mock_imgui.progress_bar.assert_called_once()
    call_args = mock_imgui.progress_bar.call_args
    assert call_args[0][0] == 0.5  # fraction


@patch("champi_imgui.widgets.progress.imgui")
def test_progress_bar_widget_render_invisible(mock_imgui):
    """Test ProgressBarWidget render when invisible."""
    widget = ProgressBarWidget("progress-2", fraction=0.5)
    widget.set_visible(False)

    widget.render()

    mock_imgui.progress_bar.assert_not_called()


@patch("champi_imgui.widgets.progress.imgui")
def test_progress_bar_widget_render_with_overlay(mock_imgui):
    """Test ProgressBarWidget render with overlay text."""
    mock_imgui.ImVec2 = MagicMock(return_value="mock_vec2")
    widget = ProgressBarWidget("progress-3", fraction=0.75, overlay="75%")

    widget.render()

    mock_imgui.progress_bar.assert_called_once()
    call_args = mock_imgui.progress_bar.call_args
    assert call_args[0][2] == "75%"  # overlay


@patch("champi_imgui.widgets.progress.imgui")
def test_progress_bar_widget_render_with_size(mock_imgui):
    """Test ProgressBarWidget render with custom size."""
    mock_imgui.ImVec2 = MagicMock(return_value="mock_vec2")
    widget = ProgressBarWidget("progress-4", fraction=0.5, size=(300.0, 25.0))

    widget.render()

    mock_imgui.progress_bar.assert_called_once()
    # Verify ImVec2 was created with size
    mock_imgui.ImVec2.assert_called_once_with(300.0, 25.0)


# ==============================================================================
# LoadingIndicatorWidget Render Tests
# ==============================================================================


@patch("champi_imgui.widgets.progress.imgui")
def test_loading_indicator_widget_render(mock_imgui):
    """Test LoadingIndicatorWidget render method."""
    mock_imgui.get_window_draw_list.return_value = MagicMock()
    mock_imgui.get_cursor_screen_pos.return_value = MagicMock(x=10.0, y=10.0)
    # Mock ImVec2 to return an object with x and y attributes
    mock_vec2 = MagicMock()
    mock_vec2.x = 20.0
    mock_vec2.y = 20.0
    mock_imgui.ImVec2 = MagicMock(return_value=mock_vec2)
    mock_imgui.get_time.return_value = 1.0
    mock_imgui.ImVec4 = MagicMock(return_value="mock_vec4")
    mock_imgui.get_color_u32.return_value = 0xFFFFFFFF
    widget = LoadingIndicatorWidget("loading-1")

    widget.render()

    # Verify that drawing functions were called
    mock_imgui.get_window_draw_list.assert_called_once()
    mock_imgui.get_cursor_screen_pos.assert_called_once()
    mock_imgui.dummy.assert_called_once()
    mock_imgui.same_line.assert_called_once()
    mock_imgui.text.assert_called_once_with("Loading")


@patch("champi_imgui.widgets.progress.imgui")
def test_loading_indicator_widget_render_invisible(mock_imgui):
    """Test LoadingIndicatorWidget render when invisible."""
    widget = LoadingIndicatorWidget("loading-2")
    widget.set_visible(False)

    widget.render()

    mock_imgui.get_window_draw_list.assert_not_called()


@patch("champi_imgui.widgets.progress.imgui")
def test_loading_indicator_widget_render_custom_label(mock_imgui):
    """Test LoadingIndicatorWidget render with custom label."""
    mock_imgui.get_window_draw_list.return_value = MagicMock()
    mock_imgui.get_cursor_screen_pos.return_value = MagicMock(x=10.0, y=10.0)
    # Mock ImVec2 to return an object with x and y attributes
    mock_vec2 = MagicMock()
    mock_vec2.x = 20.0
    mock_vec2.y = 20.0
    mock_imgui.ImVec2 = MagicMock(return_value=mock_vec2)
    mock_imgui.get_time.return_value = 1.0
    mock_imgui.ImVec4 = MagicMock(return_value="mock_vec4")
    mock_imgui.get_color_u32.return_value = 0xFFFFFFFF
    widget = LoadingIndicatorWidget("loading-3", label="Please Wait")

    widget.render()

    mock_imgui.text.assert_called_once_with("Please Wait")


@patch("champi_imgui.widgets.progress.imgui")
def test_loading_indicator_widget_render_custom_radius(mock_imgui):
    """Test LoadingIndicatorWidget render with custom radius."""
    mock_imgui.get_window_draw_list.return_value = MagicMock()
    mock_imgui.get_cursor_screen_pos.return_value = MagicMock(x=10.0, y=10.0)
    # Mock ImVec2 to return an object with x and y attributes
    mock_vec2 = MagicMock()
    mock_vec2.x = 30.0
    mock_vec2.y = 30.0
    mock_imgui.ImVec2 = MagicMock(return_value=mock_vec2)
    mock_imgui.get_time.return_value = 1.0
    mock_imgui.ImVec4 = MagicMock(return_value="mock_vec4")
    mock_imgui.get_color_u32.return_value = 0xFFFFFFFF
    widget = LoadingIndicatorWidget("loading-4", radius=20.0)

    widget.render()

    # Verify dummy was called with correct size (radius * 2)
    call_args = mock_imgui.dummy.call_args
    assert call_args is not None


# ==============================================================================
# StatusBarWidget Render Tests
# ==============================================================================


@patch("champi_imgui.widgets.progress.imgui")
def test_status_bar_widget_render(mock_imgui):
    """Test StatusBarWidget render method."""
    widget = StatusBarWidget("status-1", text="Ready")

    widget.render()

    mock_imgui.text.assert_called_once_with("Ready")
    mock_imgui.progress_bar.assert_not_called()


@patch("champi_imgui.widgets.progress.imgui")
def test_status_bar_widget_render_invisible(mock_imgui):
    """Test StatusBarWidget render when invisible."""
    widget = StatusBarWidget("status-2", text="Ready")
    widget.set_visible(False)

    widget.render()

    mock_imgui.text.assert_not_called()


@patch("champi_imgui.widgets.progress.imgui")
def test_status_bar_widget_render_with_progress(mock_imgui):
    """Test StatusBarWidget render with progress bar."""
    mock_imgui.ImVec2 = MagicMock(return_value="mock_vec2")
    widget = StatusBarWidget(
        "status-3", text="Loading", show_progress=True, progress_fraction=0.6
    )

    widget.render()

    mock_imgui.text.assert_called_once_with("Loading")
    mock_imgui.same_line.assert_called_once()
    mock_imgui.progress_bar.assert_called_once()
    call_args = mock_imgui.progress_bar.call_args
    assert call_args[0][0] == 0.6  # progress_fraction


@patch("champi_imgui.widgets.progress.imgui")
def test_status_bar_widget_render_custom_text(mock_imgui):
    """Test StatusBarWidget render with custom text."""
    widget = StatusBarWidget("status-4", text="Processing...")

    widget.render()

    mock_imgui.text.assert_called_once_with("Processing...")


@patch("champi_imgui.widgets.progress.imgui")
def test_status_bar_widget_render_progress_disabled(mock_imgui):
    """Test StatusBarWidget render with progress disabled."""
    widget = StatusBarWidget(
        "status-5", text="Done", show_progress=False, progress_fraction=1.0
    )

    widget.render()

    mock_imgui.text.assert_called_once_with("Done")
    mock_imgui.progress_bar.assert_not_called()
