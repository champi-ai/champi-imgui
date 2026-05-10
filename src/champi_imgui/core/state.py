"""Canvas and widget state management using dataclasses.

Defines the core state structures for Canvas and Widget instances.
"""

from dataclasses import dataclass, field
from typing import Any

import blinker


@dataclass
class CanvasState:
    """State for a Canvas instance.

    Tracks the configuration and runtime state of a canvas window.
    """

    canvas_id: str
    """Unique identifier for the canvas"""

    title: str = "Canvas"
    """Window title"""

    size: tuple[int, int] = (800, 600)
    """Window size (width, height) in pixels"""

    position: tuple[int, int] | None = None
    """Window position (x, y) in pixels. None = auto-position"""

    visible: bool = True
    """Whether the canvas window is visible"""

    fps_target: int = 60
    """Target frames per second for rendering"""

    properties: dict[str, Any] = field(default_factory=dict)
    """Additional canvas properties (extensible)"""

    widgets: dict[str, "WidgetState"] = field(default_factory=dict)
    """Widget states managed by this canvas"""

    def to_dict(self) -> dict[str, Any]:
        """Convert state to dictionary for serialization.

        Returns:
            Dictionary representation of canvas state
        """
        return {
            "canvas_id": self.canvas_id,
            "title": self.title,
            "size": list(self.size),
            "position": list(self.position) if self.position else None,
            "visible": self.visible,
            "fps_target": self.fps_target,
            "properties": self.properties,
            "widgets": {wid: wstate.to_dict() for wid, wstate in self.widgets.items()},
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CanvasState":
        """Create CanvasState from dictionary.

        Args:
            data: Dictionary with canvas state data

        Returns:
            CanvasState instance
        """
        size = tuple(data.get("size", [800, 600]))
        position_list = data.get("position")
        position = tuple(position_list) if position_list else None

        return cls(
            canvas_id=data["canvas_id"],
            title=data.get("title", "Canvas"),
            size=size,
            position=position,
            visible=data.get("visible", True),
            fps_target=data.get("fps_target", 60),
            properties=data.get("properties", {}),
        )


@dataclass
class WidgetState:
    """State for a widget instance.

    Tracks all configuration and runtime state for individual widgets.
    """

    widget_id: str
    """Unique identifier for the widget"""

    widget_type: str
    """Type of widget (e.g., 'button', 'text', 'slider')"""

    properties: dict[str, Any] = field(default_factory=dict)
    """Widget-specific properties"""

    position: tuple[float, float] | None = None
    """Widget position (x, y) in pixels. None = auto-layout"""

    size: tuple[float, float] | None = None
    """Widget size (width, height) in pixels. None = auto-size"""

    visible: bool = True
    """Whether the widget is visible"""

    enabled: bool = True
    """Whether the widget is enabled for interaction"""

    parent: str | None = None
    """Parent widget ID for hierarchical widgets"""

    children: list[str] = field(default_factory=list)
    """Child widget IDs for container widgets"""

    callbacks: dict[str, str] = field(default_factory=dict)
    """Registered callback names by event type"""

    data_bindings: dict[str, Any] = field(default_factory=dict)
    """Data binding configuration"""

    def to_dict(self) -> dict[str, Any]:
        """Convert state to dictionary for serialization.

        Returns:
            Dictionary representation of widget state
        """
        return {
            "widget_id": self.widget_id,
            "widget_type": self.widget_type,
            "properties": self.properties.copy(),
            "position": list(self.position) if self.position else None,
            "size": list(self.size) if self.size else None,
            "visible": self.visible,
            "enabled": self.enabled,
            "parent": self.parent,
            "children": self.children.copy(),
            "callbacks": self.callbacks.copy(),
            "data_bindings": self.data_bindings.copy(),
        }


# Signals for state changes (using blinker for event system)
widget_created = blinker.signal("widget-created")
widget_updated = blinker.signal("widget-updated")
widget_deleted = blinker.signal("widget-deleted")
canvas_updated = blinker.signal("canvas-updated")
state_changed = blinker.signal("state-changed")
