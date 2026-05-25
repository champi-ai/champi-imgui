"""Integration tests for Phase 4 MCP tools."""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import champi_imgui.api.server as _srv_mod
from champi_imgui.api.server import create_mcp_app

_DEFAULT_MCP = None


class _Server:
    """Proxy that exposes MCP tools and managers from a factory instance.

    Falls back to a lazy default instance for parametrize collection.
    """

    _mcp = None

    def __getattr__(self, name: str):
        global _DEFAULT_MCP
        if hasattr(_srv_mod, name):
            return getattr(_srv_mod, name)
        mcp = type(self)._mcp
        if mcp is None:
            if _DEFAULT_MCP is None:
                _DEFAULT_MCP = create_mcp_app()
            mcp = _DEFAULT_MCP
        if hasattr(mcp, name):
            return getattr(mcp, name)
        if hasattr(mcp, f"_{name}"):
            return getattr(mcp, f"_{name}")
        components = mcp._local_provider._components
        if f"tool:{name}@" in components:
            return components[f"tool:{name}@"]
        raise AttributeError(f"_Server has no attribute '{name}'")


server = _Server()


@pytest.fixture(autouse=True)
def _fresh_mcp():
    _Server._mcp = create_mcp_app()
    yield
    _Server._mcp = None


def _make_canvas(canvas_id: str = "c1") -> MagicMock:
    canvas = MagicMock()
    canvas.state.canvas_id = canvas_id
    canvas.state.title = "Test"
    canvas.state.size = (800, 600)
    canvas.state.to_dict.return_value = {"canvas_id": canvas_id}
    canvas.widget_registry.get_all.return_value = {}
    return canvas


class TestExportCanvasJsonTool:
    def test_success(self) -> None:
        canvas = _make_canvas()
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            filepath = f.name
        try:
            with patch.object(server.canvas_manager, "get_canvas", return_value=canvas):
                result = server.export_canvas_json.fn("c1", filepath)
            assert result["success"] is True
        finally:
            Path(filepath).unlink(missing_ok=True)

    def test_canvas_not_found(self) -> None:
        with patch.object(server.canvas_manager, "get_canvas", return_value=None):
            result = server.export_canvas_json.fn("missing", "/tmp/x.json")
        assert result["success"] is False
        assert "not found" in result["error"]


class TestExportCanvasPythonTool:
    def test_success(self) -> None:
        canvas = _make_canvas()
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as f:
            filepath = f.name
        try:
            with patch.object(server.canvas_manager, "get_canvas", return_value=canvas):
                result = server.export_canvas_python.fn("c1", filepath)
            assert result["success"] is True
            content = Path(filepath).read_text()
            assert "champi_imgui" in content
        finally:
            Path(filepath).unlink(missing_ok=True)

    def test_canvas_not_found(self) -> None:
        with patch.object(server.canvas_manager, "get_canvas", return_value=None):
            result = server.export_canvas_python.fn("missing", "/tmp/x.py")
        assert result["success"] is False

    def test_unwritable_path(self) -> None:
        canvas = _make_canvas()
        with patch.object(server.canvas_manager, "get_canvas", return_value=canvas):
            result = server.export_canvas_python.fn("c1", "/no_such_dir/x.py")
        assert result["success"] is False


class TestImportCanvasJsonTool:
    def test_success(self) -> None:
        canvas = _make_canvas("imported")
        data = {
            "canvas_id": "imported",
            "title": "T",
            "size": [800, 600],
            "widgets": [],
        }
        with tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False) as f:
            json.dump(data, f)
            filepath = f.name
        try:
            with patch.object(
                server.canvas_manager, "create_canvas", return_value=canvas
            ):
                result = server.import_canvas_json.fn(filepath)
            assert result["success"] is True
        finally:
            Path(filepath).unlink(missing_ok=True)

    def test_missing_file(self) -> None:
        result = server.import_canvas_json.fn("/no/such/file.json")
        assert result["success"] is False


class TestGetCanvasJsonTool:
    def test_success(self) -> None:
        canvas = _make_canvas()
        with patch.object(server.canvas_manager, "get_canvas", return_value=canvas):
            result = server.get_canvas_json.fn("c1")
        assert result["success"] is True
        assert "json" in result["data"]
        parsed = json.loads(result["data"]["json"])
        assert parsed["canvas_id"] == "c1"

    def test_not_found(self) -> None:
        with patch.object(server.canvas_manager, "get_canvas", return_value=None):
            result = server.get_canvas_json.fn("missing")
        assert result["success"] is False


class TestGenerateCanvasCodeTool:
    def test_success(self) -> None:
        canvas = _make_canvas()
        with patch.object(server.canvas_manager, "get_canvas", return_value=canvas):
            result = server.generate_canvas_code.fn("c1")
        assert result["success"] is True
        assert "code" in result["data"]
        assert "champi_imgui" in result["data"]["code"]

    def test_not_found(self) -> None:
        with patch.object(server.canvas_manager, "get_canvas", return_value=None):
            result = server.generate_canvas_code.fn("missing")
        assert result["success"] is False


class TestGenerateWidgetSnippetTool:
    def test_success(self) -> None:
        result = server.generate_widget_snippet.fn("ButtonWidget", "btn_1")
        assert result["success"] is True
        assert "snippet" in result["data"]
        assert "ButtonWidget" in result["data"]["snippet"]


class TestGenerateComponentTemplateTool:
    def test_success(self) -> None:
        result = server.generate_component_template.fn("my_panel", ["ButtonWidget"])
        assert result["success"] is True
        assert "code" in result["data"]
        assert "MyPanelComponent" in result["data"]["code"]


class TestSaveLoadTemplateTools:
    def test_save_success(self) -> None:
        canvas = _make_canvas()
        with (
            patch.object(server.canvas_manager, "get_canvas", return_value=canvas),
            patch.object(
                server.template_manager, "save_template", return_value=True
            ) as mock_save,
        ):
            result = server.save_template.fn("tpl1", "c1", "desc")
        assert result["success"] is True
        mock_save.assert_called_once_with("tpl1", canvas, "desc")

    def test_save_canvas_not_found(self) -> None:
        with patch.object(server.canvas_manager, "get_canvas", return_value=None):
            result = server.save_template.fn("tpl1", "missing")
        assert result["success"] is False

    def test_load_success(self) -> None:
        canvas = _make_canvas("loaded")
        with patch.object(
            server.template_manager, "load_template", return_value=canvas
        ):
            result = server.load_template.fn("tpl1")
        assert result["success"] is True

    def test_load_not_found(self) -> None:
        with patch.object(server.template_manager, "load_template", return_value=None):
            result = server.load_template.fn("ghost")
        assert result["success"] is False


class TestListDeleteTemplateTools:
    def test_list_success(self) -> None:
        templates = [{"name": "tpl1", "description": "A"}]
        with patch.object(
            server.template_manager, "list_templates", return_value=templates
        ):
            result = server.list_templates.fn()
        assert result["success"] is True
        assert result["data"]["templates"] == templates

    def test_delete_success(self) -> None:
        with patch.object(
            server.template_manager, "delete_template", return_value=True
        ):
            result = server.delete_template.fn("tpl1")
        assert result["success"] is True
        assert result["data"]["name"] == "tpl1"
