"""Input widgets: numeric inputs, combos, lists, and selection controls.

This module contains advanced input widgets:
- Numeric inputs (int, float, double, scalar)
- Selection controls (combo, listbox, selectable, radio buttons)
- Checkbox flags for multi-selection
"""

from imgui_bundle import imgui

from champi_imgui.core.widget import Widget


class InputIntWidget(Widget):
    """Integer input widget with step controls."""

    def __init__(
        self,
        widget_id: str,
        label: str = "Input Int",
        value: int = 0,
        step: int = 1,
        step_fast: int = 100,
        **props,
    ):
        """Initialize integer input.

        Args:
            widget_id: Unique widget identifier
            label: Input label
            value: Initial value
            step: Step size for +/- buttons
            step_fast: Fast step size (Ctrl + click)
            **props: Additional properties
        """
        props["label"] = label
        props["value"] = value
        props["step"] = step
        props["step_fast"] = step_fast
        super().__init__(widget_id, **props)
        self._value = value

    def render(self) -> int:
        """Render the integer input.

        Returns:
            Current integer value
        """
        if not self.state.visible:
            return self._value

        label = self.state.properties.get("label", "Input Int")
        step = self.state.properties.get("step", 1)
        step_fast = self.state.properties.get("step_fast", 100)

        changed, self._value = imgui.input_int(label, self._value, step, step_fast)

        if changed:
            self.state.properties["value"] = self._value
            self.trigger_callback("on_change", self._value)

        return self._value

    def get_value(self) -> int:
        """Get current value."""
        return self._value

    def set_value(self, value: int) -> None:
        """Set value."""
        self._value = value
        self.state.properties["value"] = value


class InputFloatWidget(Widget):
    """Float input widget with step controls."""

    def __init__(
        self,
        widget_id: str,
        label: str = "Input Float",
        value: float = 0.0,
        step: float = 0.0,
        step_fast: float = 0.0,
        format_str: str = "%.3f",
        **props,
    ):
        """Initialize float input.

        Args:
            widget_id: Unique widget identifier
            label: Input label
            value: Initial value
            step: Step size for +/- buttons (0 = no buttons)
            step_fast: Fast step size (Ctrl + click)
            format_str: Display format string
            **props: Additional properties
        """
        props["label"] = label
        props["value"] = value
        props["step"] = step
        props["step_fast"] = step_fast
        props["format"] = format_str
        super().__init__(widget_id, **props)
        self._value = value

    def render(self) -> float:
        """Render the float input.

        Returns:
            Current float value
        """
        if not self.state.visible:
            return self._value

        label = self.state.properties.get("label", "Input Float")
        step = self.state.properties.get("step", 0.0)
        step_fast = self.state.properties.get("step_fast", 0.0)
        format_str = self.state.properties.get("format", "%.3f")

        changed, self._value = imgui.input_float(
            label, self._value, step, step_fast, format_str
        )

        if changed:
            self.state.properties["value"] = self._value
            self.trigger_callback("on_change", self._value)

        return self._value

    def get_value(self) -> float:
        """Get current value."""
        return self._value

    def set_value(self, value: float) -> None:
        """Set value."""
        self._value = value
        self.state.properties["value"] = value


class InputDoubleWidget(Widget):
    """Double precision float input widget."""

    def __init__(
        self,
        widget_id: str,
        label: str = "Input Double",
        value: float = 0.0,
        step: float = 0.0,
        step_fast: float = 0.0,
        format_str: str = "%.6f",
        **props,
    ):
        """Initialize double input.

        Args:
            widget_id: Unique widget identifier
            label: Input label
            value: Initial value
            step: Step size for +/- buttons (0 = no buttons)
            step_fast: Fast step size (Ctrl + click)
            format_str: Display format string
            **props: Additional properties
        """
        props["label"] = label
        props["value"] = value
        props["step"] = step
        props["step_fast"] = step_fast
        props["format"] = format_str
        super().__init__(widget_id, **props)
        self._value = value

    def render(self) -> float:
        """Render the double input.

        Returns:
            Current double value
        """
        if not self.state.visible:
            return self._value

        label = self.state.properties.get("label", "Input Double")
        step = self.state.properties.get("step", 0.0)
        step_fast = self.state.properties.get("step_fast", 0.0)
        format_str = self.state.properties.get("format", "%.6f")

        changed, self._value = imgui.input_double(
            label, self._value, step, step_fast, format_str
        )

        if changed:
            self.state.properties["value"] = self._value
            self.trigger_callback("on_change", self._value)

        return self._value

    def get_value(self) -> float:
        """Get current value."""
        return self._value

    def set_value(self, value: float) -> None:
        """Set value."""
        self._value = value
        self.state.properties["value"] = value


class InputScalarWidget(Widget):
    """Generic scalar input widget for custom data types."""

    def __init__(
        self,
        widget_id: str,
        label: str = "Input Scalar",
        value: float = 0.0,
        data_type: int = imgui.DataType_.float,
        **props,
    ):
        """Initialize scalar input.

        Args:
            widget_id: Unique widget identifier
            label: Input label
            value: Initial value
            data_type: ImGui data type constant
            **props: Additional properties
        """
        props["label"] = label
        props["value"] = value
        props["data_type"] = data_type
        super().__init__(widget_id, **props)
        self._value = value

    def render(self) -> float:
        """Render the scalar input.

        Returns:
            Current scalar value
        """
        if not self.state.visible:
            return self._value

        label = self.state.properties.get("label", "Input Scalar")
        # Note: imgui.input_scalar has complex API, simplified here
        # Full implementation would need proper type handling
        changed, self._value = imgui.input_float(label, self._value)

        if changed:
            self.state.properties["value"] = self._value
            self.trigger_callback("on_change", self._value)

        return self._value

    def get_value(self) -> float:
        """Get current value."""
        return self._value


class RadioButtonWidget(Widget):
    """Radio button widget for exclusive selection."""

    def __init__(
        self, widget_id: str, label: str = "Radio", active: bool = False, **props
    ):
        """Initialize radio button.

        Args:
            widget_id: Unique widget identifier
            label: Button label
            active: Initial active state
            **props: Additional properties
        """
        props["label"] = label
        props["active"] = active
        super().__init__(widget_id, **props)
        self._active = active

    def render(self) -> bool:
        """Render the radio button.

        Returns:
            True if clicked, False otherwise
        """
        if not self.state.visible:
            return False

        label = self.state.properties.get("label", "Radio")
        clicked = imgui.radio_button(label, self._active)

        if clicked:
            self._active = not self._active
            self.state.properties["active"] = self._active
            self.trigger_callback("on_click", self._active)

        return clicked

    def is_active(self) -> bool:
        """Get active state."""
        return self._active

    def set_active(self, active: bool) -> None:
        """Set active state."""
        self._active = active
        self.state.properties["active"] = active


class ComboWidget(Widget):
    """Combo box (dropdown) widget."""

    def __init__(
        self,
        widget_id: str,
        label: str = "Combo",
        items: list[str] | None = None,
        current_item: int = 0,
        **props,
    ):
        """Initialize combo box.

        Args:
            widget_id: Unique widget identifier
            label: Combo label
            items: List of items to display
            current_item: Initial selected item index
            **props: Additional properties
        """
        props["label"] = label
        props["items"] = items or []
        props["current_item"] = current_item
        super().__init__(widget_id, **props)
        self._current_item = current_item

    def render(self) -> int:
        """Render the combo box.

        Returns:
            Current selected item index
        """
        if not self.state.visible:
            return self._current_item

        label = self.state.properties.get("label", "Combo")
        items = self.state.properties.get("items", [])

        if not items:
            return self._current_item

        changed, self._current_item = imgui.combo(label, self._current_item, items)

        if changed:
            self.state.properties["current_item"] = self._current_item
            self.trigger_callback(
                "on_change", self._current_item, items[self._current_item]
            )

        return self._current_item

    def get_current_item(self) -> int:
        """Get current selected item index."""
        return self._current_item

    def get_current_value(self) -> str | None:
        """Get current selected item value."""
        items: list[str] = self.state.properties.get("items", [])
        if 0 <= self._current_item < len(items):
            return str(items[self._current_item])
        return None

    def set_items(self, items: list[str]) -> None:
        """Set the items list."""
        self.state.properties["items"] = items


class ListBoxWidget(Widget):
    """List box widget for single selection from a list."""

    def __init__(
        self,
        widget_id: str,
        label: str = "ListBox",
        items: list[str] | None = None,
        current_item: int = 0,
        **props,
    ):
        """Initialize list box.

        Args:
            widget_id: Unique widget identifier
            label: ListBox label
            items: List of items to display
            current_item: Initial selected item index
            **props: Additional properties (height_in_items, etc.)
        """
        props["label"] = label
        props["items"] = items or []
        props["current_item"] = current_item
        super().__init__(widget_id, **props)
        self._current_item = current_item

    def render(self) -> int:
        """Render the list box.

        Returns:
            Current selected item index
        """
        if not self.state.visible:
            return self._current_item

        label = self.state.properties.get("label", "ListBox")
        items = self.state.properties.get("items", [])
        height_in_items = self.state.properties.get("height_in_items", -1)

        if not items:
            return self._current_item

        changed, self._current_item = imgui.list_box(
            label, self._current_item, items, height_in_items
        )

        if changed:
            self.state.properties["current_item"] = self._current_item
            self.trigger_callback(
                "on_change", self._current_item, items[self._current_item]
            )

        return self._current_item

    def get_current_item(self) -> int:
        """Get current selected item index."""
        return self._current_item

    def get_current_value(self) -> str | None:
        """Get current selected item value."""
        items: list[str] = self.state.properties.get("items", [])
        if 0 <= self._current_item < len(items):
            return str(items[self._current_item])
        return None


class SelectableWidget(Widget):
    """Selectable widget for clickable list items."""

    def __init__(
        self,
        widget_id: str,
        label: str = "Selectable",
        selected: bool = False,
        **props,
    ):
        """Initialize selectable.

        Args:
            widget_id: Unique widget identifier
            label: Selectable label
            selected: Initial selected state
            **props: Additional properties (size, flags)
        """
        props["label"] = label
        props["selected"] = selected
        super().__init__(widget_id, **props)
        self._selected = selected

    def render(self) -> bool:
        """Render the selectable.

        Returns:
            Current selected state
        """
        if not self.state.visible:
            return self._selected

        label = self.state.properties.get("label", "Selectable")
        flags = self.state.properties.get("flags", 0)
        size = self.state.properties.get("size")

        if size:
            clicked, self._selected = imgui.selectable(
                label, self._selected, flags, imgui.ImVec2(size[0], size[1])
            )
        else:
            clicked, self._selected = imgui.selectable(label, self._selected, flags)

        if clicked:
            self.state.properties["selected"] = self._selected
            self.trigger_callback("on_click", self._selected)

        return self._selected

    def is_selected(self) -> bool:
        """Get selected state."""
        return self._selected

    def set_selected(self, selected: bool) -> None:
        """Set selected state."""
        self._selected = selected
        self.state.properties["selected"] = selected


class CheckboxFlagsWidget(Widget):
    """Checkbox flags widget for bitfield manipulation."""

    def __init__(
        self,
        widget_id: str,
        label: str = "Checkbox Flags",
        flags: int = 0,
        flags_value: int = 1,
        **props,
    ):
        """Initialize checkbox flags.

        Args:
            widget_id: Unique widget identifier
            label: Checkbox label
            flags: Current flags value (bitfield)
            flags_value: Bit value to toggle
            **props: Additional properties
        """
        props["label"] = label
        props["flags"] = flags
        props["flags_value"] = flags_value
        super().__init__(widget_id, **props)
        self._flags = flags

    def render(self) -> int:
        """Render the checkbox flags.

        Returns:
            Current flags value
        """
        if not self.state.visible:
            return self._flags

        label = self.state.properties.get("label", "Checkbox Flags")
        flags_value = self.state.properties.get("flags_value", 1)

        changed, self._flags = imgui.checkbox_flags(label, self._flags, flags_value)

        if changed:
            self.state.properties["flags"] = self._flags
            self.trigger_callback("on_change", self._flags)

        return self._flags

    def get_flags(self) -> int:
        """Get current flags value."""
        return self._flags

    def set_flags(self, flags: int) -> None:
        """Set flags value."""
        self._flags = flags
        self.state.properties["flags"] = flags
