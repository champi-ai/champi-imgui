"""Progress widgets: progress bars, loading indicators, and status displays.

This module contains widgets for showing progress and loading states:
- ProgressBarWidget: Standard progress bar with fraction/overlay
- LoadingIndicatorWidget: Animated spinner/loading indicator
- StatusBarWidget: Status display with text and optional progress
"""

from imgui_bundle import imgui

from champi_imgui.core.widget import Widget


class ProgressBarWidget(Widget):
    """Progress bar widget for displaying progress as a filled bar."""

    def __init__(
        self,
        widget_id: str,
        fraction: float = 0.0,
        size: tuple[float, float] = (-1.0, 0.0),
        overlay: str | None = None,
        **props,
    ):
        """Initialize progress bar.

        Args:
            widget_id: Unique widget identifier
            fraction: Progress fraction (0.0 to 1.0)
            size: Bar size (width, height) - (-1, 0) means full width, default height
            overlay: Optional text overlay on the progress bar
            **props: Additional properties
        """
        props["fraction"] = fraction
        props["size"] = size
        props["overlay"] = overlay
        super().__init__(widget_id, **props)
        self._fraction = fraction

    def render(self) -> None:
        """Render the progress bar."""
        if not self.state.visible:
            return

        fraction = self.state.properties.get("fraction", 0.0)
        size = self.state.properties.get("size", (-1.0, 0.0))
        overlay = self.state.properties.get("overlay")

        imgui.progress_bar(fraction, imgui.ImVec2(size[0], size[1]), overlay)

    def get_fraction(self) -> float:
        """Get current progress fraction.

        Returns:
            Progress fraction (0.0 to 1.0)
        """
        return self._fraction

    def set_fraction(self, fraction: float) -> None:
        """Set progress fraction.

        Args:
            fraction: Progress fraction (0.0 to 1.0)
        """
        self._fraction = max(0.0, min(1.0, fraction))
        self.state.properties["fraction"] = self._fraction


class LoadingIndicatorWidget(Widget):
    """Loading indicator (spinner) widget for showing loading states."""

    def __init__(
        self,
        widget_id: str,
        label: str = "Loading",
        radius: float = 10.0,
        thickness: float = 3.0,
        color: tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0),
        **props,
    ):
        """Initialize loading indicator.

        Args:
            widget_id: Unique widget identifier
            label: Loading label text
            radius: Spinner radius in pixels
            thickness: Spinner line thickness
            color: Spinner color (RGBA, 0.0-1.0 range per channel)
            **props: Additional properties
        """
        props["label"] = label
        props["radius"] = radius
        props["thickness"] = thickness
        props["color"] = color
        super().__init__(widget_id, **props)

    def render(self) -> None:
        """Render the loading indicator."""
        if not self.state.visible:
            return

        label = self.state.properties.get("label", "Loading")
        radius = self.state.properties.get("radius", 10.0)
        thickness = self.state.properties.get("thickness", 3.0)
        color = self.state.properties.get("color", (1.0, 1.0, 1.0, 1.0))

        # Custom spinner using draw list
        draw_list = imgui.get_window_draw_list()
        pos = imgui.get_cursor_screen_pos()
        center = imgui.ImVec2(pos.x + radius, pos.y + radius)

        # Simple rotating arc
        num_segments = 12
        start = imgui.get_time() * 6.0
        imgui.dummy(imgui.ImVec2(radius * 2, radius * 2))

        for i in range(num_segments):
            import math

            angle = start + (i / num_segments) * math.pi * 2
            alpha = 1.0 - (i / num_segments)
            col = imgui.get_color_u32(
                imgui.ImVec4(color[0], color[1], color[2], color[3] * alpha)
            )
            draw_list.add_circle_filled(
                imgui.ImVec2(
                    center.x + radius * 0.7 * math.cos(angle),
                    center.y + radius * 0.7 * math.sin(angle),
                ),
                thickness,
                col,
            )

        # Draw label
        imgui.same_line()
        imgui.text(label)


class StatusBarWidget(Widget):
    """Status bar widget for displaying status text with optional progress."""

    def __init__(
        self,
        widget_id: str,
        text: str = "Ready",
        show_progress: bool = False,
        progress_fraction: float = 0.0,
        **props,
    ):
        """Initialize status bar.

        Args:
            widget_id: Unique widget identifier
            text: Status text to display
            show_progress: Whether to show progress bar
            progress_fraction: Progress fraction if show_progress is True (0.0 to 1.0)
            **props: Additional properties
        """
        props["text"] = text
        props["show_progress"] = show_progress
        props["progress_fraction"] = progress_fraction
        super().__init__(widget_id, **props)
        self._text = text
        self._progress_fraction = progress_fraction

    def render(self) -> None:
        """Render the status bar."""
        if not self.state.visible:
            return

        text = self.state.properties.get("text", "Ready")
        show_progress = self.state.properties.get("show_progress", False)
        progress_fraction = self.state.properties.get("progress_fraction", 0.0)

        # Display status text
        imgui.text(text)

        # Optionally show progress bar
        if show_progress:
            imgui.same_line()
            imgui.progress_bar(progress_fraction, imgui.ImVec2(100, 0))

    def get_text(self) -> str:
        """Get current status text.

        Returns:
            Status text
        """
        return self._text

    def set_text(self, text: str) -> None:
        """Set status text.

        Args:
            text: New status text
        """
        self._text = text
        self.state.properties["text"] = text

    def get_progress_fraction(self) -> float:
        """Get current progress fraction.

        Returns:
            Progress fraction (0.0 to 1.0)
        """
        return self._progress_fraction

    def set_progress_fraction(self, fraction: float) -> None:
        """Set progress fraction.

        Args:
            fraction: Progress fraction (0.0 to 1.0)
        """
        self._progress_fraction = max(0.0, min(1.0, fraction))
        self.state.properties["progress_fraction"] = self._progress_fraction

    def set_show_progress(self, show: bool) -> None:
        """Set whether to show progress bar.

        Args:
            show: True to show progress bar, False to hide
        """
        self.state.properties["show_progress"] = show
