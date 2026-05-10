"""Slider and drag control widgets.

This module contains widgets for numeric input via sliders and drag controls:
- SliderIntWidget: Integer slider with min/max range
- SliderFloatWidget: Float slider with min/max range
- DragIntWidget: Integer drag control (click and drag to change value)
- DragFloatWidget: Float drag control (click and drag to change value)
- ProgressBarWidget is in progress.py
"""

from imgui_bundle import imgui

from champi_imgui.core.widget import Widget


class SliderIntWidget(Widget):
    """Integer slider widget.

    Displays a horizontal slider for selecting an integer value within a range.
    """

    def __init__(
        self,
        widget_id: str,
        label: str = "Slider",
        value: int = 0,
        v_min: int = 0,
        v_max: int = 100,
        **props,
    ):
        """Initialize integer slider.

        Args:
            widget_id: Unique widget identifier
            label: Slider label text
            value: Initial value
            v_min: Minimum value
            v_max: Maximum value
            **props: Additional properties (format, etc.)
        """
        props["label"] = label
        props["value"] = value
        props["v_min"] = v_min
        props["v_max"] = v_max
        super().__init__(widget_id, **props)
        self._value = value

    def render(self) -> int:
        """Render the slider.

        Returns:
            Current integer value
        """
        if not self.state.visible:
            return self._value

        label = self.state.properties.get("label", "Slider")
        v_min = self.state.properties.get("v_min", 0)
        v_max = self.state.properties.get("v_max", 100)
        format_str = self.state.properties.get("format", "%d")

        changed, self._value = imgui.slider_int(
            label, self._value, v_min, v_max, format_str
        )

        if changed:
            self.state.properties["value"] = self._value
            self.trigger_callback("on_change", self._value)

        return self._value

    def get_value(self) -> int:
        """Get current value.

        Returns:
            Current integer value
        """
        return self._value

    def set_value(self, value: int) -> None:
        """Set value.

        Args:
            value: New integer value
        """
        self._value = value
        self.state.properties["value"] = value


class SliderFloatWidget(Widget):
    """Float slider widget.

    Displays a horizontal slider for selecting a float value within a range.
    """

    def __init__(
        self,
        widget_id: str,
        label: str = "Slider",
        value: float = 0.0,
        v_min: float = 0.0,
        v_max: float = 1.0,
        **props,
    ):
        """Initialize float slider.

        Args:
            widget_id: Unique widget identifier
            label: Slider label text
            value: Initial value
            v_min: Minimum value
            v_max: Maximum value
            **props: Additional properties (format, etc.)
        """
        props["label"] = label
        props["value"] = value
        props["v_min"] = v_min
        props["v_max"] = v_max
        super().__init__(widget_id, **props)
        self._value = value

    def render(self) -> float:
        """Render the slider.

        Returns:
            Current float value
        """
        if not self.state.visible:
            return self._value

        label = self.state.properties.get("label", "Slider")
        v_min = self.state.properties.get("v_min", 0.0)
        v_max = self.state.properties.get("v_max", 1.0)
        format_str = self.state.properties.get("format", "%.3f")

        changed, self._value = imgui.slider_float(
            label, self._value, v_min, v_max, format_str
        )

        if changed:
            self.state.properties["value"] = self._value
            self.trigger_callback("on_change", self._value)

        return self._value

    def get_value(self) -> float:
        """Get current value.

        Returns:
            Current float value
        """
        return self._value

    def set_value(self, value: float) -> None:
        """Set value.

        Args:
            value: New float value
        """
        self._value = value
        self.state.properties["value"] = value


class DragIntWidget(Widget):
    """Integer drag control widget.

    Allows the user to click and drag to change an integer value.
    """

    def __init__(
        self,
        widget_id: str,
        label: str = "Drag",
        value: int = 0,
        v_speed: float = 1.0,
        v_min: int = 0,
        v_max: int = 0,
        **props,
    ):
        """Initialize integer drag control.

        Args:
            widget_id: Unique widget identifier
            label: Control label text
            value: Initial value
            v_speed: Drag speed (change per pixel dragged)
            v_min: Minimum value (0 means no minimum)
            v_max: Maximum value (0 means no maximum)
            **props: Additional properties (format, etc.)
        """
        props["label"] = label
        props["value"] = value
        props["v_speed"] = v_speed
        props["v_min"] = v_min
        props["v_max"] = v_max
        super().__init__(widget_id, **props)
        self._value = value

    def render(self) -> int:
        """Render the drag control.

        Returns:
            Current integer value
        """
        if not self.state.visible:
            return self._value

        label = self.state.properties.get("label", "Drag")
        v_speed = self.state.properties.get("v_speed", 1.0)
        v_min = self.state.properties.get("v_min", 0)
        v_max = self.state.properties.get("v_max", 0)
        format_str = self.state.properties.get("format", "%d")

        changed, self._value = imgui.drag_int(
            label, self._value, v_speed, v_min, v_max, format_str
        )

        if changed:
            self.state.properties["value"] = self._value
            self.trigger_callback("on_change", self._value)

        return self._value

    def get_value(self) -> int:
        """Get current value.

        Returns:
            Current integer value
        """
        return self._value

    def set_value(self, value: int) -> None:
        """Set value.

        Args:
            value: New integer value
        """
        self._value = value
        self.state.properties["value"] = value


class DragFloatWidget(Widget):
    """Float drag control widget.

    Allows the user to click and drag to change a float value.
    """

    def __init__(
        self,
        widget_id: str,
        label: str = "Drag",
        value: float = 0.0,
        v_speed: float = 0.01,
        v_min: float = 0.0,
        v_max: float = 0.0,
        **props,
    ):
        """Initialize float drag control.

        Args:
            widget_id: Unique widget identifier
            label: Control label text
            value: Initial value
            v_speed: Drag speed (change per pixel dragged)
            v_min: Minimum value (0.0 means no minimum)
            v_max: Maximum value (0.0 means no maximum)
            **props: Additional properties (format, etc.)
        """
        props["label"] = label
        props["value"] = value
        props["v_speed"] = v_speed
        props["v_min"] = v_min
        props["v_max"] = v_max
        super().__init__(widget_id, **props)
        self._value = value

    def render(self) -> float:
        """Render the drag control.

        Returns:
            Current float value
        """
        if not self.state.visible:
            return self._value

        label = self.state.properties.get("label", "Drag")
        v_speed = self.state.properties.get("v_speed", 0.01)
        v_min = self.state.properties.get("v_min", 0.0)
        v_max = self.state.properties.get("v_max", 0.0)
        format_str = self.state.properties.get("format", "%.3f")

        changed, self._value = imgui.drag_float(
            label, self._value, v_speed, v_min, v_max, format_str
        )

        if changed:
            self.state.properties["value"] = self._value
            self.trigger_callback("on_change", self._value)

        return self._value

    def get_value(self) -> float:
        """Get current value.

        Returns:
            Current float value
        """
        return self._value

    def set_value(self, value: float) -> None:
        """Set value.

        Args:
            value: New float value
        """
        self._value = value
        self.state.properties["value"] = value
