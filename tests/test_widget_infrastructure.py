"""Comprehensive tests for widget infrastructure.

Tests cover:
- WidgetState dataclass and serialization
- Widget ABC base class
- WidgetFactory registration and creation
- WidgetRegistry management
- Signal emission
"""

import pytest

from champi_imgui.core.state import WidgetState, widget_created, widget_updated
from champi_imgui.core.widget import Widget, WidgetFactory, WidgetRegistry


# Test Widget implementations (using Mock prefix to avoid pytest class detection)
class MockTestWidget(Widget):
    """Concrete widget implementation for testing."""

    def __init__(self, widget_id: str, **props):
        super().__init__(widget_id, **props)
        self.render_count = 0

    def render(self) -> str:
        """Test render method."""
        self.render_count += 1
        return f"Rendered {self.widget_id}"


class MockAnotherWidget(Widget):
    """Another widget type for testing."""

    def render(self) -> int:
        return 42


# ============================================================================
# WidgetState Tests
# ============================================================================


def test_widget_state_creation():
    """Test WidgetState creation with required fields."""
    state = WidgetState(widget_id="test-1", widget_type="MockTestWidget")

    assert state.widget_id == "test-1"
    assert state.widget_type == "MockTestWidget"
    assert state.properties == {}
    assert state.position is None
    assert state.size is None
    assert state.visible is True
    assert state.enabled is True
    assert state.parent is None
    assert state.children == []
    assert state.callbacks == {}
    assert state.data_bindings == {}


def test_widget_state_with_all_fields():
    """Test WidgetState creation with all optional fields."""
    state = WidgetState(
        widget_id="test-2",
        widget_type="ButtonWidget",
        properties={"label": "Click me", "color": "red"},
        position=(10.0, 20.0),
        size=(100.0, 50.0),
        visible=False,
        enabled=False,
        parent="parent-1",
        children=["child-1", "child-2"],
        callbacks={"click": "on_click"},
        data_bindings={"value": "model.button_state"},
    )

    assert state.widget_id == "test-2"
    assert state.widget_type == "ButtonWidget"
    assert state.properties == {"label": "Click me", "color": "red"}
    assert state.position == (10.0, 20.0)
    assert state.size == (100.0, 50.0)
    assert state.visible is False
    assert state.enabled is False
    assert state.parent == "parent-1"
    assert state.children == ["child-1", "child-2"]
    assert state.callbacks == {"click": "on_click"}
    assert state.data_bindings == {"value": "model.button_state"}


def test_widget_state_serialization():
    """Test WidgetState to_dict serialization."""
    state = WidgetState(
        widget_id="test-3",
        widget_type="SliderWidget",
        properties={"min": 0, "max": 100, "value": 50},
        position=(5.0, 10.0),
        size=(200.0, 30.0),
    )

    data = state.to_dict()

    assert data["widget_id"] == "test-3"
    assert data["widget_type"] == "SliderWidget"
    assert data["properties"] == {"min": 0, "max": 100, "value": 50}
    assert data["position"] == [5.0, 10.0]  # Converted to list
    assert data["size"] == [200.0, 30.0]  # Converted to list
    assert data["visible"] is True
    assert data["enabled"] is True


def test_widget_state_serialization_with_none_values():
    """Test WidgetState serialization when position/size are None."""
    state = WidgetState(widget_id="test-4", widget_type="TextWidget")

    data = state.to_dict()

    assert data["position"] is None
    assert data["size"] is None


# ============================================================================
# Widget ABC Tests
# ============================================================================


def test_widget_abstract_instantiation():
    """Test that Widget ABC cannot be instantiated directly."""
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        Widget("test-widget")  # type: ignore


def test_widget_concrete_instantiation():
    """Test concrete widget instantiation."""
    widget = MockTestWidget("widget-1", label="Test", value=42)

    assert widget.widget_id == "widget-1"
    assert isinstance(widget.state, WidgetState)
    assert widget.state.widget_id == "widget-1"
    assert widget.state.widget_type == "MockTestWidget"
    assert widget.state.properties == {"label": "Test", "value": 42}


def test_widget_render_abstract():
    """Test that render() must be implemented."""
    widget = MockTestWidget("widget-2")
    result = widget.render()
    assert result == "Rendered widget-2"
    assert widget.render_count == 1


def test_widget_update():
    """Test widget property updates."""
    widget = MockTestWidget("widget-3", initial="value")

    # Track signal emission
    signals_received = []

    def on_update(sender, widget):
        signals_received.append((sender, widget))

    widget_updated.connect(on_update)

    try:
        # Update properties
        widget.update(new_prop="new_value", another=123)

        assert widget.state.properties["initial"] == "value"  # Original preserved
        assert widget.state.properties["new_prop"] == "new_value"
        assert widget.state.properties["another"] == 123

        # Check signal emitted
        assert len(signals_received) == 1
        assert signals_received[0][1] == widget
    finally:
        widget_updated.disconnect(on_update)


def test_widget_set_visible():
    """Test widget visibility setter."""
    widget = MockTestWidget("widget-4")

    assert widget.state.visible is True
    widget.set_visible(False)
    assert widget.state.visible is False
    widget.set_visible(True)
    assert widget.state.visible is True


def test_widget_set_enabled():
    """Test widget enabled setter."""
    widget = MockTestWidget("widget-5")

    assert widget.state.enabled is True
    widget.set_enabled(False)
    assert widget.state.enabled is False
    widget.set_enabled(True)
    assert widget.state.enabled is True


def test_widget_set_position():
    """Test widget position setter."""
    widget = MockTestWidget("widget-6")

    assert widget.state.position is None
    widget.set_position(10.0, 20.0)
    assert widget.state.position == (10.0, 20.0)
    widget.set_position(100.5, 200.5)
    assert widget.state.position == (100.5, 200.5)


def test_widget_set_size():
    """Test widget size setter."""
    widget = MockTestWidget("widget-7")

    assert widget.state.size is None
    widget.set_size(100.0, 50.0)
    assert widget.state.size == (100.0, 50.0)
    widget.set_size(200.0, 100.0)
    assert widget.state.size == (200.0, 100.0)


def test_widget_register_callback():
    """Test callback registration."""
    widget = MockTestWidget("widget-8")

    def on_click(event_data):
        return f"Clicked with {event_data}"

    widget.register_callback("click", on_click)

    assert "click" in widget._callbacks
    assert widget._callbacks["click"] == on_click
    assert widget.state.callbacks["click"] == "on_click"


def test_widget_trigger_callback():
    """Test callback triggering."""
    widget = MockTestWidget("widget-9")

    callback_results = []

    def on_change(value):
        callback_results.append(value)
        return value * 2

    widget.register_callback("change", on_change)

    # Trigger callback
    result = widget.trigger_callback("change", 42)
    assert result == 84
    assert callback_results == [42]

    # Trigger with kwargs
    result = widget.trigger_callback("change", value=10)
    assert result == 20


def test_widget_trigger_nonexistent_callback():
    """Test triggering callback that doesn't exist."""
    widget = MockTestWidget("widget-10")

    result = widget.trigger_callback("nonexistent")
    assert result is None


def test_widget_serialize():
    """Test widget serialization."""
    widget = MockTestWidget("widget-11", label="Serialize me", value=42)
    widget.set_position(10.0, 20.0)
    widget.set_size(100.0, 50.0)

    data = widget.serialize()

    assert data["widget_id"] == "widget-11"
    assert data["widget_type"] == "MockTestWidget"
    assert data["properties"] == {"label": "Serialize me", "value": 42}
    assert data["position"] == [10.0, 20.0]
    assert data["size"] == [100.0, 50.0]


# ============================================================================
# WidgetFactory Tests
# ============================================================================


def test_widget_factory_creation():
    """Test WidgetFactory instantiation."""
    factory = WidgetFactory()
    assert factory._creators == {}
    assert factory.list_types() == []


def test_widget_factory_register():
    """Test registering widget types."""
    factory = WidgetFactory()

    factory.register("test", MockTestWidget)
    assert "test" in factory._creators
    assert factory._creators["test"] == MockTestWidget

    factory.register("another", MockAnotherWidget)
    assert len(factory._creators) == 2
    assert factory.list_types() == ["test", "another"]


def test_widget_factory_create():
    """Test creating widgets via factory."""
    factory = WidgetFactory()
    factory.register("test", MockTestWidget)

    # Track signal emission
    signals_received = []

    def on_create(sender, widget):
        signals_received.append((sender, widget))

    widget_created.connect(on_create)

    try:
        widget = factory.create("test", "widget-12", label="Factory created")

        assert isinstance(widget, MockTestWidget)
        assert widget.widget_id == "widget-12"
        assert widget.state.properties["label"] == "Factory created"

        # Check signal emitted
        assert len(signals_received) == 1
        assert signals_received[0][1] == widget
    finally:
        widget_created.disconnect(on_create)


def test_widget_factory_create_unknown_type():
    """Test creating widget with unregistered type."""
    factory = WidgetFactory()

    with pytest.raises(ValueError, match="Unknown widget type: unknown"):
        factory.create("unknown", "widget-13")


def test_widget_factory_list_types():
    """Test listing registered widget types."""
    factory = WidgetFactory()

    assert factory.list_types() == []

    factory.register("button", MockTestWidget)
    factory.register("text", MockAnotherWidget)

    types = factory.list_types()
    assert sorted(types) == ["button", "text"]


# ============================================================================
# WidgetRegistry Tests
# ============================================================================


def test_widget_registry_creation():
    """Test WidgetRegistry instantiation."""
    registry = WidgetRegistry()

    assert registry._widgets == {}
    assert isinstance(registry.factory, WidgetFactory)


def test_widget_registry_add():
    """Test adding widgets to registry."""
    registry = WidgetRegistry()
    widget = MockTestWidget("widget-14")

    registry.add(widget)

    assert "widget-14" in registry._widgets
    assert registry._widgets["widget-14"] == widget


def test_widget_registry_get():
    """Test retrieving widgets from registry."""
    registry = WidgetRegistry()
    widget = MockTestWidget("widget-15")
    registry.add(widget)

    retrieved = registry.get("widget-15")
    assert retrieved == widget
    assert retrieved.widget_id == "widget-15"


def test_widget_registry_get_nonexistent():
    """Test retrieving non-existent widget."""
    registry = WidgetRegistry()

    result = registry.get("nonexistent")
    assert result is None


def test_widget_registry_remove():
    """Test removing widgets from registry."""
    registry = WidgetRegistry()
    widget = MockTestWidget("widget-16")
    registry.add(widget)

    assert registry.get("widget-16") is not None

    # Remove widget
    result = registry.remove("widget-16")
    assert result is True
    assert registry.get("widget-16") is None


def test_widget_registry_remove_nonexistent():
    """Test removing non-existent widget."""
    registry = WidgetRegistry()

    result = registry.remove("nonexistent")
    assert result is False


def test_widget_registry_list():
    """Test listing widget IDs."""
    registry = WidgetRegistry()

    assert registry.list() == []

    widget1 = MockTestWidget("widget-17")
    widget2 = MockTestWidget("widget-18")
    registry.add(widget1)
    registry.add(widget2)

    widget_ids = registry.list()
    assert sorted(widget_ids) == ["widget-17", "widget-18"]


def test_widget_registry_get_all():
    """Test getting all widgets."""
    registry = WidgetRegistry()

    widget1 = MockTestWidget("widget-19")
    widget2 = MockAnotherWidget("widget-20")
    registry.add(widget1)
    registry.add(widget2)

    all_widgets = registry.get_all()
    assert len(all_widgets) == 2
    assert all_widgets["widget-19"] == widget1
    assert all_widgets["widget-20"] == widget2

    # Verify it's a copy
    all_widgets["new-widget"] = MockTestWidget("widget-21")
    assert "new-widget" not in registry._widgets


def test_widget_registry_clear():
    """Test clearing all widgets."""
    registry = WidgetRegistry()

    widget1 = MockTestWidget("widget-22")
    widget2 = MockTestWidget("widget-23")
    registry.add(widget1)
    registry.add(widget2)

    assert len(registry._widgets) == 2

    registry.clear()

    assert len(registry._widgets) == 0
    assert registry.list() == []


def test_widget_registry_factory_integration():
    """Test full integration of factory with registry."""
    registry = WidgetRegistry()

    # Register widget type with factory
    registry.factory.register("test", MockTestWidget)

    # Create widget via factory
    widget = registry.factory.create("test", "widget-24", label="Integrated")

    # Add to registry
    registry.add(widget)

    # Retrieve from registry
    retrieved = registry.get("widget-24")
    assert retrieved == widget
    assert retrieved.state.properties["label"] == "Integrated"


# ============================================================================
# Coverage Tests (edge cases)
# ============================================================================


def test_widget_multiple_updates():
    """Test multiple consecutive updates."""
    widget = MockTestWidget("widget-25", initial="value")

    widget.update(first="1")
    widget.update(second="2")
    widget.update(third="3")

    assert widget.state.properties["initial"] == "value"
    assert widget.state.properties["first"] == "1"
    assert widget.state.properties["second"] == "2"
    assert widget.state.properties["third"] == "3"


def test_widget_update_overwrites():
    """Test that updates overwrite existing properties."""
    widget = MockTestWidget("widget-26", value=1)

    assert widget.state.properties["value"] == 1

    widget.update(value=2)
    assert widget.state.properties["value"] == 2

    widget.update(value=3)
    assert widget.state.properties["value"] == 3


def test_widget_registry_replace_widget():
    """Test replacing widget with same ID."""
    registry = WidgetRegistry()

    widget1 = MockTestWidget("same-id")
    widget2 = MockAnotherWidget("same-id")

    registry.add(widget1)
    assert isinstance(registry.get("same-id"), MockTestWidget)

    registry.add(widget2)
    assert isinstance(registry.get("same-id"), MockAnotherWidget)


def test_widget_state_property_mutation():
    """Test that properties dict is mutable."""
    state = WidgetState(widget_id="test", widget_type="MockTestWidget")

    assert state.properties == {}

    state.properties["key1"] = "value1"
    assert state.properties["key1"] == "value1"

    state.properties["key2"] = "value2"
    assert len(state.properties) == 2
