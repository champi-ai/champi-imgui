"""Tests for UIExporter, UIImporter, and TemplateManager."""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

from champi_imgui.core.serialization import TemplateManager, UIExporter, UIImporter


def _make_canvas(canvas_id: str = "test_canvas") -> MagicMock:
    """Build a minimal canvas mock matching the expected serialization API."""
    canvas = MagicMock()
    canvas.state.canvas_id = canvas_id
    canvas.state.title = "Test"
    canvas.state.size = (800, 600)
    canvas.state.mode.value = "standard"
    canvas.state.mode.name = "STANDARD"

    w1 = MagicMock()
    w1.__class__.__name__ = "ButtonWidget"
    w1.widget_id = "btn_1"
    w1.serialize.return_value = {
        "widget_id": "btn_1",
        "widget_type": "ButtonWidget",
        "visible": True,
        "enabled": True,
        "position": None,
        "size": None,
        "properties": {"label": "Click me"},
    }
    w1.state.properties = {"label": "Click me"}
    w1.state.visible = True
    w1.state.enabled = True
    w1.state.position = None
    w1.state.size = None

    canvas.widget_registry.get_all.return_value = {"btn_1": w1}
    return canvas


class TestUIExporter:
    def test_export_canvas_state_returns_json_string(self) -> None:
        canvas = _make_canvas()
        result = UIExporter.export_canvas_state(canvas)
        data = json.loads(result)
        assert data["canvas_id"] == "test_canvas"
        assert data["title"] == "Test"
        assert data["size"] == [800, 600]
        assert data["metadata"]["created_with"] == "champi-imgui"

    def test_export_canvas_state_includes_widgets(self) -> None:
        canvas = _make_canvas()
        result = UIExporter.export_canvas_state(canvas)
        data = json.loads(result)
        assert len(data["widgets"]) == 1
        assert data["widgets"][0]["widget_type"] == "ButtonWidget"

    def test_export_to_json_writes_file(self) -> None:
        canvas = _make_canvas()
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            filepath = f.name
        try:
            ok = UIExporter.export_to_json(canvas, filepath)
            assert ok is True
            with open(filepath) as f:
                data = json.load(f)
            assert data["canvas_id"] == "test_canvas"
        finally:
            Path(filepath).unlink(missing_ok=True)

    def test_export_to_json_returns_false_on_error(self) -> None:
        canvas = _make_canvas()
        ok = UIExporter.export_to_json(canvas, "/nonexistent_dir/file.json")
        assert ok is False

    def test_serialize_canvas_no_widgets(self) -> None:
        canvas = _make_canvas()
        canvas.widget_registry.get_all.return_value = {}
        result = UIExporter.export_canvas_state(canvas)
        data = json.loads(result)
        assert data["widgets"] == []


class TestUIImporter:
    def _make_canvas_data(self) -> dict:
        return {
            "canvas_id": "imported_canvas",
            "title": "Imported",
            "size": [800, 600],
            "mode": "standard",
            "widgets": [
                {
                    "widget_id": "btn_1",
                    "widget_type": "ButtonWidget",
                    "visible": True,
                    "enabled": True,
                    "position": None,
                    "size": None,
                    "properties": {"label": "Click"},
                }
            ],
        }

    def test_import_from_json_creates_canvas(self) -> None:
        data = self._make_canvas_data()
        canvas_manager = MagicMock()
        mock_canvas = MagicMock()
        mock_canvas.widget_registry.factory.create.return_value = MagicMock()
        canvas_manager.create_canvas.return_value = mock_canvas

        with tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False) as f:
            json.dump(data, f)
            filepath = f.name
        try:
            result = UIImporter.import_from_json(filepath, canvas_manager)
            assert result is mock_canvas
            canvas_manager.create_canvas.assert_called_once()
        finally:
            Path(filepath).unlink(missing_ok=True)

    def test_import_from_json_returns_none_on_bad_file(self) -> None:
        canvas_manager = MagicMock()
        result = UIImporter.import_from_json("/nonexistent/file.json", canvas_manager)
        assert result is None

    def test_import_adds_widgets(self) -> None:
        data = self._make_canvas_data()
        canvas_manager = MagicMock()
        mock_canvas = MagicMock()
        mock_widget = MagicMock()
        mock_canvas.widget_registry.factory.create.return_value = mock_widget
        canvas_manager.create_canvas.return_value = mock_canvas

        with tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False) as f:
            json.dump(data, f)
            filepath = f.name
        try:
            UIImporter.import_from_json(filepath, canvas_manager)
            mock_canvas.add_widget.assert_called_once_with(mock_widget)
        finally:
            Path(filepath).unlink(missing_ok=True)

    def test_import_skips_unknown_widget_type(self) -> None:
        data = self._make_canvas_data()
        data["widgets"][0]["widget_type"] = "UnknownWidget"
        canvas_manager = MagicMock()
        mock_canvas = MagicMock()
        mock_canvas.widget_registry.factory.create.side_effect = ValueError("unknown")
        canvas_manager.create_canvas.return_value = mock_canvas

        with tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False) as f:
            json.dump(data, f)
            filepath = f.name
        try:
            result = UIImporter.import_from_json(filepath, canvas_manager)
            assert result is mock_canvas
            mock_canvas.add_widget.assert_not_called()
        finally:
            Path(filepath).unlink(missing_ok=True)


class TestTemplateManager:
    def test_save_and_list_template(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tm = TemplateManager(template_dir=tmpdir)
            canvas = _make_canvas()
            ok = tm.save_template("my_tpl", canvas, description="A template")
            assert ok is True
            templates = tm.list_templates()
            names = [t["name"] for t in templates]
            assert "my_tpl" in names

    def test_save_template_writes_json_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tm = TemplateManager(template_dir=tmpdir)
            canvas = _make_canvas()
            tm.save_template("tpl1", canvas)
            filepath = Path(tmpdir) / "tpl1.json"
            assert filepath.exists()
            with open(filepath) as f:
                data = json.load(f)
            assert data["template_name"] == "tpl1"

    def test_load_template_creates_canvas(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tm = TemplateManager(template_dir=tmpdir)
            canvas = _make_canvas()
            tm.save_template("tpl1", canvas)

            canvas_manager = MagicMock()
            mock_canvas = MagicMock()
            mock_canvas.widget_registry.factory.create.return_value = MagicMock()
            canvas_manager.create_canvas.return_value = mock_canvas

            result = tm.load_template("tpl1", canvas_manager)
            assert result is mock_canvas

    def test_load_missing_template_returns_none(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tm = TemplateManager(template_dir=tmpdir)
            canvas_manager = MagicMock()
            result = tm.load_template("no_such", canvas_manager)
            assert result is None

    def test_delete_template(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tm = TemplateManager(template_dir=tmpdir)
            canvas = _make_canvas()
            tm.save_template("tpl1", canvas)
            ok = tm.delete_template("tpl1")
            assert ok is True
            filepath = Path(tmpdir) / "tpl1.json"
            assert not filepath.exists()
            templates = tm.list_templates()
            names = [t["name"] for t in templates]
            assert "tpl1" not in names

    def test_delete_nonexistent_template(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tm = TemplateManager(template_dir=tmpdir)
            ok = tm.delete_template("ghost")
            assert ok is True  # no-op succeeds

    def test_list_templates_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tm = TemplateManager(template_dir=tmpdir)
            assert tm.list_templates() == []

    def test_list_templates_from_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            # Write a template file directly
            data = {
                "canvas_id": "c1",
                "title": "C",
                "size": [800, 600],
                "mode": "standard",
                "widgets": [],
                "template_name": "disk_tpl",
                "description": "From disk",
            }
            Path(tmpdir, "disk_tpl.json").write_text(json.dumps(data))
            tm = TemplateManager(template_dir=tmpdir)
            templates = tm.list_templates()
            assert any(t["name"] == "disk_tpl" for t in templates)
