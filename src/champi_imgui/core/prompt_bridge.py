"""Prompt broker for UI-initiated prompt requests.

The PromptBroker mediates prompt requests between the ImGui render thread
(producers: a widget the user pressed) and MCP tool consumers (long-poll
tools or the sampling bridge). It is the authoritative store for the request
lifecycle; the EventQueue only receives a lightweight mirror event.

Thread-safety: all state is guarded by a single threading.Condition. Response
callbacks registered by widgets are invoked outside the lock and must only
mutate plain Python attributes on the widget (never call ImGui). Those
assignments are atomic under CPython's GIL and the render thread tolerates
seeing a stale value for one frame.
"""

from __future__ import annotations

import threading
import uuid
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from time import time
from typing import Any

from loguru import logger

# ``PromptBroker.list`` shadows the builtin inside the class body; alias it for hints.
_List = list


class PromptStatus(str, Enum):
    """Lifecycle state of a prompt request."""

    PENDING = "pending"
    CLAIMED = "claimed"
    ANSWERED = "answered"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


_TERMINAL = frozenset(
    {PromptStatus.ANSWERED, PromptStatus.CANCELLED, PromptStatus.EXPIRED}
)


@dataclass
class PromptRequest:
    """A single prompt submitted from the UI."""

    request_id: str
    canvas_id: str
    widget_id: str
    prompt: str
    user_input: str | None = None
    created_at: float = field(default_factory=time)
    status: PromptStatus = PromptStatus.PENDING
    claimed_at: float | None = None
    response: str | None = None
    responded_at: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def new_id() -> str:
        """Generate a request identifier."""
        return uuid.uuid4().hex

    @property
    def is_terminal(self) -> bool:
        """Whether the request can no longer change state."""
        return self.status in _TERMINAL

    def to_dict(self) -> dict[str, Any]:
        """Serialize the request to a dictionary."""
        return {
            "request_id": self.request_id,
            "canvas_id": self.canvas_id,
            "widget_id": self.widget_id,
            "prompt": self.prompt,
            "user_input": self.user_input,
            "created_at": self.created_at,
            "status": self.status.value,
            "claimed_at": self.claimed_at,
            "response": self.response,
            "responded_at": self.responded_at,
            "metadata": dict(self.metadata),
        }


ResponseCallback = Callable[[PromptRequest], None]


class PromptBroker:
    """Thread-safe store and hand-off point for prompt requests."""

    def __init__(
        self,
        max_history: int = 200,
        ttl_seconds: float = 600.0,
        max_pending_per_widget: int = 3,
        event_queue: Any | None = None,
    ):
        """Initialize the broker.

        Args:
            max_history: Maximum number of requests kept; oldest are dropped.
            ttl_seconds: Pending requests older than this become EXPIRED.
            max_pending_per_widget: Cap on non-terminal requests per widget.
            event_queue: Optional EventQueue receiving mirror "prompt" events.
        """
        self.max_history = max_history
        self.ttl_seconds = ttl_seconds
        self.max_pending_per_widget = max_pending_per_widget
        self._event_queue = event_queue
        self._requests: deque[PromptRequest] = deque(maxlen=max_history)
        self._by_id: dict[str, PromptRequest] = {}
        self._callbacks: dict[str, ResponseCallback] = {}
        self._cond = threading.Condition()
        self._waiters = 0

    # ------------------------------------------------------------------
    # Producer side (render thread)
    # ------------------------------------------------------------------

    def submit(self, request: PromptRequest) -> bool:
        """Store a new request and wake waiters.

        Returns:
            False when the widget already has ``max_pending_per_widget``
            non-terminal requests; the request is then discarded.
        """
        with self._cond:
            self._sweep_expired_locked()
            open_count = sum(
                1
                for r in self._requests
                if r.widget_id == request.widget_id and not r.is_terminal
            )
            if open_count >= self.max_pending_per_widget:
                logger.warning(
                    f"Prompt request from '{request.widget_id}' rejected: "
                    f"{open_count} requests already pending"
                )
                return False
            if len(self._requests) == self._requests.maxlen:
                dropped = self._requests[0]
                self._by_id.pop(dropped.request_id, None)
            self._requests.append(request)
            self._by_id[request.request_id] = request
            self._cond.notify_all()

        if self._event_queue is not None:
            self._event_queue.push(
                request.widget_id,
                "prompt",
                {"request_id": request.request_id, "prompt": request.prompt},
            )
        return True

    # ------------------------------------------------------------------
    # Consumer side (MCP thread / worker)
    # ------------------------------------------------------------------

    def wait(
        self, timeout: float, canvas_id: str | None = None
    ) -> PromptRequest | None:
        """Block until a pending request is available, then claim it.

        Exactly one waiter receives a given request. Expired requests are
        swept before the predicate is evaluated so they are never returned.

        Returns:
            The oldest pending request (now CLAIMED), or None on timeout.
        """

        def _next_pending() -> PromptRequest | None:
            self._sweep_expired_locked()
            for r in self._requests:
                if r.status is PromptStatus.PENDING and (
                    canvas_id is None or r.canvas_id == canvas_id
                ):
                    return r
            return None

        with self._cond:
            self._waiters += 1
            try:
                found = self._cond.wait_for(
                    lambda: _next_pending() is not None, timeout=max(0.0, timeout)
                )
                if not found:
                    return None
                request = _next_pending()
                assert request is not None
                request.status = PromptStatus.CLAIMED
                request.claimed_at = time()
                return request
            finally:
                self._waiters -= 1

    def respond(
        self,
        request_id: str,
        response: str,
        status: PromptStatus = PromptStatus.ANSWERED,
    ) -> PromptRequest:
        """Record a response and notify the owning widget.

        Raises:
            KeyError: Unknown request id.
            ValueError: Request already in a terminal state, or bad status.
        """
        if status not in (PromptStatus.ANSWERED, PromptStatus.CANCELLED):
            raise ValueError(f"Invalid response status '{status.value}'")
        with self._cond:
            request = self._by_id.get(request_id)
            if request is None:
                raise KeyError(f"Prompt request '{request_id}' not found")
            if request.is_terminal:
                raise ValueError(
                    f"Prompt request '{request_id}' is already {request.status.value}"
                )
            request.response = response
            request.responded_at = time()
            request.status = status
            callback = self._callbacks.get(request.widget_id)
        self._notify(callback, request)
        return request

    def cancel(self, request_id: str) -> PromptRequest:
        """Cancel a single non-terminal request.

        Raises:
            KeyError: Unknown request id.
            ValueError: Request already terminal.
        """
        return self.respond(request_id, "", status=PromptStatus.CANCELLED)

    def cancel_for_widget(self, widget_id: str) -> int:
        """Cancel every open request for a widget. Returns the count."""
        return self._cancel_where(lambda r: r.widget_id == widget_id)

    def cancel_for_canvas(self, canvas_id: str) -> int:
        """Cancel every open request for a canvas. Returns the count."""
        return self._cancel_where(lambda r: r.canvas_id == canvas_id)

    def get(self, request_id: str) -> PromptRequest | None:
        """Look up a request by id."""
        with self._cond:
            return self._by_id.get(request_id)

    def list(
        self,
        status: PromptStatus | None = None,
        canvas_id: str | None = None,
    ) -> _List[PromptRequest]:
        """Return matching requests, newest first."""
        with self._cond:
            self._sweep_expired_locked()
            return [
                r
                for r in reversed(self._requests)
                if (status is None or r.status is status)
                and (canvas_id is None or r.canvas_id == canvas_id)
            ]

    def sweep_expired(self) -> int:
        """Mark pending requests older than ``ttl_seconds`` as EXPIRED."""
        with self._cond:
            expired = self._sweep_expired_locked()
        for request in expired:
            self._notify(self._callbacks.get(request.widget_id), request)
        return len(expired)

    # ------------------------------------------------------------------
    # Widget hookup
    # ------------------------------------------------------------------

    def on_response(self, widget_id: str, callback: ResponseCallback) -> None:
        """Register the callback invoked when a widget's request reaches a terminal state."""
        with self._cond:
            self._callbacks[widget_id] = callback

    def remove_response_callback(self, widget_id: str) -> None:
        """Remove a widget's response callback."""
        with self._cond:
            self._callbacks.pop(widget_id, None)

    def to_diagnostics(self) -> dict[str, Any]:
        """Return a snapshot of broker state for diagnostics."""
        with self._cond:
            return {
                "pending": sum(
                    1 for r in self._requests if r.status is PromptStatus.PENDING
                ),
                "claimed": sum(
                    1 for r in self._requests if r.status is PromptStatus.CLAIMED
                ),
                "history": len(self._requests),
                "waiters": self._waiters,
            }

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _sweep_expired_locked(self) -> _List[PromptRequest]:
        """Expire stale pending requests. Caller must hold the lock."""
        cutoff = time() - self.ttl_seconds
        expired = []
        for r in self._requests:
            if r.status is PromptStatus.PENDING and r.created_at < cutoff:
                r.status = PromptStatus.EXPIRED
                r.responded_at = time()
                expired.append(r)
        return expired

    def _cancel_where(self, predicate: Callable[[PromptRequest], bool]) -> int:
        with self._cond:
            cancelled = []
            for r in self._requests:
                if not r.is_terminal and predicate(r):
                    r.status = PromptStatus.CANCELLED
                    r.responded_at = time()
                    cancelled.append(r)
            callbacks = [(self._callbacks.get(r.widget_id), r) for r in cancelled]
        for callback, request in callbacks:
            self._notify(callback, request)
        return len(cancelled)

    @staticmethod
    def _notify(callback: ResponseCallback | None, request: PromptRequest) -> None:
        if callback is None:
            return
        try:
            callback(request)
        except Exception as e:
            logger.error(
                f"Prompt response callback for '{request.widget_id}' failed: {e}"
            )
