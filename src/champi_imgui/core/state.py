"""Canvas state management using dataclasses.

Defines the core state structure for Canvas instances.
"""

from dataclasses import dataclass, field
from typing import Any


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
