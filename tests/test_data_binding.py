"""Tests for DataStore, BindingManager, and ValidationManager."""

from unittest.mock import MagicMock, patch

import pytest

from champi_imgui.core.binding import BindingConfig, BindingManager, DataStore, ValidationManager


class TestDataStore:
    def test_set_and_get_simple(self) -> None:
        store = DataStore()
        store.set("key", 42)
        assert store.get("key") == 42

    def test_get_default(self) -> None:
        store = DataStore()
        assert store.get("missing") is None
        assert store.get("missing", "default") == "default"

    def test_set_nested(self) -> None:
        store = DataStore()
        store.set("user.name", "Alice")
        assert store.get("user.name") == "Alice"

    def test_set_deep_nested(self) -> None:
        store = DataStore()
        store.set("a.b.c", 100)
        assert store.get("a.b.c") == 100

    def test_get_nested_missing(self) -> None:
        store = DataStore()
        assert store.get("a.b.c", 0) == 0

    def test_subscribe_fires_on_set(self) -> None:
        store = DataStore()
        callback = MagicMock()
        store.subscribe("x", callback)
        store.set("x", 10)
        callback.assert_called_once()

    def test_unsubscribe(self) -> None:
        store = DataStore()
        callback = MagicMock()
        store.subscribe("x", callback)
        store.unsubscribe("x", callback)
        store.set("x", 10)
        callback.assert_not_called()

    def test_delete_simple(self) -> None:
        store = DataStore()
        store.set("key", 1)
        result = store.delete("key")
        assert result is True
        assert store.get("key") is None

    def test_delete_missing(self) -> None:
        store = DataStore()
        assert store.delete("nonexistent") is False

    def test_delete_nested(self) -> None:
        store = DataStore()
        store.set("a.b", 5)
        assert store.delete("a.b") is True
        assert store.get("a.b") is None

    def test_clear(self) -> None:
        store = DataStore()
        store.set("a", 1)
        store.set("b", 2)
        store.clear()
        assert store.get("a") is None
        assert store.get("b") is None

    def test_to_dict(self) -> None:
        store = DataStore()
        store.set("x", 1)
        d = store.to_dict()
        assert "x" in d

    def test_from_dict(self) -> None:
        store = DataStore()
        store.from_dict({"foo": "bar"})
        assert store.get("foo") == "bar"


class TestBindingManager:
    def test_init(self) -> None:
        store = DataStore()
        bm = BindingManager(store)
        assert bm.bindings == {}

    def test_bind_creates_binding(self) -> None:
        store = DataStore()
        bm = BindingManager(store)
        bm.bind("user.name", "label_1", "text")
        assert "user.name" in bm.bindings
        assert len(bm.bindings["user.name"]) == 1
        cfg = bm.bindings["user.name"][0]
        assert cfg.target_widget == "label_1"
        assert cfg.target_property == "text"

    def test_get_bindings_empty(self) -> None:
        store = DataStore()
        bm = BindingManager(store)
        assert bm.get_bindings("x") == []

    def test_unbind_all(self) -> None:
        store = DataStore()
        bm = BindingManager(store)
        bm.bind("path", "w1", "text")
        bm.unbind("path")
        assert "path" not in bm.bindings

    def test_unbind_specific_widget(self) -> None:
        store = DataStore()
        bm = BindingManager(store)
        bm.bind("path", "w1", "text")
        bm.bind("path", "w2", "value")
        bm.unbind("path", "w1")
        remaining = bm.get_bindings("path")
        assert len(remaining) == 1
        assert remaining[0].target_widget == "w2"

    def test_bind_with_transform(self) -> None:
        store = DataStore()
        bm = BindingManager(store)
        transform = lambda x: x * 2
        bm.bind("val", "widget", "prop", transform=transform)
        cfg = bm.bindings["val"][0]
        assert cfg.transform is transform

    def test_data_change_triggers_widget_update(self) -> None:
        store = DataStore()
        bm = BindingManager(store)
        bm.bind("score", "score_label", "text")
        with patch("champi_imgui.core.state.widget_updated") as mock_signal:
            store.set("score", 99)
        mock_signal.send.assert_called_once()

    def test_clear(self) -> None:
        store = DataStore()
        bm = BindingManager(store)
        bm.bind("a", "w", "p")
        bm.clear()
        assert bm.bindings == {}


class TestValidationManager:
    def test_validate_no_validators(self) -> None:
        vm = ValidationManager()
        assert vm.validate("path", "any_value") is True

    def test_validate_passes(self) -> None:
        vm = ValidationManager()
        vm.add_validator("age", lambda v: v > 0)
        assert vm.validate("age", 5) is True

    def test_validate_fails(self) -> None:
        vm = ValidationManager()
        vm.add_validator("age", lambda v: v > 0)
        assert vm.validate("age", -1) is False

    def test_validate_with_error_msg(self) -> None:
        vm = ValidationManager()
        vm.add_validator("age", lambda v: v > 0, error_msg="Must be positive")
        vm.validate("age", -1)
        assert vm.has_errors("age") is True
        assert "Must be positive" in vm.get_errors("age")

    def test_add_error(self) -> None:
        vm = ValidationManager()
        vm.add_error("field", "error msg")
        assert vm.has_errors("field") is True

    def test_get_errors_empty(self) -> None:
        vm = ValidationManager()
        assert vm.get_errors("field") == []

    def test_has_errors_global(self) -> None:
        vm = ValidationManager()
        assert vm.has_errors() is False
        vm.add_error("field", "err")
        assert vm.has_errors() is True

    def test_clear_errors_specific(self) -> None:
        vm = ValidationManager()
        vm.add_error("a", "err")
        vm.add_error("b", "err")
        vm.clear_errors("a")
        assert not vm.has_errors("a")
        assert vm.has_errors("b")

    def test_clear_errors_all(self) -> None:
        vm = ValidationManager()
        vm.add_error("a", "err")
        vm.add_error("b", "err")
        vm.clear_errors()
        assert not vm.has_errors()
