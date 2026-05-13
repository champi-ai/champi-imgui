"""Tests for EventQueue and WidgetEvent."""

import threading

from champi_imgui.core.events import EventQueue, WidgetEvent


class TestWidgetEvent:
    def test_to_dict_fields(self) -> None:
        event = WidgetEvent(widget_id="btn1", event_type="click", payload={"args": []})
        d = event.to_dict()
        assert d["widget_id"] == "btn1"
        assert d["event_type"] == "click"
        assert "timestamp" in d
        assert d["payload"] == {"args": []}

    def test_default_payload_is_empty(self) -> None:
        event = WidgetEvent(widget_id="w", event_type="change")
        assert event.payload == {}


class TestEventQueuePushPoll:
    def test_push_and_poll_all(self) -> None:
        q = EventQueue()
        q.subscribe("btn1", ["click"])
        q.push("btn1", "click", {"args": []})
        events = q.poll()
        assert len(events) == 1
        assert events[0].widget_id == "btn1"
        assert events[0].event_type == "click"

    def test_push_unsubscribed_event_not_stored(self) -> None:
        q = EventQueue()
        q.subscribe("btn1", ["click"])
        q.push("btn1", "change")  # not subscribed
        assert q.poll() == []

    def test_push_unsubscribed_widget_not_stored(self) -> None:
        q = EventQueue()
        q.push("unknown", "click")
        assert q.poll() == []

    def test_poll_with_widget_id_filter(self) -> None:
        q = EventQueue()
        q.subscribe("btn1", ["click"])
        q.subscribe("btn2", ["click"])
        q.push("btn1", "click")
        q.push("btn2", "click")
        events = q.poll(widget_id="btn1")
        assert len(events) == 1
        assert events[0].widget_id == "btn1"
        # btn2 event should still be present
        remaining = q.poll(widget_id="btn2")
        assert len(remaining) == 1

    def test_drain_false_leaves_events_in_queue(self) -> None:
        q = EventQueue()
        q.subscribe("btn1", ["click"])
        q.push("btn1", "click")
        first = q.poll(drain=False)
        second = q.poll(drain=False)
        assert len(first) == 1
        assert len(second) == 1

    def test_drain_true_clears_events(self) -> None:
        q = EventQueue()
        q.subscribe("btn1", ["click"])
        q.push("btn1", "click")
        q.poll(drain=True)
        assert q.poll() == []

    def test_drain_widget_id_filter_clears_only_that_widget(self) -> None:
        q = EventQueue()
        q.subscribe("a", ["click"])
        q.subscribe("b", ["click"])
        q.push("a", "click")
        q.push("b", "click")
        q.poll(widget_id="a", drain=True)
        remaining = q.poll()
        assert len(remaining) == 1
        assert remaining[0].widget_id == "b"


class TestEventQueueSubscriptions:
    def test_subscribe_and_get_subscriptions(self) -> None:
        q = EventQueue()
        q.subscribe("btn1", ["click", "hover"])
        subs = q.get_subscriptions()
        assert "btn1" in subs
        assert set(subs["btn1"]) == {"click", "hover"}

    def test_unsubscribe_specific_events(self) -> None:
        q = EventQueue()
        q.subscribe("btn1", ["click", "hover"])
        q.unsubscribe("btn1", ["hover"])
        subs = q.get_subscriptions()
        assert set(subs["btn1"]) == {"click"}

    def test_unsubscribe_all_events_removes_widget(self) -> None:
        q = EventQueue()
        q.subscribe("btn1", ["click"])
        q.unsubscribe("btn1")
        assert "btn1" not in q.get_subscriptions()

    def test_unsubscribe_specific_removes_widget_when_empty(self) -> None:
        q = EventQueue()
        q.subscribe("btn1", ["click"])
        q.unsubscribe("btn1", ["click"])
        assert "btn1" not in q.get_subscriptions()

    def test_unsubscribe_unknown_widget_is_noop(self) -> None:
        q = EventQueue()
        q.unsubscribe("nonexistent")  # should not raise

    def test_subscribe_multiple_calls_accumulate(self) -> None:
        q = EventQueue()
        q.subscribe("w", ["click"])
        q.subscribe("w", ["change"])
        subs = q.get_subscriptions()
        assert set(subs["w"]) == {"click", "change"}


class TestEventQueueMaxSize:
    def test_overflow_drops_oldest(self) -> None:
        q = EventQueue(max_size=3)
        q.subscribe("w", ["click"])
        for _ in range(5):
            q.push("w", "click")
        events = q.poll()
        assert len(events) == 3


class TestEventQueueThreadSafety:
    def test_concurrent_push_and_poll(self) -> None:
        q = EventQueue()
        q.subscribe("w", ["click"])
        errors: list[Exception] = []

        def push_many() -> None:
            try:
                for _ in range(100):
                    q.push("w", "click")
            except Exception as exc:
                errors.append(exc)

        def poll_many() -> None:
            try:
                for _ in range(50):
                    q.poll()
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=push_many) for _ in range(4)]
        threads += [threading.Thread(target=poll_many) for _ in range(2)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert errors == []

    def test_concurrent_subscribe_and_push(self) -> None:
        q = EventQueue()
        errors: list[Exception] = []

        def subscribe_and_push() -> None:
            try:
                q.subscribe("w", ["click"])
                q.push("w", "click")
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=subscribe_and_push) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert errors == []
