"""Data binding system for reactive UI updates."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from blinker import Signal
from loguru import logger


@dataclass
class BindingConfig:
    """Configuration for a data binding."""

    source_path: str
    target_widget: str
    target_property: str
    transform: Callable[[Any], Any] | None = None
    bidirectional: bool = False


class DataStore:
    """Reactive data store with change notifications."""

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}
        self._signals: dict[str, Signal] = {}
        logger.debug("Initialized DataStore")

    def set(self, path: str, value: Any) -> None:
        """Set a value at dot-notation path and notify listeners."""
        self._set_nested(path, value)
        if path not in self._signals:
            self._signals[path] = Signal()
        self._signals[path].send(self, path=path, value=value)
        logger.debug(f"DataStore set: {path} = {value}")

    def get(self, path: str, default: Any = None) -> Any:
        """Get a value at dot-notation path."""
        return self._get_nested(path, default)

    def subscribe(self, path: str, callback: Callable) -> None:
        """Subscribe to changes at a path."""
        if path not in self._signals:
            self._signals[path] = Signal()
        self._signals[path].connect(callback)

    def unsubscribe(self, path: str, callback: Callable) -> None:
        """Unsubscribe from changes at a path."""
        if path in self._signals:
            self._signals[path].disconnect(callback)

    def delete(self, path: str) -> bool:
        """Delete a value. Returns True if deleted."""
        try:
            parts = path.split(".")
            if len(parts) == 1:
                if path in self._data:
                    del self._data[path]
                    return True
                return False
            current = self._data
            for part in parts[:-1]:
                if part not in current:
                    return False
                current = current[part]
            final_key = parts[-1]
            if final_key in current:
                del current[final_key]
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting {path}: {e}")
            return False

    def clear(self) -> None:
        """Clear all data."""
        self._data.clear()
        self._signals.clear()

    def to_dict(self) -> dict[str, Any]:
        """Export data as dictionary."""
        return self._data.copy()

    def from_dict(self, data: dict[str, Any]) -> None:
        """Import data from dictionary."""
        self._data = data.copy()

    def _set_nested(self, path: str, value: Any) -> None:
        parts = path.split(".")
        current = self._data
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value

    def _get_nested(self, path: str, default: Any = None) -> Any:
        parts = path.split(".")
        current: Any = self._data
        try:
            for part in parts:
                current = current[part]
            return current
        except (KeyError, TypeError):
            return default


class BindingManager:
    """Manager for widget data bindings."""

    def __init__(self, data_store: DataStore) -> None:
        self.data_store = data_store
        self.bindings: dict[str, list[BindingConfig]] = {}
        self._widget_lookup: Callable[[str], Any] | None = None
        logger.debug("Initialized BindingManager")

    def set_widget_lookup(self, lookup: Callable[[str], Any]) -> None:
        """Register a callable used to resolve a widget by its ID.

        Args:
            lookup: Callable that accepts a widget_id string and returns the
                    widget instance, or None if the widget does not exist.
        """
        self._widget_lookup = lookup

    def bind(
        self,
        source_path: str,
        target_widget: str,
        target_property: str,
        transform: Callable | None = None,
        bidirectional: bool = False,
    ) -> None:
        """Create a data binding from a store path to a widget property."""
        binding = BindingConfig(
            source_path=source_path,
            target_widget=target_widget,
            target_property=target_property,
            transform=transform,
            bidirectional=bidirectional,
        )
        if source_path not in self.bindings:
            self.bindings[source_path] = []
        self.bindings[source_path].append(binding)
        self.data_store.subscribe(source_path, self._on_data_change)
        logger.debug(f"Bound {source_path} -> {target_widget}.{target_property}")

    def unbind(self, source_path: str, target_widget: str | None = None) -> None:
        """Remove bindings for a path, optionally scoped to a specific widget."""
        if source_path not in self.bindings:
            return
        if target_widget:
            self.bindings[source_path] = [
                b
                for b in self.bindings[source_path]
                if b.target_widget != target_widget
            ]
        else:
            del self.bindings[source_path]
            self.data_store.unsubscribe(source_path, self._on_data_change)

    def get_bindings(self, source_path: str) -> list[BindingConfig]:
        """Get all bindings for a data path."""
        return self.bindings.get(source_path, [])

    def clear(self) -> None:
        """Clear all bindings."""
        self.bindings.clear()

    def _on_data_change(self, sender: object, **kwargs: Any) -> None:
        path = kwargs.get("path")
        value = kwargs.get("value")
        if path not in self.bindings:
            return
        for binding in self.bindings[path]:
            final_value = binding.transform(value) if binding.transform else value
            self._update_widget_property(
                binding.target_widget, binding.target_property, final_value
            )

    def _update_widget_property(
        self, widget_id: str, property_name: str, value: Any
    ) -> None:
        if self._widget_lookup is not None:
            widget = self._widget_lookup(widget_id)
            if widget is not None:
                widget.state.properties[property_name] = value
                logger.debug(
                    f"Binding updated {widget_id}.{property_name} = {value}"
                )
                return
        from champi_imgui.core.state import widget_updated

        widget_updated.send(
            self, widget_id=widget_id, property=property_name, value=value
        )


class ValidationManager:
    """Manager for data validation rules."""

    def __init__(self) -> None:
        self.validators: dict[str, list[Callable]] = {}
        self.errors: dict[str, list[str]] = {}
        logger.debug("Initialized ValidationManager")

    def add_validator(
        self, path: str, validator: Callable, error_msg: str | None = None
    ) -> None:
        """Register a validator for a data path."""
        if path not in self.validators:
            self.validators[path] = []

        def wrapped(value: Any) -> bool:
            result: bool = bool(validator(value))
            if not result and error_msg:
                self.add_error(path, error_msg)
            return result

        self.validators[path].append(wrapped)

    def validate(self, path: str, value: Any) -> bool:
        """Run all validators for path. Returns True if all pass."""
        if path not in self.validators:
            return True
        if path in self.errors:
            del self.errors[path]
        return all(v(value) for v in self.validators[path])

    def add_error(self, path: str, error: str) -> None:
        if path not in self.errors:
            self.errors[path] = []
        self.errors[path].append(error)

    def get_errors(self, path: str) -> list[str]:
        return self.errors.get(path, [])

    def has_errors(self, path: str | None = None) -> bool:
        if path:
            return path in self.errors and len(self.errors[path]) > 0
        return len(self.errors) > 0

    def clear_errors(self, path: str | None = None) -> None:
        if path:
            self.errors.pop(path, None)
        else:
            self.errors.clear()
