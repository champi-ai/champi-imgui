"""Base widget class and registry.

Defines the core Widget ABC, WidgetFactory for widget creation,
and WidgetRegistry for widget lifecycle management.
"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

from loguru import logger

from champi_imgui.core.state import WidgetState, widget_created, widget_updated

_event_queue = None


def set_event_queue(queue: Any) -> None:
    """Wire a global EventQueue so all widget callbacks push events into it.

    Args:
        queue: An EventQueue instance (or None to detach)
    """
    global _event_queue
    _event_queue = queue


class Widget(ABC):
    """Base class for all widgets.

    All widget types must inherit from this class and implement
    the abstract render() method.
    """

    def __init__(self, widget_id: str, **props):
        """Initialize widget with ID and properties.

        Args:
            widget_id: Unique identifier for the widget
            **props: Widget-specific properties
        """
        self.widget_id = widget_id
        self.state = WidgetState(
            widget_id=widget_id, widget_type=self.__class__.__name__, properties=props
        )
        self._callbacks: dict[str, Callable] = {}

    @abstractmethod
    def render(self) -> Any:
        """Render the widget using ImGui calls.

        This method must be implemented by all widget subclasses.
        It should contain the ImGui rendering logic for the widget.

        Returns:
            Widget-specific return value (e.g., click state for Button,
            current value for Slider, etc.)
        """
        pass

    def update(self, **props) -> None:
        """Update widget properties.

        Args:
            **props: Properties to update
        """
        self.state.properties.update(props)
        widget_updated.send(self, widget=self)
        logger.debug(f"Updated widget {self.widget_id} with {props}")

    def set_visible(self, visible: bool) -> None:
        """Set widget visibility.

        Args:
            visible: Whether the widget should be visible
        """
        self.state.visible = visible

    def set_enabled(self, enabled: bool) -> None:
        """Set widget enabled state.

        Args:
            enabled: Whether the widget should be enabled for interaction
        """
        self.state.enabled = enabled

    def set_position(self, x: float, y: float) -> None:
        """Set widget position.

        Args:
            x: X coordinate in pixels
            y: Y coordinate in pixels
        """
        self.state.position = (x, y)

    def set_size(self, width: float, height: float) -> None:
        """Set widget size.

        Args:
            width: Width in pixels
            height: Height in pixels
        """
        self.state.size = (width, height)

    def register_callback(self, event: str, callback: Callable) -> None:
        """Register a callback function for an event.

        Args:
            event: Event name (e.g., 'click', 'change', 'hover')
            callback: Callback function to invoke
        """
        self._callbacks[event] = callback
        self.state.callbacks[event] = callback.__name__

    def trigger_callback(self, event: str, *args, **kwargs) -> Any:
        """Trigger a registered callback.

        Args:
            event: Event name
            *args: Positional arguments for callback
            **kwargs: Keyword arguments for callback

        Returns:
            Callback return value, or None if no callback registered
        """
        result = None
        if event in self._callbacks:
            result = self._callbacks[event](*args, **kwargs)
        if _event_queue is not None:
            _event_queue.push(self.widget_id, event, {"args": list(args)})
        return result

    def serialize(self) -> dict[str, Any]:
        """Serialize widget state to dictionary.

        Returns:
            Dictionary representation of widget state
        """
        return self.state.to_dict()


class WidgetFactory:
    """Factory for creating widget instances.

    Maintains a registry of widget types and creates instances on demand.
    """

    def __init__(self):
        """Initialize factory with empty creator registry."""
        self._creators: dict[str, type[Widget]] = {}

    def register(self, widget_type: str, creator: type[Widget]) -> None:
        """Register a widget creator class.

        Args:
            widget_type: String identifier for the widget type
                         (e.g., 'button', 'text', 'slider')
            creator: Widget class to use for creating instances
        """
        self._creators[widget_type] = creator
        logger.info(f"Registered widget type: {widget_type}")

    def create(self, widget_type: str, widget_id: str, **props) -> Widget:
        """Create a widget instance.

        Args:
            widget_type: Type of widget to create
            widget_id: Unique identifier for the new widget
            **props: Widget-specific properties

        Returns:
            Created widget instance

        Raises:
            ValueError: If widget_type is not registered
        """
        creator = self._creators.get(widget_type)
        if not creator:
            raise ValueError(f"Unknown widget type: {widget_type}")

        widget = creator(widget_id, **props)
        widget_created.send(self, widget=widget)
        logger.debug(f"Created widget {widget_id} of type {widget_type}")
        return widget

    def list_types(self) -> list[str]:
        """List all registered widget types.

        Returns:
            List of registered widget type names
        """
        return list(self._creators.keys())


class WidgetRegistry:
    """Registry for managing widget instances.

    Maintains a collection of widget instances and provides
    access to the widget factory.
    """

    def __init__(self):
        """Initialize registry with empty widget collection."""
        self._widgets: dict[str, Widget] = {}
        self._factory = WidgetFactory()
        self._register_drawing_widgets()

    def _register_drawing_widgets(self) -> None:
        """Register built-in drawing widget types with the factory."""
        from champi_imgui.widgets.drawing import (
            BrushWidget,
            CanvasMenuWidget,
            DrawingWidget,
        )

        self._factory.register("drawing_area", DrawingWidget)
        self._factory.register("brush_controls", BrushWidget)
        self._factory.register("canvas_menu", CanvasMenuWidget)

    @property
    def factory(self) -> WidgetFactory:
        """Get the widget factory.

        Returns:
            WidgetFactory instance for creating widgets
        """
        return self._factory

    def add(self, widget: Widget) -> None:
        """Add a widget to the registry.

        Args:
            widget: Widget instance to add
        """
        self._widgets[widget.widget_id] = widget
        logger.debug(f"Added widget {widget.widget_id} to registry")

    def get(self, widget_id: str) -> Widget | None:
        """Get a widget by ID.

        Args:
            widget_id: Widget identifier

        Returns:
            Widget instance if found, None otherwise
        """
        return self._widgets.get(widget_id)

    def remove(self, widget_id: str) -> bool:
        """Remove a widget from the registry.

        Args:
            widget_id: Widget identifier

        Returns:
            True if widget was removed, False if not found
        """
        if widget_id in self._widgets:
            del self._widgets[widget_id]
            logger.debug(f"Removed widget {widget_id} from registry")
            return True
        return False

    def list(self) -> list[str]:
        """List all widget IDs.

        Returns:
            List of widget identifiers
        """
        return list(self._widgets.keys())

    def get_all(self) -> dict[str, Widget]:
        """Get all widgets.

        Returns:
            Dictionary mapping widget IDs to Widget instances
        """
        return self._widgets.copy()

    def clear(self) -> None:
        """Clear all widgets from the registry."""
        self._widgets.clear()
        logger.debug("Cleared widget registry")
