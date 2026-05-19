"""Thread-safe event queue for widget events.

Provides WidgetEvent dataclass and EventQueue for MCP clients to subscribe
to and poll widget events (clicks, value changes, etc.).
"""

from collections import deque
from dataclasses import dataclass, field
from threading import Lock
from time import time
from typing import Any


@dataclass
class WidgetEvent:
    """A single widget event with metadata."""

    widget_id: str
    event_type: str
    timestamp: float = field(default_factory=time)
    payload: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the event to a dictionary."""
        return {
            "widget_id": self.widget_id,
            "event_type": self.event_type,
            "timestamp": self.timestamp,
            "payload": self.payload,
        }


class EventQueue:
    """Thread-safe bounded event queue for widget events."""

    def __init__(self, max_size: int = 1000):
        """Initialize the event queue.

        Args:
            max_size: Maximum number of events to hold; oldest are dropped when full.
        """
        self._queue: deque[WidgetEvent] = deque(maxlen=max_size)
        self._subscriptions: dict[str, set[str]] = {}  # widget_id -> set of event_types
        self._lock = Lock()

    def subscribe(self, widget_id: str, event_types: list[str]) -> None:
        """Subscribe to events for a widget.

        Args:
            widget_id: Widget identifier to subscribe to
            event_types: Event type names to subscribe to (e.g. ['click', 'change'])
        """
        with self._lock:
            if widget_id not in self._subscriptions:
                self._subscriptions[widget_id] = set()
            self._subscriptions[widget_id].update(event_types)

    def unsubscribe(self, widget_id: str, event_types: list[str] | None = None) -> None:
        """Unsubscribe from events for a widget.

        Args:
            widget_id: Widget identifier
            event_types: Event types to remove, or None to remove all subscriptions
        """
        with self._lock:
            if widget_id not in self._subscriptions:
                return
            if event_types is None:
                del self._subscriptions[widget_id]
            else:
                self._subscriptions[widget_id].difference_update(event_types)
                if not self._subscriptions[widget_id]:
                    del self._subscriptions[widget_id]

    def push(
        self, widget_id: str, event_type: str, payload: dict | None = None
    ) -> None:
        """Push an event onto the queue if the widget+type is subscribed.

        Args:
            widget_id: Widget that fired the event
            event_type: Type of event that fired
            payload: Optional event payload data
        """
        with self._lock:
            if (
                widget_id in self._subscriptions
                and event_type in self._subscriptions[widget_id]
            ):
                self._queue.append(
                    WidgetEvent(widget_id, event_type, payload=payload or {})
                )

    def poll(
        self, widget_id: str | None = None, drain: bool = True
    ) -> list[WidgetEvent]:
        """Poll for queued events.

        Args:
            widget_id: Filter by widget ID, or None for all events
            drain: If True, remove returned events from the queue

        Returns:
            List of matching WidgetEvent instances
        """
        with self._lock:
            if widget_id is None:
                events = list(self._queue)
                if drain:
                    self._queue.clear()
            else:
                events = [e for e in self._queue if e.widget_id == widget_id]
                if drain:
                    self._queue = deque(
                        (e for e in self._queue if e.widget_id != widget_id),
                        maxlen=self._queue.maxlen,
                    )
            return events

    def get_subscriptions(self) -> dict[str, list[str]]:
        """Return a snapshot of all active subscriptions.

        Returns:
            Mapping of widget_id to list of subscribed event type names
        """
        with self._lock:
            return {k: list(v) for k, v in self._subscriptions.items()}

    def to_diagnostics(self) -> dict[str, Any]:
        """Return a snapshot of event queue state for diagnostics."""
        with self._lock:
            return {
                "pending_count": len(self._queue),
                "subscription_count": len(self._subscriptions),
            }
