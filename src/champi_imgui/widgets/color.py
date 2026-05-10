"""Color widgets: color pickers, editors, and color buttons.

This module contains widgets for color selection and manipulation:
- ColorEdit3Widget, ColorEdit4Widget: Direct color value editing
- ColorPicker3Widget, ColorPickerWidget: Interactive color pickers
- ColorButtonWidget: Clickable color swatches
"""

from imgui_bundle import imgui

from champi_imgui.core.widget import Widget


class ColorEdit3Widget(Widget):
    """RGB color editor widget (no alpha channel)."""

    def __init__(
        self,
        widget_id: str,
        label: str = "Color",
        color: tuple[float, float, float] = (1.0, 1.0, 1.0),
        **props,
    ):
        """Initialize RGB color editor.

        Args:
            widget_id: Unique widget identifier
            label: Editor label
            color: Initial RGB color (0.0-1.0 range per channel)
            **props: Additional properties (flags, etc.)
        """
        props["label"] = label
        props["color"] = color
        super().__init__(widget_id, **props)
        self._color = list(color)

    def render(self) -> tuple[float, float, float]:
        """Render the RGB color editor.

        Returns:
            Current RGB color tuple
        """
        if not self.state.visible:
            return tuple(self._color)  # type: ignore

        label = self.state.properties.get("label", "Color")
        flags = self.state.properties.get("flags", 0)

        changed, self._color = imgui.color_edit3(label, self._color, flags)

        if changed:
            self.state.properties["color"] = tuple(self._color)
            self.trigger_callback("on_change", tuple(self._color))

        return tuple(self._color)  # type: ignore

    def get_color(self) -> tuple[float, float, float]:
        """Get current RGB color.

        Returns:
            RGB color tuple
        """
        return tuple(self._color)  # type: ignore

    def set_color(self, color: tuple[float, float, float]) -> None:
        """Set RGB color.

        Args:
            color: RGB color tuple
        """
        self._color = list(color)
        self.state.properties["color"] = color


class ColorEdit4Widget(Widget):
    """RGBA color editor widget (with alpha channel)."""

    def __init__(
        self,
        widget_id: str,
        label: str = "Color",
        color: tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0),
        **props,
    ):
        """Initialize RGBA color editor.

        Args:
            widget_id: Unique widget identifier
            label: Editor label
            color: Initial RGBA color (0.0-1.0 range per channel)
            **props: Additional properties (flags, etc.)
        """
        props["label"] = label
        props["color"] = color
        super().__init__(widget_id, **props)
        self._color = list(color)

    def render(self) -> tuple[float, float, float, float]:
        """Render the RGBA color editor.

        Returns:
            Current RGBA color tuple
        """
        if not self.state.visible:
            return tuple(self._color)  # type: ignore

        label = self.state.properties.get("label", "Color")
        flags = self.state.properties.get("flags", 0)

        changed, self._color = imgui.color_edit4(label, self._color, flags)

        if changed:
            self.state.properties["color"] = tuple(self._color)
            self.trigger_callback("on_change", tuple(self._color))

        return tuple(self._color)  # type: ignore

    def get_color(self) -> tuple[float, float, float, float]:
        """Get current RGBA color.

        Returns:
            RGBA color tuple
        """
        return tuple(self._color)  # type: ignore

    def set_color(self, color: tuple[float, float, float, float]) -> None:
        """Set RGBA color.

        Args:
            color: RGBA color tuple
        """
        self._color = list(color)
        self.state.properties["color"] = color


class ColorPicker3Widget(Widget):
    """RGB color picker widget with interactive picker interface."""

    def __init__(
        self,
        widget_id: str,
        label: str = "Color Picker",
        color: tuple[float, float, float] = (1.0, 1.0, 1.0),
        **props,
    ):
        """Initialize RGB color picker.

        Args:
            widget_id: Unique widget identifier
            label: Picker label
            color: Initial RGB color (0.0-1.0 range per channel)
            **props: Additional properties (flags, etc.)
        """
        props["label"] = label
        props["color"] = color
        super().__init__(widget_id, **props)
        self._color = list(color)

    def render(self) -> tuple[float, float, float]:
        """Render the RGB color picker.

        Returns:
            Current RGB color tuple
        """
        if not self.state.visible:
            return tuple(self._color)  # type: ignore

        label = self.state.properties.get("label", "Color Picker")
        flags = self.state.properties.get("flags", 0)

        changed, self._color = imgui.color_picker3(label, self._color, flags)

        if changed:
            self.state.properties["color"] = tuple(self._color)
            self.trigger_callback("on_change", tuple(self._color))

        return tuple(self._color)  # type: ignore

    def get_color(self) -> tuple[float, float, float]:
        """Get current RGB color.

        Returns:
            RGB color tuple
        """
        return tuple(self._color)  # type: ignore

    def set_color(self, color: tuple[float, float, float]) -> None:
        """Set RGB color.

        Args:
            color: RGB color tuple
        """
        self._color = list(color)
        self.state.properties["color"] = color


class ColorPickerWidget(Widget):
    """RGBA color picker widget with interactive picker interface."""

    def __init__(
        self,
        widget_id: str,
        label: str = "Color Picker",
        color: tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0),
        **props,
    ):
        """Initialize RGBA color picker.

        Args:
            widget_id: Unique widget identifier
            label: Picker label
            color: Initial RGBA color (0.0-1.0 range per channel)
            **props: Additional properties (flags, ref_col, etc.)
        """
        props["label"] = label
        props["color"] = color
        super().__init__(widget_id, **props)
        self._color = list(color)

    def render(self) -> tuple[float, float, float, float]:
        """Render the RGBA color picker.

        Returns:
            Current RGBA color tuple
        """
        if not self.state.visible:
            return tuple(self._color)  # type: ignore

        label = self.state.properties.get("label", "Color Picker")
        flags = self.state.properties.get("flags", 0)
        ref_col = self.state.properties.get("ref_col")

        if ref_col:
            changed, color_result = imgui.color_picker4(
                label, self._color, flags, ref_col
            )
        else:
            changed, color_result = imgui.color_picker4(label, self._color, flags)

        if changed:
            # Convert ImVec4 to list
            self._color = [
                color_result.x,
                color_result.y,
                color_result.z,
                color_result.w,
            ]
            self.state.properties["color"] = tuple(self._color)
            self.trigger_callback("on_change", tuple(self._color))

        return tuple(self._color)  # type: ignore[return-value]

    def get_color(self) -> tuple[float, float, float, float]:
        """Get current RGBA color.

        Returns:
            RGBA color tuple
        """
        return tuple(self._color)  # type: ignore

    def set_color(self, color: tuple[float, float, float, float]) -> None:
        """Set RGBA color.

        Args:
            color: RGBA color tuple
        """
        self._color = list(color)
        self.state.properties["color"] = color


class ColorButtonWidget(Widget):
    """Color button widget - displays a clickable color swatch."""

    def __init__(
        self,
        widget_id: str,
        color: tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0),
        **props,
    ):
        """Initialize color button.

        Args:
            widget_id: Unique widget identifier (also used as desc_id)
            color: Button color (RGBA, 0.0-1.0 range per channel)
            **props: Additional properties (flags, size)
        """
        props["color"] = color
        super().__init__(widget_id, **props)
        self._color = list(color)

    def render(self) -> bool:
        """Render the color button.

        Returns:
            True if button was clicked, False otherwise
        """
        if not self.state.visible:
            return False

        flags = self.state.properties.get("flags", 0)
        size = self.state.properties.get("size")

        # Create ImVec4 for color
        color_vec = imgui.ImVec4(*self._color)

        if size:
            clicked = imgui.color_button(
                self.widget_id, color_vec, flags, imgui.ImVec2(size[0], size[1])
            )
        else:
            clicked = imgui.color_button(self.widget_id, color_vec, flags)

        if clicked:
            self.trigger_callback("on_click", tuple(self._color))

        return clicked

    def get_color(self) -> tuple[float, float, float, float]:
        """Get current button color.

        Returns:
            RGBA color tuple
        """
        return tuple(self._color)  # type: ignore

    def set_color(self, color: tuple[float, float, float, float]) -> None:
        """Set button color.

        Args:
            color: RGBA color tuple
        """
        self._color = list(color)
        self.state.properties["color"] = color
