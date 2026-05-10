"""Comprehensive tests for menu and navigation widgets.

Tests cover all menu widgets:
- MenuBarWidget
- MenuWidget
- MenuItemWidget
- TreeNodeWidget
- TooltipWidget
- PopupWidget
- ContextMenuWidget
"""

from champi_imgui.core.state import WidgetState
from champi_imgui.widgets.menu import (
    ContextMenuWidget,
    MenuBarWidget,
    MenuItemWidget,
    MenuWidget,
    PopupWidget,
    TooltipWidget,
    TreeNodeWidget,
)

# ==============================================================================
# MenuBarWidget Tests
# ==============================================================================


def test_menu_bar_creation():
    """Test MenuBarWidget creation with default values."""
    widget = MenuBarWidget("menubar-1")

    assert widget.widget_id == "menubar-1"
    assert isinstance(widget.state, WidgetState)
    assert widget.state.widget_type == "MenuBarWidget"


def test_menu_bar_visibility():
    """Test MenuBarWidget visibility state."""
    widget = MenuBarWidget("menubar-2")

    assert widget.state.visible is True
    widget.set_visible(False)
    assert widget.state.visible is False


def test_menu_bar_serialization():
    """Test MenuBarWidget serialization."""
    widget = MenuBarWidget("menubar-3")

    data = widget.serialize()

    assert data["widget_id"] == "menubar-3"
    assert data["widget_type"] == "MenuBarWidget"


# ==============================================================================
# MenuWidget Tests
# ==============================================================================


def test_menu_widget_creation_defaults():
    """Test MenuWidget creation with default values."""
    widget = MenuWidget("menu-1")

    assert widget.widget_id == "menu-1"
    assert widget.state.widget_type == "MenuWidget"
    assert widget.state.properties["label"] == "Menu"
    assert widget.state.properties["enabled"] is True


def test_menu_widget_custom_label():
    """Test MenuWidget with custom label."""
    widget = MenuWidget("menu-2", label="File")

    assert widget.state.properties["label"] == "File"


def test_menu_widget_disabled():
    """Test MenuWidget with disabled state."""
    widget = MenuWidget("menu-3", label="Edit", enabled=False)

    assert widget.state.properties["enabled"] is False


def test_menu_widget_serialization():
    """Test MenuWidget serialization."""
    widget = MenuWidget("menu-4", label="View", enabled=True)

    data = widget.serialize()

    assert data["widget_id"] == "menu-4"
    assert data["widget_type"] == "MenuWidget"
    assert data["properties"]["label"] == "View"
    assert data["properties"]["enabled"] is True


# ==============================================================================
# MenuItemWidget Tests
# ==============================================================================


def test_menu_item_creation_defaults():
    """Test MenuItemWidget creation with default values."""
    widget = MenuItemWidget("item-1")

    assert widget.widget_id == "item-1"
    assert widget.state.widget_type == "MenuItemWidget"
    assert widget.state.properties["label"] == "Item"
    assert widget.state.properties["shortcut"] is None
    assert widget.state.properties["selected"] is False
    assert widget.state.properties["enabled"] is True


def test_menu_item_with_shortcut():
    """Test MenuItemWidget with keyboard shortcut."""
    widget = MenuItemWidget("item-2", label="Save", shortcut="Ctrl+S")

    assert widget.state.properties["label"] == "Save"
    assert widget.state.properties["shortcut"] == "Ctrl+S"


def test_menu_item_with_selection():
    """Test MenuItemWidget with selected state."""
    widget = MenuItemWidget("item-3", label="Toggle", selected=True)

    assert widget.state.properties["selected"] is True


def test_menu_item_disabled():
    """Test MenuItemWidget in disabled state."""
    widget = MenuItemWidget("item-4", label="Disabled", enabled=False)

    assert widget.state.properties["enabled"] is False


def test_menu_item_serialization():
    """Test MenuItemWidget serialization."""
    widget = MenuItemWidget("item-5", label="Open", shortcut="Ctrl+O", selected=False)

    data = widget.serialize()

    assert data["widget_id"] == "item-5"
    assert data["widget_type"] == "MenuItemWidget"
    assert data["properties"]["label"] == "Open"
    assert data["properties"]["shortcut"] == "Ctrl+O"


def test_menu_item_callback_registration():
    """Test that MenuItemWidget supports callback registration."""
    widget = MenuItemWidget("item-6", label="Exit")

    callback_called = []

    def on_click(selected):
        callback_called.append(selected)

    widget.register_callback("on_click", on_click)
    assert "on_click" in widget._callbacks


# ==============================================================================
# TreeNodeWidget Tests
# ==============================================================================


def test_tree_node_creation_defaults():
    """Test TreeNodeWidget creation with default values."""
    widget = TreeNodeWidget("tree-1")

    assert widget.widget_id == "tree-1"
    assert widget.state.widget_type == "TreeNodeWidget"
    assert widget.state.properties["label"] == "Node"
    assert widget.state.properties["is_open"] is False


def test_tree_node_custom_label():
    """Test TreeNodeWidget with custom label."""
    widget = TreeNodeWidget("tree-2", label="Children")

    assert widget.state.properties["label"] == "Children"


def test_tree_node_default_open():
    """Test TreeNodeWidget starting in open state."""
    widget = TreeNodeWidget("tree-3", label="Open Node", default_open=True)

    assert widget.state.properties["is_open"] is True


def test_tree_node_serialization():
    """Test TreeNodeWidget serialization."""
    widget = TreeNodeWidget("tree-4", label="Root", default_open=True)

    data = widget.serialize()

    assert data["widget_id"] == "tree-4"
    assert data["widget_type"] == "TreeNodeWidget"
    assert data["properties"]["label"] == "Root"
    assert data["properties"]["is_open"] is True


def test_tree_node_callback_registration():
    """Test that TreeNodeWidget supports callback registration."""
    widget = TreeNodeWidget("tree-5", label="Node")

    callback_called = []

    def on_open():
        callback_called.append(True)

    widget.register_callback("on_open", on_open)
    assert "on_open" in widget._callbacks


# ==============================================================================
# TooltipWidget Tests
# ==============================================================================


def test_tooltip_creation_defaults():
    """Test TooltipWidget creation with default values."""
    widget = TooltipWidget("tip-1")

    assert widget.widget_id == "tip-1"
    assert widget.state.widget_type == "TooltipWidget"
    assert widget.state.properties["text"] == ""


def test_tooltip_with_text():
    """Test TooltipWidget with custom text."""
    widget = TooltipWidget("tip-2", text="This is helpful")

    assert widget.state.properties["text"] == "This is helpful"


def test_tooltip_serialization():
    """Test TooltipWidget serialization."""
    widget = TooltipWidget("tip-3", text="Hover info")

    data = widget.serialize()

    assert data["widget_id"] == "tip-3"
    assert data["widget_type"] == "TooltipWidget"
    assert data["properties"]["text"] == "Hover info"


# ==============================================================================
# PopupWidget Tests
# ==============================================================================


def test_popup_creation_defaults():
    """Test PopupWidget creation with default values."""
    widget = PopupWidget("popup-1")

    assert widget.widget_id == "popup-1"
    assert widget.state.widget_type == "PopupWidget"
    assert widget.state.properties["title"] == "Popup"
    assert widget.state.properties["modal"] is False
    assert widget.state.properties["is_open"] is False


def test_popup_modal():
    """Test PopupWidget as modal dialog."""
    widget = PopupWidget("popup-2", title="Confirm", modal=True)

    assert widget.state.properties["title"] == "Confirm"
    assert widget.state.properties["modal"] is True


def test_popup_open_state():
    """Test PopupWidget open state tracking."""
    widget = PopupWidget("popup-3", title="Dialog")

    assert widget.state.properties["is_open"] is False
    widget.state.properties["is_open"] = True
    assert widget.state.properties["is_open"] is True


def test_popup_serialization():
    """Test PopupWidget serialization."""
    widget = PopupWidget("popup-4", title="Alert", modal=False)

    data = widget.serialize()

    assert data["widget_id"] == "popup-4"
    assert data["widget_type"] == "PopupWidget"
    assert data["properties"]["title"] == "Alert"
    assert data["properties"]["modal"] is False


# ==============================================================================
# ContextMenuWidget Tests
# ==============================================================================


def test_context_menu_creation():
    """Test ContextMenuWidget creation."""
    widget = ContextMenuWidget("ctx-1")

    assert widget.widget_id == "ctx-1"
    assert widget.state.widget_type == "ContextMenuWidget"


def test_context_menu_custom_flags():
    """Test ContextMenuWidget with custom popup flags."""
    widget = ContextMenuWidget("ctx-2", popup_flags=2)

    assert widget.state.properties["popup_flags"] == 2


def test_context_menu_serialization():
    """Test ContextMenuWidget serialization."""
    widget = ContextMenuWidget("ctx-3")

    data = widget.serialize()

    assert data["widget_id"] == "ctx-3"
    assert data["widget_type"] == "ContextMenuWidget"


# ==============================================================================
# __init__.py Export Tests
# ==============================================================================


def test_menu_widgets_exported_from_package():
    """Test that menu widgets are exported from the widgets package."""
    from champi_imgui.widgets import (
        ContextMenuWidget,
        MenuBarWidget,
        MenuItemWidget,
        MenuWidget,
        PopupWidget,
        TooltipWidget,
        TreeNodeWidget,
    )

    assert MenuBarWidget is not None
    assert MenuWidget is not None
    assert MenuItemWidget is not None
    assert TreeNodeWidget is not None
    assert TooltipWidget is not None
    assert PopupWidget is not None
    assert ContextMenuWidget is not None
