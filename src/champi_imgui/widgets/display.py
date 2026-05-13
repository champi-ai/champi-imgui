"""Display and visualization widgets.

This module contains widgets for displaying data and formatted text:
- ImageWidget: Display a PNG/JPG image loaded from a file path
- PlotLinesWidget: Line plot from a list of float values
- TextColoredWidget: Text rendered in a custom RGBA color
- BulletTextWidget: Bullet-prefixed text line
- HelpMarkerWidget: Hoverable (?) marker that shows a tooltip
"""

from imgui_bundle import imgui

from champi_imgui.core.widget import Widget


class ImageWidget(Widget):
    """Image display widget.

    Loads a PNG or JPG image from a file path and renders it using imgui.image().
    Texture loading is deferred to the first render call so it always happens
    on the OpenGL render thread.
    """

    def __init__(
        self,
        widget_id: str,
        file_path: str = "",
        width: float = 200.0,
        height: float = 200.0,
        **props,
    ):
        """Initialize image widget.

        Args:
            widget_id: Unique widget identifier
            file_path: Absolute or relative path to a PNG or JPG image
            width: Display width in pixels
            height: Display height in pixels
            **props: Additional properties
        """
        props["file_path"] = file_path
        props["width"] = width
        props["height"] = height
        super().__init__(widget_id, **props)
        self._texture_id: int | None = None
        self._loaded_path: str = ""

    def _load_texture(self, file_path: str) -> int | None:
        """Load an image file into an OpenGL texture and return the texture ID.

        Must be called from the render thread while the OpenGL context is active.

        Args:
            file_path: Path to PNG or JPG image

        Returns:
            OpenGL texture ID, or None on failure
        """
        try:
            import numpy as np
            from OpenGL import GL
            from PIL import Image as PILImage

            img = PILImage.open(file_path).convert("RGBA")
            img_data = np.array(img, dtype=np.uint8)

            tex_id = GL.glGenTextures(1)
            GL.glBindTexture(GL.GL_TEXTURE_2D, tex_id)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
            GL.glTexImage2D(
                GL.GL_TEXTURE_2D,
                0,
                GL.GL_RGBA,
                img.width,
                img.height,
                0,
                GL.GL_RGBA,
                GL.GL_UNSIGNED_BYTE,
                img_data,
            )
            GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
            return int(tex_id)
        except Exception:
            return None

    def render(self) -> None:
        """Render the image. Loads the texture on first render or when file_path changes."""
        if not self.state.visible:
            return

        file_path = self.state.properties.get("file_path", "")
        width = self.state.properties.get("width", 200.0)
        height = self.state.properties.get("height", 200.0)

        if file_path != self._loaded_path:
            self._texture_id = self._load_texture(file_path) if file_path else None
            self._loaded_path = file_path

        if self._texture_id is None:
            imgui.text_disabled(f"[Image: {file_path or 'no file'}]")
            return

        imgui.image(imgui.ImTextureRef(self._texture_id), imgui.ImVec2(width, height))
        if imgui.is_item_clicked():
            self.trigger_callback("click")


class PlotLinesWidget(Widget):
    """Line plot widget.

    Renders a simple line graph from a list of float values using
    imgui.plot_lines.
    """

    def __init__(
        self,
        widget_id: str,
        label: str = "Plot",
        values: list[float] | None = None,
        overlay_text: str | None = None,
        scale_min: float | None = None,
        scale_max: float | None = None,
        graph_size: tuple[float, float] = (0, 0),
        **props,
    ):
        """Initialize plot lines widget.

        Args:
            widget_id: Unique widget identifier
            label: Plot label shown beside the graph
            values: List of float values to plot
            overlay_text: Optional text drawn over the graph area
            scale_min: Minimum Y scale (None = auto)
            scale_max: Maximum Y scale (None = auto)
            graph_size: (width, height) of the graph in pixels; (0,0) = auto
            **props: Additional properties
        """
        props["label"] = label
        props["values"] = values if values is not None else []
        props["overlay_text"] = overlay_text
        props["scale_min"] = scale_min
        props["scale_max"] = scale_max
        props["graph_size"] = graph_size
        super().__init__(widget_id, **props)

    def get_values(self) -> list[float]:
        """Return the current list of plot values."""
        return list(self.state.properties.get("values", []))

    def set_values(self, values: list[float]) -> None:
        """Update the plot values.

        Args:
            values: New list of float values to display
        """
        self.state.properties["values"] = list(values)

    def render(self) -> None:
        """Render the plot lines graph."""
        if not self.state.visible:
            return

        label = self.state.properties.get("label", "Plot")
        values = self.state.properties.get("values", [])
        overlay_text = self.state.properties.get("overlay_text")
        scale_min = self.state.properties.get("scale_min")
        scale_max = self.state.properties.get("scale_max")
        graph_size = self.state.properties.get("graph_size", (0, 0))

        if not values:
            return

        # imgui.plot_lines requires float | None for scale bounds
        s_min: float = scale_min if scale_min is not None else float("nan")
        s_max: float = scale_max if scale_max is not None else float("nan")

        imgui.plot_lines(
            label,
            values,
            0,
            overlay_text,
            s_min,
            s_max,
            imgui.ImVec2(*graph_size),
        )


class TextColoredWidget(Widget):
    """Colored text widget.

    Renders a text string in the specified RGBA color.
    """

    def __init__(
        self,
        widget_id: str,
        text: str = "",
        color: tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0),
        **props,
    ):
        """Initialize colored text widget.

        Args:
            widget_id: Unique widget identifier
            text: Text to display
            color: RGBA color tuple with components in [0, 1]
            **props: Additional properties
        """
        props["text"] = text
        props["color"] = color
        super().__init__(widget_id, **props)

    def render(self) -> None:
        """Render the colored text."""
        if not self.state.visible:
            return

        text = self.state.properties.get("text", "")
        color = self.state.properties.get("color", (1.0, 1.0, 1.0, 1.0))
        imgui.text_colored(imgui.ImVec4(*color), text)


class BulletTextWidget(Widget):
    """Bullet text widget.

    Renders a line of text prefixed with a small bullet point.
    """

    def __init__(self, widget_id: str, text: str = "", **props):
        """Initialize bullet text widget.

        Args:
            widget_id: Unique widget identifier
            text: Text to display after the bullet
            **props: Additional properties
        """
        props["text"] = text
        super().__init__(widget_id, **props)

    def render(self) -> None:
        """Render the bullet text."""
        if not self.state.visible:
            return

        text = self.state.properties.get("text", "")
        imgui.bullet_text(text)


class HelpMarkerWidget(Widget):
    """Help marker widget.

    Renders a disabled marker string (default "(?)")  that shows a tooltip
    with descriptive text when the user hovers over it.
    """

    def __init__(
        self,
        widget_id: str,
        description: str = "",
        marker: str = "(?)",
        **props,
    ):
        """Initialize help marker widget.

        Args:
            widget_id: Unique widget identifier
            description: Tooltip text shown on hover
            marker: Marker string rendered in the UI (default: "(?)")
            **props: Additional properties
        """
        props["description"] = description
        props["marker"] = marker
        super().__init__(widget_id, **props)

    def render(self) -> None:
        """Render the help marker and tooltip."""
        if not self.state.visible:
            return

        description = self.state.properties.get("description", "")
        marker = self.state.properties.get("marker", "(?)")

        imgui.text_disabled(marker)
        if imgui.is_item_hovered():
            imgui.set_tooltip(description)
