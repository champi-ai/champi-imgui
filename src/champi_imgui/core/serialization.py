"""JSON serialization for UI export/import."""

import json
from pathlib import Path
from typing import Any

from loguru import logger


class UIExporter:
    """Export UI to various formats."""

    @staticmethod
    def export_to_json(canvas: Any, filepath: str) -> bool:
        """Export canvas to JSON file."""
        try:
            data = UIExporter._serialize_canvas(canvas)
            with open(filepath, "w") as f:
                json.dump(data, f, indent=2)
            logger.info(f"Exported UI to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
            return False

    @staticmethod
    def export_canvas_state(canvas: Any) -> str:
        """Export canvas state as JSON string."""
        data = UIExporter._serialize_canvas(canvas)
        return json.dumps(data, indent=2)

    @staticmethod
    def _serialize_canvas(canvas: Any) -> dict[str, Any]:
        widgets = []
        for widget in canvas.widget_registry.get_all().values():
            w = widget.serialize()
            w["widget_type"] = widget.__class__.__name__
            widgets.append(w)

        return {
            "type": "canvas",
            "canvas_id": canvas.state.canvas_id,
            "title": canvas.state.title,
            "size": list(canvas.state.size),
            "widgets": widgets,
            "metadata": {
                "version": "1.0.0",
                "created_with": "champi-imgui",
            },
        }


class UIImporter:
    """Import UI from various formats."""

    @staticmethod
    def import_from_json(filepath: str, canvas_manager: Any) -> Any:
        """Import canvas from JSON file."""
        try:
            with open(filepath) as f:
                data = json.load(f)
            canvas = UIImporter._deserialize_canvas(data, canvas_manager)
            logger.info(f"Imported UI from {filepath}")
            return canvas
        except Exception as e:
            logger.error(f"Error importing from JSON: {e}")
            return None

    @staticmethod
    def _deserialize_canvas(data: dict[str, Any], canvas_manager: Any) -> Any:
        canvas = canvas_manager.create_canvas(
            canvas_id=data["canvas_id"],
            title=data.get("title", "Canvas"),
            size=tuple(data.get("size", [800, 600])),
        )

        factory = canvas.widget_registry.factory
        for w in data.get("widgets", []):
            widget_type = w.get("widget_type", "")
            widget_id = w.get("widget_id", "")
            props = w.get("properties", {})
            try:
                widget = factory.create(widget_type.lower(), widget_id, **props)
                widget.state.visible = w.get("visible", True)
                widget.state.enabled = w.get("enabled", True)
                pos = w.get("position")
                if pos:
                    widget.state.position = tuple(pos)
                sz = w.get("size")
                if sz:
                    widget.state.size = tuple(sz)
                canvas.add_widget(widget)
            except Exception as e:
                logger.error(f"Error deserializing widget {widget_id}: {e}")

        return canvas


class TemplateManager:
    """Manager for UI templates."""

    def __init__(self, template_dir: str | None = None):
        self.templates_dir = (
            Path(template_dir)
            if template_dir
            else Path.home() / ".champi-imgui" / "templates"
        )
        self._cache: dict[str, dict[str, Any]] = {}

    def save_template(self, name: str, canvas: Any, description: str = "") -> bool:
        """Save canvas as a named template."""
        try:
            data = UIExporter._serialize_canvas(canvas)
            data["template_name"] = name
            data["description"] = description

            self.templates_dir.mkdir(parents=True, exist_ok=True)
            filepath = self.templates_dir / f"{name}.json"
            with open(filepath, "w") as f:
                json.dump(data, f, indent=2)

            self._cache[name] = data
            logger.info(f"Saved template: {name}")
            return True
        except Exception as e:
            logger.error(f"Error saving template: {e}")
            return False

    def load_template(self, name: str, canvas_manager: Any) -> Any:
        """Load a template and create a canvas from it."""
        try:
            if name in self._cache:
                data = self._cache[name]
            else:
                filepath = self.templates_dir / f"{name}.json"
                if not filepath.exists():
                    logger.warning(f"Template not found: {name}")
                    return None
                with open(filepath) as f:
                    data = json.load(f)
                self._cache[name] = data

            return UIImporter._deserialize_canvas(data, canvas_manager)
        except Exception as e:
            logger.error(f"Error loading template: {e}")
            return None

    def list_templates(self) -> list[dict[str, str]]:
        """Return list of available templates."""
        result: list[dict[str, str]] = []
        seen: set[str] = set()

        for name, data in self._cache.items():
            result.append({"name": name, "description": data.get("description", "")})
            seen.add(name)

        if self.templates_dir.exists():
            for filepath in self.templates_dir.glob("*.json"):
                name = filepath.stem
                if name not in seen:
                    try:
                        with open(filepath) as f:
                            data = json.load(f)
                        result.append(
                            {"name": name, "description": data.get("description", "")}
                        )
                    except Exception as e:
                        logger.error(f"Error reading template {name}: {e}")

        return result

    def delete_template(self, name: str) -> bool:
        """Delete a template by name."""
        try:
            self._cache.pop(name, None)
            filepath = self.templates_dir / f"{name}.json"
            if filepath.exists():
                filepath.unlink()
            logger.info(f"Deleted template: {name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting template: {e}")
            return False
