"""Tests for PromptBroker, PromptRequest and PromptStatus."""

import threading
import time

import pytest

from champi_imgui.core.events import EventQueue
from champi_imgui.core.prompt_bridge import PromptBroker, PromptRequest, PromptStatus


def _req(
    widget_id: str = "ask", canvas_id: str = "c1", prompt: str = "hi"
) -> PromptRequest:
    return PromptRequest(
        request_id=PromptRequest.new_id(),
        canvas_id=canvas_id,
        widget_id=widget_id,
        prompt=prompt,
    )


class TestPromptRequest:
    def test_to_dict_fields(self) -> None:
        r = _req()
        r.metadata["k"] = 1
        d = r.to_dict()
        assert d["status"] == "pending"
        assert d["prompt"] == "hi"
        assert d["response"] is None
        assert d["metadata"] == {"k": 1}
        assert d["metadata"] is not r.metadata

    def test_terminal_states(self) -> None:
        r = _req()
        assert not r.is_terminal
        for s in (PromptStatus.ANSWERED, PromptStatus.CANCELLED, PromptStatus.EXPIRED):
            r.status = s
            assert r.is_terminal
        r.status = PromptStatus.CLAIMED
        assert not r.is_terminal


class TestSubmitAndWait:
    def test_wait_claims_oldest_pending(self) -> None:
        b = PromptBroker()
        first, second = _req(prompt="1"), _req(prompt="2")
        assert b.submit(first)
        assert b.submit(second)
        got = b.wait(0)
        assert got is first
        assert got.status is PromptStatus.CLAIMED
        assert got.claimed_at is not None
        assert b.wait(0) is second
        assert b.wait(0) is None

    def test_wait_timeout_returns_none(self) -> None:
        b = PromptBroker()
        start = time.monotonic()
        assert b.wait(0.05) is None
        assert time.monotonic() - start < 1.0

    def test_wait_filters_by_canvas(self) -> None:
        b = PromptBroker()
        other = _req(canvas_id="other")
        mine = _req(canvas_id="mine")
        b.submit(other)
        b.submit(mine)
        assert b.wait(0, canvas_id="mine") is mine
        assert b.wait(0, canvas_id="mine") is None
        assert b.wait(0) is other

    def test_four_waiters_one_submit_single_claim(self) -> None:
        b = PromptBroker()
        results: list[PromptRequest | None] = []
        errors: list[BaseException] = []
        lock = threading.Lock()

        def waiter() -> None:
            try:
                r = b.wait(1.0)
            except BaseException as e:  # pragma: no cover - surfaced via assert
                errors.append(e)
                return
            with lock:
                results.append(r)

        threads = [threading.Thread(target=waiter) for _ in range(4)]
        for t in threads:
            t.start()
        deadline = time.monotonic() + 1.0
        while b.to_diagnostics()["waiters"] < 4 and time.monotonic() < deadline:
            time.sleep(0.005)
        assert b.to_diagnostics()["waiters"] == 4

        request = _req()
        assert b.submit(request)
        for t in threads:
            t.join(timeout=3.0)

        assert not errors
        assert len(results) == 4
        claimed = [r for r in results if r is not None]
        assert claimed == [request]
        assert results.count(None) == 3
        assert b.to_diagnostics()["waiters"] == 0

    def test_submit_mirrors_event_to_queue(self) -> None:
        q = EventQueue()
        q.subscribe("ask", ["prompt"])
        b = PromptBroker(event_queue=q)
        r = _req()
        b.submit(r)
        events = q.poll()
        assert len(events) == 1
        assert events[0].event_type == "prompt"
        assert events[0].payload == {"request_id": r.request_id, "prompt": "hi"}


class TestPendingCap:
    def test_fourth_submit_rejected(self) -> None:
        b = PromptBroker(max_pending_per_widget=3)
        assert all(b.submit(_req()) for _ in range(3))
        assert b.submit(_req()) is False
        assert b.submit(_req(widget_id="other")) is True

    def test_cap_counts_claimed_and_frees_on_respond(self) -> None:
        b = PromptBroker(max_pending_per_widget=1)
        r = _req()
        assert b.submit(r)
        assert b.wait(0) is r
        assert b.submit(_req()) is False
        b.respond(r.request_id, "done")
        assert b.submit(_req()) is True

    def test_history_bounded(self) -> None:
        b = PromptBroker(max_history=2, max_pending_per_widget=10)
        first = _req()
        b.submit(first)
        b.submit(_req())
        b.submit(_req())
        assert b.get(first.request_id) is None
        assert b.to_diagnostics()["history"] == 2


class TestRespondAndCancel:
    def test_respond_sets_fields_and_calls_callback(self) -> None:
        b = PromptBroker()
        seen: list[PromptRequest] = []
        b.on_response("ask", seen.append)
        r = _req()
        b.submit(r)
        b.wait(0)
        out = b.respond(r.request_id, "answer")
        assert out is r
        assert r.status is PromptStatus.ANSWERED
        assert r.response == "answer"
        assert r.responded_at is not None
        assert seen == [r]

    def test_callback_runs_outside_lock(self) -> None:
        b = PromptBroker()
        r = _req()
        b.submit(r)

        def cb(request: PromptRequest) -> None:
            # Would deadlock if invoked while the broker lock were held.
            assert b.get(request.request_id) is request

        b.on_response("ask", cb)
        b.respond(r.request_id, "x")

    def test_callback_exception_is_swallowed(self) -> None:
        b = PromptBroker()
        r = _req()
        b.submit(r)

        def bad(_: PromptRequest) -> None:
            raise RuntimeError("boom")

        b.on_response("ask", bad)
        assert b.respond(r.request_id, "x").status is PromptStatus.ANSWERED

    def test_remove_callback(self) -> None:
        b = PromptBroker()
        seen: list[PromptRequest] = []
        b.on_response("ask", seen.append)
        b.remove_response_callback("ask")
        r = _req()
        b.submit(r)
        b.respond(r.request_id, "x")
        assert seen == []

    def test_respond_unknown_raises_keyerror(self) -> None:
        with pytest.raises(KeyError):
            PromptBroker().respond("nope", "x")

    def test_respond_after_cancel_raises_valueerror(self) -> None:
        b = PromptBroker()
        r = _req()
        b.submit(r)
        b.cancel(r.request_id)
        assert r.status is PromptStatus.CANCELLED
        with pytest.raises(ValueError, match="already cancelled"):
            b.respond(r.request_id, "x")

    def test_respond_with_invalid_status_raises(self) -> None:
        b = PromptBroker()
        r = _req()
        b.submit(r)
        with pytest.raises(ValueError):
            b.respond(r.request_id, "x", status=PromptStatus.PENDING)

    def test_cancel_for_widget_and_canvas(self) -> None:
        b = PromptBroker(max_pending_per_widget=10)
        a1, a2 = (
            _req(widget_id="a", canvas_id="c1"),
            _req(widget_id="a", canvas_id="c1"),
        )
        b1 = _req(widget_id="b", canvas_id="c1")
        c2 = _req(widget_id="c", canvas_id="c2")
        for r in (a1, a2, b1, c2):
            b.submit(r)
        b.wait(0)  # claims a1; still cancellable
        b.respond(a2.request_id, "done")  # terminal; not counted
        assert b.cancel_for_widget("a") == 1
        assert a1.status is PromptStatus.CANCELLED
        assert b.cancel_for_canvas("c1") == 1
        assert b1.status is PromptStatus.CANCELLED
        assert c2.status is PromptStatus.PENDING
        assert b.cancel_for_canvas("c1") == 0


class TestExpiry:
    def test_wait_never_returns_expired(self) -> None:
        b = PromptBroker(ttl_seconds=0.05)
        r = _req()
        b.submit(r)
        time.sleep(0.08)
        assert b.wait(0) is None
        assert r.status is PromptStatus.EXPIRED
        listed = b.list(status=PromptStatus.EXPIRED)
        assert listed == [r]

    def test_sweep_expired_notifies_callback(self) -> None:
        b = PromptBroker(ttl_seconds=0.01)
        seen: list[PromptRequest] = []
        b.on_response("ask", seen.append)
        r = _req()
        b.submit(r)
        time.sleep(0.02)
        assert b.sweep_expired() == 1
        assert seen == [r]
        assert b.sweep_expired() == 0

    def test_claimed_requests_do_not_expire(self) -> None:
        b = PromptBroker(ttl_seconds=0.01)
        r = _req()
        b.submit(r)
        assert b.wait(0) is r
        time.sleep(0.02)
        assert b.sweep_expired() == 0
        assert r.status is PromptStatus.CLAIMED


class TestListAndDiagnostics:
    def test_list_newest_first_with_filters(self) -> None:
        b = PromptBroker(max_pending_per_widget=10)
        r1, r2, r3 = _req(canvas_id="x"), _req(canvas_id="y"), _req(canvas_id="x")
        for r in (r1, r2, r3):
            b.submit(r)
        assert b.list() == [r3, r2, r1]
        assert b.list(canvas_id="x") == [r3, r1]
        b.wait(0)
        assert b.list(status=PromptStatus.CLAIMED) == [r1]
        assert b.list(status=PromptStatus.PENDING, canvas_id="y") == [r2]

    def test_diagnostics_track_state(self) -> None:
        b = PromptBroker(max_pending_per_widget=10)
        assert b.to_diagnostics() == {
            "pending": 0,
            "claimed": 0,
            "history": 0,
            "waiters": 0,
        }
        r1, r2 = _req(), _req()
        b.submit(r1)
        b.submit(r2)
        assert b.to_diagnostics()["pending"] == 2
        b.wait(0)
        d = b.to_diagnostics()
        assert (d["pending"], d["claimed"], d["history"]) == (1, 1, 2)
        b.respond(r1.request_id, "x")
        d = b.to_diagnostics()
        assert (d["pending"], d["claimed"], d["history"]) == (1, 0, 2)
