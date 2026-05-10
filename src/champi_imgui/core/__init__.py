"""Core module for Canvas state, widget infrastructure, and management."""

from champi_imgui.core.canvas import Canvas, CanvasManager
from champi_imgui.core.state import CanvasState, WidgetState
from champi_imgui.core.widget import Widget, WidgetFactory, WidgetRegistry

__all__ = [
    "Canvas",
    "CanvasManager",
    "CanvasState",
    "Widget",
    "WidgetFactory",
    "WidgetRegistry",
    "WidgetState",
]
