"""Basic widgets: buttons, text, inputs, checkboxes.

This module contains the fundamental UI widgets for user interaction:
- Buttons (standard, small, arrow, invisible)
- Text display (plain, colored, disabled, wrapped, bullet)
- Text input (single-line, multiline, with hint)
- Checkboxes
"""

from imgui_bundle import imgui

from champi_imgui.core.widget import Widget


class ButtonWidget(Widget):
    """Standard button widget.

    A clickable button that triggers callbacks on click.
    """

    def __init__(self, widget_id: str, label: str = "Button", **props):
        """Initialize button.

        Args:
            widget_id: Unique widget identifier
            label: Button label text
            **props: Additional properties (size, etc.)
        """
        props["label"] = label
        super().__init__(widget_id, **props)

    def render(self) -> bool:
        """Render the button.

        Returns:
            True if button was clicked, False otherwise
        """
        if not self.state.visible:
            return False

        label = self.state.properties.get("label", "Button")
        size = self.state.properties.get("size")

        if size:
            clicked = imgui.button(label, imgui.ImVec2(size[0], size[1]))
        else:
            clicked = imgui.button(label)

        if clicked:
            self.trigger_callback("on_click")

        return clicked


class SmallButtonWidget(Widget):
    """Small button widget.

    A compact button that takes up less space.
    """

    def __init__(self, widget_id: str, label: str = "Button", **props):
        """Initialize small button.

        Args:
            widget_id: Unique widget identifier
            label: Button label text
            **props: Additional properties
        """
        props["label"] = label
        super().__init__(widget_id, **props)

    def render(self) -> bool:
        """Render the small button.

        Returns:
            True if button was clicked, False otherwise
        """
        if not self.state.visible:
            return False

        label = self.state.properties.get("label", "Button")
        clicked = imgui.small_button(label)

        if clicked:
            self.trigger_callback("on_click")

        return clicked


class ArrowButtonWidget(Widget):
    """Arrow button widget.

    A button that displays a directional arrow.
    """

    def __init__(self, widget_id: str, direction: int = 0, **props):
        """Initialize arrow button.

        Args:
            widget_id: Unique widget identifier
            direction: Arrow direction (imgui.Dir.left/right/up/down)
            **props: Additional properties
        """
        props["direction"] = direction
        super().__init__(widget_id, **props)

    def render(self) -> bool:
        """Render the arrow button.

        Returns:
            True if button was clicked, False otherwise
        """
        if not self.state.visible:
            return False

        direction = self.state.properties.get("direction", 0)
        clicked = imgui.arrow_button(self.widget_id, direction)

        if clicked:
            self.trigger_callback("on_click")

        return clicked


class InvisibleButtonWidget(Widget):
    """Invisible button widget.

    A clickable area without visual representation.
    Useful for custom rendering with click detection.
    """

    def __init__(
        self,
        widget_id: str,
        size: tuple[float, float] = (100.0, 30.0),
        **props,
    ):
        """Initialize invisible button.

        Args:
            widget_id: Unique widget identifier
            size: Button size (width, height)
            **props: Additional properties
        """
        props["size"] = size
        super().__init__(widget_id, **props)

    def render(self) -> bool:
        """Render the invisible button.

        Returns:
            True if button was clicked, False otherwise
        """
        if not self.state.visible:
            return False

        size = self.state.properties.get("size", (100.0, 30.0))
        flags = self.state.properties.get("flags", 0)

        clicked = imgui.invisible_button(
            self.widget_id, imgui.ImVec2(size[0], size[1]), flags
        )

        if clicked:
            self.trigger_callback("on_click")

        return clicked


class TextWidget(Widget):
    """Static text label widget.

    Displays non-interactive text.
    """

    def __init__(self, widget_id: str, text: str = "", **props):
        """Initialize text widget.

        Args:
            widget_id: Unique widget identifier
            text: Text to display
            **props: Additional properties
        """
        props["text"] = text
        super().__init__(widget_id, **props)

    def render(self) -> None:
        """Render the text."""
        if not self.state.visible:
            return

        text = self.state.properties.get("text", "")
        imgui.text(text)


class TextColoredWidget(Widget):
    """Colored text widget.

    Displays text with a custom color.
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
            color: RGBA color tuple (0.0-1.0 range)
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


class TextDisabledWidget(Widget):
    """Disabled text widget.

    Displays text in a disabled (grayed out) style.
    """

    def __init__(self, widget_id: str, text: str = "", **props):
        """Initialize disabled text widget.

        Args:
            widget_id: Unique widget identifier
            text: Text to display
            **props: Additional properties
        """
        props["text"] = text
        super().__init__(widget_id, **props)

    def render(self) -> None:
        """Render the disabled text."""
        if not self.state.visible:
            return

        text = self.state.properties.get("text", "")
        imgui.text_disabled(text)


class TextWrappedWidget(Widget):
    """Wrapped text widget.

    Displays text with automatic line wrapping.
    """

    def __init__(self, widget_id: str, text: str = "", **props):
        """Initialize wrapped text widget.

        Args:
            widget_id: Unique widget identifier
            text: Text to display
            **props: Additional properties
        """
        props["text"] = text
        super().__init__(widget_id, **props)

    def render(self) -> None:
        """Render the wrapped text."""
        if not self.state.visible:
            return

        text = self.state.properties.get("text", "")
        imgui.text_wrapped(text)


class BulletTextWidget(Widget):
    """Bullet text widget.

    Displays text with a bullet point prefix.
    """

    def __init__(self, widget_id: str, text: str = "", **props):
        """Initialize bullet text widget.

        Args:
            widget_id: Unique widget identifier
            text: Text to display
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


class BulletWidget(Widget):
    """Bullet point widget.

    Displays a simple bullet point.
    """

    def __init__(self, widget_id: str, **props):
        """Initialize bullet widget.

        Args:
            widget_id: Unique widget identifier
            **props: Additional properties
        """
        super().__init__(widget_id, **props)

    def render(self) -> None:
        """Render the bullet point."""
        if not self.state.visible:
            return

        imgui.bullet()


class LabelTextWidget(Widget):
    """Label text widget.

    Displays a label-value pair (label: value).
    """

    def __init__(self, widget_id: str, label: str = "Label", text: str = "", **props):
        """Initialize label text widget.

        Args:
            widget_id: Unique widget identifier
            label: Label text
            text: Value text
            **props: Additional properties
        """
        props["label"] = label
        props["text"] = text
        super().__init__(widget_id, **props)

    def render(self) -> None:
        """Render the label-text pair."""
        if not self.state.visible:
            return

        label = self.state.properties.get("label", "Label")
        text = self.state.properties.get("text", "")
        imgui.label_text(label, text)


class InputTextWidget(Widget):
    """Text input widget.

    Interactive text input field with support for:
    - Single-line input
    - Multiline input
    - Hint text (placeholder)
    """

    def __init__(self, widget_id: str, label: str = "Input", value: str = "", **props):
        """Initialize input text widget.

        Args:
            widget_id: Unique widget identifier
            label: Input label
            value: Initial value
            **props: Additional properties (hint, multiline, size)
        """
        props["label"] = label
        props["value"] = value
        super().__init__(widget_id, **props)
        self._value = value

    def render(self) -> str:
        """Render the input field.

        Returns:
            Current input value
        """
        if not self.state.visible:
            return self._value

        label = self.state.properties.get("label", "Input")
        hint = self.state.properties.get("hint")
        multiline = self.state.properties.get("multiline", False)
        size = self.state.properties.get("size")

        # Choose appropriate ImGui function based on mode
        if multiline and size:
            changed, self._value = imgui.input_text_multiline(
                label, self._value, imgui.ImVec2(size[0], size[1])
            )
        elif hint:
            changed, self._value = imgui.input_text_with_hint(label, hint, self._value)
        else:
            changed, self._value = imgui.input_text(label, self._value)

        if changed:
            self.state.properties["value"] = self._value
            self.trigger_callback("on_change", self._value)

        return self._value

    def get_value(self) -> str:
        """Get current input value.

        Returns:
            Current value
        """
        return self._value

    def set_value(self, value: str) -> None:
        """Set input value.

        Args:
            value: New value
        """
        self._value = value
        self.state.properties["value"] = value


class CheckboxWidget(Widget):
    """Checkbox widget.

    Interactive checkbox for boolean selection.
    """

    def __init__(
        self, widget_id: str, label: str = "Checkbox", checked: bool = False, **props
    ):
        """Initialize checkbox.

        Args:
            widget_id: Unique widget identifier
            label: Checkbox label
            checked: Initial checked state
            **props: Additional properties
        """
        props["label"] = label
        props["checked"] = checked
        super().__init__(widget_id, **props)
        self._checked = checked

    def render(self) -> bool:
        """Render the checkbox.

        Returns:
            Current checked state
        """
        if not self.state.visible:
            return self._checked

        label = self.state.properties.get("label", "Checkbox")
        changed, self._checked = imgui.checkbox(label, self._checked)

        if changed:
            self.state.properties["checked"] = self._checked
            self.trigger_callback("on_change", self._checked)

        return self._checked

    def get_checked(self) -> bool:
        """Get checked state.

        Returns:
            True if checked, False otherwise
        """
        return self._checked

    def set_checked(self, checked: bool) -> None:
        """Set checked state.

        Args:
            checked: New checked state
        """
        self._checked = checked
        self.state.properties["checked"] = checked
