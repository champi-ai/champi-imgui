"""Container widgets: windows, panels, groups.

This module contains layout and container widgets:
- WindowWidget: Standalone window container
- ChildWindowWidget: Embedded child window region
- GroupWidget: Inline group for layout
- CollapsingHeaderWidget: Collapsible section header
- TabBarWidget: Tab bar container
- TabItemWidget: Individual tab item
- SeparatorWidget: Horizontal or vertical separator line
- SpacingWidget: Vertical spacing
- DummyWidget: Blank space placeholder
"""

import contextlib

from imgui_bundle import imgui

from champi_imgui.core.widget import Widget


class WindowWidget(Widget):
    """Standalone window container widget."""

    def __init__(
        self,
        widget_id: str,
        title: str = "Window",
        closable: bool = True,
        **props,
    ):
        """Initialize window widget.

        Args:
            widget_id: Unique widget identifier
            title: Window title bar text
            closable: Whether the window has a close button
            **props: Additional properties (flags, etc.)
        """
        props["title"] = title
        props["closable"] = closable
        props["is_open"] = True
        super().__init__(widget_id, **props)

    def render(self) -> bool:
        """Render the window.

        Returns:
            True if window is open, False if closed
        """
        title = self.state.properties.get("title", "Window")
        closable = self.state.properties.get("closable", True)
        flags = self.state.properties.get("flags", 0)
        is_open = self.state.properties.get("is_open", True)

        if not is_open:
            return False

        if closable:
            expanded, is_open = imgui.begin(title, True, flags)
            self.state.properties["is_open"] = is_open
        else:
            expanded, _ = imgui.begin(title, None, flags)

        if expanded:
            pass

        imgui.end()
        return bool(is_open)


class ChildWindowWidget(Widget):
    """Child window (embedded region) widget."""

    def __init__(
        self,
        widget_id: str,
        size: tuple[float, float] = (0, 0),
        border: bool = False,
        **props,
    ):
        """Initialize child window.

        Args:
            widget_id: Unique widget identifier
            size: Width and height of the child window (0 = auto)
            border: Whether to draw a border around the child window
            **props: Additional properties (flags, etc.)
        """
        props["size"] = size
        props["border"] = border
        super().__init__(widget_id, **props)

    def render(self) -> bool:
        """Render the child window.

        Returns:
            True if the child window is visible
        """
        size = self.state.properties.get("size", (0, 0))
        border = self.state.properties.get("border", False)
        flags = self.state.properties.get("flags", 0)

        visible = imgui.begin_child(self.widget_id, imgui.ImVec2(*size), border, flags)

        if visible:
            pass

        imgui.end_child()
        return bool(visible)


class GroupWidget(Widget):
    """Group widget for inline layout."""

    def __init__(self, widget_id: str, **props):
        """Initialize group widget.

        Args:
            widget_id: Unique widget identifier
            **props: Additional properties
        """
        super().__init__(widget_id, **props)

    def render(self) -> None:
        """Render the group."""
        imgui.begin_group()
        imgui.end_group()


class CollapsingHeaderWidget(Widget):
    """Collapsible section header widget."""

    def __init__(
        self,
        widget_id: str,
        label: str = "Header",
        default_open: bool = False,
        **props,
    ):
        """Initialize collapsing header.

        Args:
            widget_id: Unique widget identifier
            label: Header label text
            default_open: Whether the header starts expanded
            **props: Additional properties (flags, etc.)
        """
        props["label"] = label
        props["is_open"] = default_open
        super().__init__(widget_id, **props)

    def render(self) -> bool:
        """Render the collapsing header.

        Returns:
            True if the header is expanded
        """
        label = self.state.properties.get("label", "Header")
        flags = self.state.properties.get("flags", 0)

        is_open = bool(imgui.collapsing_header(label, flags))
        self.state.properties["is_open"] = is_open

        if is_open:
            self.trigger_callback("on_open")

        return is_open


class TabItemWidget(Widget):
    """Individual tab item widget.

    Must be added to a TabBarWidget via TabBarWidget.add_tab_item().
    Child widgets added via add_child() are rendered when the tab is active.
    """

    def __init__(
        self,
        widget_id: str,
        label: str = "Tab",
        closable: bool = False,
        **props,
    ):
        props["label"] = label
        props["closable"] = closable
        props["is_open"] = True
        super().__init__(widget_id, **props)
        self._children: list[Widget] = []

    def add_child(self, widget: "Widget") -> None:
        widget._parent_id = self.widget_id
        self._children.append(widget)

    def render(self) -> bool:
        """Render the tab item and its children. Must be called inside begin_tab_bar."""
        label = self.state.properties.get("label", "Tab")
        closable = self.state.properties.get("closable", False)
        is_open = self.state.properties.get("is_open", True)
        flags = self.state.properties.get("flags", 0)

        if not is_open:
            return False

        if closable:
            selected, is_open = imgui.begin_tab_item(label, True, flags)
            self.state.properties["is_open"] = is_open
        else:
            selected, _ = imgui.begin_tab_item(label, None, flags)

        if selected:
            for child in self._children:
                with contextlib.suppress(Exception):
                    child.render()
            imgui.end_tab_item()
            self.trigger_callback("on_select")

        return bool(selected)


class TabBarWidget(Widget):
    """Tab bar container widget.

    Add tab items via add_tab_item(). Each TabItemWidget can hold child
    widgets added via TabItemWidget.add_child().
    """

    def __init__(self, widget_id: str, **props):
        props["active_tab"] = None
        super().__init__(widget_id, **props)
        self._tab_items: list[TabItemWidget] = []

    def add_tab_item(self, tab_item: TabItemWidget) -> None:
        tab_item._parent_id = self.widget_id
        self._tab_items.append(tab_item)

    def render(self) -> str | None:
        """Render the tab bar and all owned tab items.

        Returns:
            The currently active tab id, or None
        """
        flags = self.state.properties.get("flags", 0)

        if imgui.begin_tab_bar(self.widget_id, flags):
            active_tab = None
            for tab_item in self._tab_items:
                with contextlib.suppress(Exception):
                    if tab_item.render():
                        active_tab = tab_item.widget_id
            self.state.properties["active_tab"] = active_tab
            imgui.end_tab_bar()
            return active_tab
        return None


class SeparatorWidget(Widget):
    """Separator line widget."""

    def __init__(self, widget_id: str, vertical: bool = False, **props):
        """Initialize separator.

        Args:
            widget_id: Unique widget identifier
            vertical: If True, render a vertical separator; otherwise horizontal
            **props: Additional properties
        """
        props["vertical"] = vertical
        super().__init__(widget_id, **props)

    def render(self) -> None:
        """Render the separator."""
        vertical = self.state.properties.get("vertical", False)

        if vertical:
            imgui.separator_text("")
        else:
            imgui.separator()


class SpacingWidget(Widget):
    """Spacing widget for layout."""

    def __init__(self, widget_id: str, count: int = 1, **props):
        """Initialize spacing widget.

        Args:
            widget_id: Unique widget identifier
            count: Number of blank lines to insert
            **props: Additional properties
        """
        props["count"] = count
        super().__init__(widget_id, **props)

    def render(self) -> None:
        """Render spacing."""
        count = self.state.properties.get("count", 1)
        for _ in range(count):
            imgui.spacing()


class DummyWidget(Widget):
    """Dummy (blank space) widget."""

    def __init__(
        self,
        widget_id: str,
        size: tuple[float, float] = (0, 0),
        **props,
    ):
        """Initialize dummy widget.

        Args:
            widget_id: Unique widget identifier
            size: Width and height of the blank space
            **props: Additional properties
        """
        props["size"] = size
        super().__init__(widget_id, **props)

    def render(self) -> None:
        """Render dummy space."""
        size = self.state.properties.get("size", (0, 0))
        imgui.dummy(imgui.ImVec2(*size))
