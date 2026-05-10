"""Menu and navigation widgets.

This module contains widgets for building menus and navigation structures:
- MenuBarWidget: Main application menu bar
- MenuWidget: Dropdown menu container
- MenuItemWidget: Clickable menu item with optional shortcut and selection state
- TreeNodeWidget: Collapsible tree node for hierarchical data
- TooltipWidget: Hover tooltip
- PopupWidget: Modal and non-modal popup windows
- ContextMenuWidget: Right-click context menu
"""

from imgui_bundle import imgui

from champi_imgui.core.widget import Widget


class MenuBarWidget(Widget):
    """Main menu bar widget.

    Renders a menu bar anchored to the top of the application window.
    Use end_render() to finalize the menu bar after adding child menus.
    """

    def __init__(self, widget_id: str, **props):
        """Initialize menu bar.

        Args:
            widget_id: Unique widget identifier
            **props: Additional properties
        """
        super().__init__(widget_id, **props)

    def render(self) -> bool:
        """Render the menu bar.

        Returns:
            True if the menu bar is visible and rendering should continue
        """
        return imgui.begin_main_menu_bar()

    def end_render(self) -> None:
        """End menu bar rendering."""
        imgui.end_main_menu_bar()


class MenuWidget(Widget):
    """Dropdown menu container widget.

    Renders a collapsible menu that can contain menu items.
    Use end_render() to finalize the menu after adding items.
    """

    def __init__(
        self,
        widget_id: str,
        label: str = "Menu",
        enabled: bool = True,
        **props,
    ):
        """Initialize menu.

        Args:
            widget_id: Unique widget identifier
            label: Menu label text
            enabled: Whether the menu is enabled (clickable)
            **props: Additional properties
        """
        props["label"] = label
        props["enabled"] = enabled
        super().__init__(widget_id, **props)

    def render(self) -> bool:
        """Render the menu.

        Returns:
            True if the menu is open and items should be rendered
        """
        label = self.state.properties.get("label", "Menu")
        enabled = self.state.properties.get("enabled", True)

        return imgui.begin_menu(label, enabled)

    def end_render(self) -> None:
        """End menu rendering."""
        imgui.end_menu()


class MenuItemWidget(Widget):
    """Menu item widget.

    A clickable item within a MenuWidget. Supports keyboard shortcuts
    and toggle selection state.
    """

    def __init__(
        self,
        widget_id: str,
        label: str = "Item",
        shortcut: str | None = None,
        selected: bool = False,
        enabled: bool = True,
        **props,
    ):
        """Initialize menu item.

        Args:
            widget_id: Unique widget identifier
            label: Item label text
            shortcut: Optional keyboard shortcut hint (display only)
            selected: Whether the item is initially selected/checked
            enabled: Whether the item is enabled (clickable)
            **props: Additional properties
        """
        props["label"] = label
        props["shortcut"] = shortcut
        props["selected"] = selected
        props["enabled"] = enabled
        super().__init__(widget_id, **props)

    def render(self) -> tuple[bool, bool]:
        """Render the menu item.

        Returns:
            Tuple of (clicked, selected) booleans
        """
        label = self.state.properties.get("label", "Item")
        shortcut: str = self.state.properties.get("shortcut") or ""
        selected = self.state.properties.get("selected", False)
        enabled = self.state.properties.get("enabled", True)

        clicked, selected = imgui.menu_item(label, shortcut, selected, enabled)

        if clicked:
            self.state.properties["selected"] = selected
            self.trigger_callback("on_click", selected)

        return clicked, selected


class TreeNodeWidget(Widget):
    """Tree node widget for hierarchical data.

    Renders a collapsible tree node. Use end_render() to finalize
    child content when the node is open.
    """

    def __init__(
        self,
        widget_id: str,
        label: str = "Node",
        default_open: bool = False,
        **props,
    ):
        """Initialize tree node.

        Args:
            widget_id: Unique widget identifier
            label: Node label text
            default_open: Whether the node starts in the open state
            **props: Additional properties
        """
        props["label"] = label
        props["is_open"] = default_open
        super().__init__(widget_id, **props)

    def render(self) -> bool:
        """Render the tree node.

        Returns:
            True if the node is open and children should be rendered
        """
        label = self.state.properties.get("label", "Node")
        flags = self.state.properties.get("flags", 0)

        is_open = imgui.tree_node_ex(label, flags)
        self.state.properties["is_open"] = is_open

        if is_open:
            self.trigger_callback("on_open")

        return is_open

    def end_render(self) -> None:
        """End tree node rendering (calls tree_pop if open)."""
        if self.state.properties.get("is_open", False):
            imgui.tree_pop()


class TooltipWidget(Widget):
    """Tooltip widget.

    Displays a tooltip text, typically shown when hovering over an item.
    """

    def __init__(self, widget_id: str, text: str = "", **props):
        """Initialize tooltip.

        Args:
            widget_id: Unique widget identifier
            text: Tooltip text to display
            **props: Additional properties
        """
        props["text"] = text
        super().__init__(widget_id, **props)

    def render(self) -> None:
        """Render the tooltip."""
        text = self.state.properties.get("text", "")
        imgui.set_tooltip(text)


class PopupWidget(Widget):
    """Generic popup widget.

    Supports both modal and non-modal popup windows. Use open() to
    trigger the popup and close() to dismiss it programmatically.
    """

    def __init__(
        self,
        widget_id: str,
        title: str = "Popup",
        modal: bool = False,
        **props,
    ):
        """Initialize popup.

        Args:
            widget_id: Unique widget identifier
            title: Popup window title
            modal: If True, renders as a blocking modal dialog
            **props: Additional properties
        """
        props["title"] = title
        props["modal"] = modal
        props["is_open"] = False
        super().__init__(widget_id, **props)

    def open(self) -> None:
        """Open the popup."""
        self.state.properties["is_open"] = True
        imgui.open_popup(self.widget_id)

    def render(self) -> bool:
        """Render the popup.

        Returns:
            True if the popup is open and content should be rendered
        """
        title = self.state.properties.get("title", "Popup")
        modal = self.state.properties.get("modal", False)
        flags = self.state.properties.get("flags", 0)

        if modal:
            is_open, still_open = imgui.begin_popup_modal(title, True, flags)
            self.state.properties["is_open"] = still_open
        else:
            is_open = imgui.begin_popup(self.widget_id, flags)

        if is_open:
            imgui.end_popup()

        return is_open

    def close(self) -> None:
        """Close the popup."""
        self.state.properties["is_open"] = False
        imgui.close_current_popup()


class ContextMenuWidget(Widget):
    """Context menu (right-click menu) widget.

    Renders a popup menu triggered by right-clicking on an item.
    Use end_render() after adding menu items.
    """

    def __init__(self, widget_id: str, **props):
        """Initialize context menu.

        Args:
            widget_id: Unique widget identifier
            **props: Additional properties (popup_flags, etc.)
        """
        super().__init__(widget_id, **props)

    def render(self) -> bool:
        """Render the context menu.

        Returns:
            True if the context menu is open
        """
        popup_flags = self.state.properties.get("popup_flags", 1)
        return imgui.begin_popup_context_item(self.widget_id, popup_flags)

    def end_render(self) -> None:
        """End context menu rendering."""
        imgui.end_popup()
