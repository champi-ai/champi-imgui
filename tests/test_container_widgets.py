"""Comprehensive tests for container and layout widgets.

Tests cover all 9 container widgets:
- WindowWidget
- ChildWindowWidget
- GroupWidget
- CollapsingHeaderWidget
- TabBarWidget
- TabItemWidget
- SeparatorWidget
- SpacingWidget
- DummyWidget
"""

from champi_imgui.core.state import WidgetState
from champi_imgui.widgets.container import (
    ChildWindowWidget,
    CollapsingHeaderWidget,
    DummyWidget,
    GroupWidget,
    SeparatorWidget,
    SpacingWidget,
    TabBarWidget,
    TabItemWidget,
    WindowWidget,
)

# ==============================================================================
# WindowWidget Tests
# ==============================================================================


def test_window_widget_creation():
    """Test WindowWidget creation with default values."""
    widget = WindowWidget("win-1")

    assert widget.widget_id == "win-1"
    assert isinstance(widget.state, WidgetState)
    assert widget.state.widget_type == "WindowWidget"
    assert widget.state.properties["title"] == "Window"
    assert widget.state.properties["closable"] is True
    assert widget.state.properties["is_open"] is True


def test_window_widget_custom_title():
    """Test WindowWidget with a custom title."""
    widget = WindowWidget("win-2", title="My App")

    assert widget.state.properties["title"] == "My App"


def test_window_widget_not_closable():
    """Test WindowWidget created as non-closable."""
    widget = WindowWidget("win-3", closable=False)

    assert widget.state.properties["closable"] is False


def test_window_widget_visibility():
    """Test WindowWidget respects visible flag."""
    widget = WindowWidget("win-4")

    assert widget.state.visible is True
    widget.set_visible(False)
    assert widget.state.visible is False


def test_window_widget_callback_registration():
    """Test WindowWidget can register callbacks."""
    widget = WindowWidget("win-5")

    widget.register_callback("on_close", lambda: None)
    assert "on_close" in widget._callbacks


# ==============================================================================
# ChildWindowWidget Tests
# ==============================================================================


def test_child_window_widget_creation():
    """Test ChildWindowWidget creation with default values."""
    widget = ChildWindowWidget("child-1")

    assert widget.widget_id == "child-1"
    assert isinstance(widget.state, WidgetState)
    assert widget.state.widget_type == "ChildWindowWidget"
    assert widget.state.properties["size"] == (0, 0)
    assert widget.state.properties["border"] is False


def test_child_window_widget_custom_size():
    """Test ChildWindowWidget with custom size."""
    widget = ChildWindowWidget("child-2", size=(200, 150))

    assert widget.state.properties["size"] == (200, 150)


def test_child_window_widget_with_border():
    """Test ChildWindowWidget with border enabled."""
    widget = ChildWindowWidget("child-3", border=True)

    assert widget.state.properties["border"] is True


# ==============================================================================
# GroupWidget Tests
# ==============================================================================


def test_group_widget_creation():
    """Test GroupWidget creation."""
    widget = GroupWidget("group-1")

    assert widget.widget_id == "group-1"
    assert isinstance(widget.state, WidgetState)
    assert widget.state.widget_type == "GroupWidget"


def test_group_widget_visibility():
    """Test GroupWidget visibility flag."""
    widget = GroupWidget("group-2")

    assert widget.state.visible is True
    widget.set_visible(False)
    assert widget.state.visible is False


# ==============================================================================
# CollapsingHeaderWidget Tests
# ==============================================================================


def test_collapsing_header_creation():
    """Test CollapsingHeaderWidget creation with default values."""
    widget = CollapsingHeaderWidget("header-1")

    assert widget.widget_id == "header-1"
    assert isinstance(widget.state, WidgetState)
    assert widget.state.widget_type == "CollapsingHeaderWidget"
    assert widget.state.properties["label"] == "Header"
    assert widget.state.properties["is_open"] is False


def test_collapsing_header_custom_label():
    """Test CollapsingHeaderWidget with custom label."""
    widget = CollapsingHeaderWidget("header-2", label="Settings")

    assert widget.state.properties["label"] == "Settings"


def test_collapsing_header_default_open():
    """Test CollapsingHeaderWidget starts open when default_open=True."""
    widget = CollapsingHeaderWidget("header-3", default_open=True)

    assert widget.state.properties["is_open"] is True


def test_collapsing_header_callback_registration():
    """Test CollapsingHeaderWidget can register on_open callback."""
    widget = CollapsingHeaderWidget("header-4")
    called = []

    widget.register_callback("on_open", lambda: called.append(True))
    assert "on_open" in widget._callbacks


# ==============================================================================
# TabBarWidget Tests
# ==============================================================================


def test_tab_bar_widget_creation():
    """Test TabBarWidget creation with default values."""
    widget = TabBarWidget("tabbar-1")

    assert widget.widget_id == "tabbar-1"
    assert isinstance(widget.state, WidgetState)
    assert widget.state.widget_type == "TabBarWidget"
    assert widget.state.properties["active_tab"] is None


# ==============================================================================
# TabItemWidget Tests
# ==============================================================================


def test_tab_item_widget_creation():
    """Test TabItemWidget creation with default values."""
    widget = TabItemWidget("tab-1")

    assert widget.widget_id == "tab-1"
    assert isinstance(widget.state, WidgetState)
    assert widget.state.widget_type == "TabItemWidget"
    assert widget.state.properties["label"] == "Tab"
    assert widget.state.properties["closable"] is False
    assert widget.state.properties["is_open"] is True


def test_tab_item_widget_custom_label():
    """Test TabItemWidget with custom label."""
    widget = TabItemWidget("tab-2", label="Overview")

    assert widget.state.properties["label"] == "Overview"


def test_tab_item_widget_closable():
    """Test TabItemWidget with close button enabled."""
    widget = TabItemWidget("tab-3", closable=True)

    assert widget.state.properties["closable"] is True


def test_tab_item_widget_callback_registration():
    """Test TabItemWidget can register on_select callback."""
    widget = TabItemWidget("tab-4")

    widget.register_callback("on_select", lambda: None)
    assert "on_select" in widget._callbacks


# ==============================================================================
# SeparatorWidget Tests
# ==============================================================================


def test_separator_widget_creation():
    """Test SeparatorWidget creation with default values."""
    widget = SeparatorWidget("sep-1")

    assert widget.widget_id == "sep-1"
    assert isinstance(widget.state, WidgetState)
    assert widget.state.widget_type == "SeparatorWidget"
    assert widget.state.properties["vertical"] is False


def test_separator_widget_vertical():
    """Test SeparatorWidget created as vertical."""
    widget = SeparatorWidget("sep-2", vertical=True)

    assert widget.state.properties["vertical"] is True


# ==============================================================================
# SpacingWidget Tests
# ==============================================================================


def test_spacing_widget_creation():
    """Test SpacingWidget creation with default values."""
    widget = SpacingWidget("spacing-1")

    assert widget.widget_id == "spacing-1"
    assert isinstance(widget.state, WidgetState)
    assert widget.state.widget_type == "SpacingWidget"
    assert widget.state.properties["count"] == 1


def test_spacing_widget_custom_count():
    """Test SpacingWidget with custom count."""
    widget = SpacingWidget("spacing-2", count=5)

    assert widget.state.properties["count"] == 5


# ==============================================================================
# DummyWidget Tests
# ==============================================================================


def test_dummy_widget_creation():
    """Test DummyWidget creation with default values."""
    widget = DummyWidget("dummy-1")

    assert widget.widget_id == "dummy-1"
    assert isinstance(widget.state, WidgetState)
    assert widget.state.widget_type == "DummyWidget"
    assert widget.state.properties["size"] == (0, 0)


def test_dummy_widget_custom_size():
    """Test DummyWidget with custom size."""
    widget = DummyWidget("dummy-2", size=(100, 50))

    assert widget.state.properties["size"] == (100, 50)


# ==============================================================================
# Cross-widget Tests
# ==============================================================================


def test_all_container_widgets_have_state():
    """Test that all container widgets have proper WidgetState."""
    widgets = [
        WindowWidget("w1"),
        ChildWindowWidget("w2"),
        GroupWidget("w3"),
        CollapsingHeaderWidget("w4"),
        TabBarWidget("w5"),
        TabItemWidget("w6"),
        SeparatorWidget("w7"),
        SpacingWidget("w8"),
        DummyWidget("w9"),
    ]

    for widget in widgets:
        assert isinstance(widget.state, WidgetState)
        assert widget.state.widget_id is not None
        assert widget.state.widget_type is not None


def test_all_container_widgets_are_visible_by_default():
    """Test that all container widgets start visible."""
    widgets = [
        WindowWidget("w1"),
        ChildWindowWidget("w2"),
        GroupWidget("w3"),
        CollapsingHeaderWidget("w4"),
        TabBarWidget("w5"),
        TabItemWidget("w6"),
        SeparatorWidget("w7"),
        SpacingWidget("w8"),
        DummyWidget("w9"),
    ]

    for widget in widgets:
        assert widget.state.visible is True
