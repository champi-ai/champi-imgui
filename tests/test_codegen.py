"""Tests for CodeGenerator and TemplateCodeGenerator."""

import ast
from unittest.mock import MagicMock

from champi_imgui.core.codegen import CodeGenerator, TemplateCodeGenerator


def _make_canvas(canvas_id: str = "my_canvas") -> MagicMock:
    canvas = MagicMock()
    canvas.state.canvas_id = canvas_id
    canvas.state.title = "My Canvas"
    canvas.state.size = (800, 600)
    canvas.state.mode.name = "STANDARD"

    w = MagicMock()
    w.__class__.__name__ = "ButtonWidget"
    w.widget_id = "btn_1"
    w.state.properties = {"label": "Click me"}

    canvas.widget_registry.get_all.return_value = {"btn_1": w}
    return canvas


class TestCodeGenerator:
    def test_generate_canvas_code_is_valid_python(self) -> None:
        canvas = _make_canvas()
        code = CodeGenerator.generate_canvas_code(canvas)
        ast.parse(code)  # raises SyntaxError if invalid

    def test_generate_canvas_code_contains_canvas_id(self) -> None:
        canvas = _make_canvas()
        code = CodeGenerator.generate_canvas_code(canvas)
        assert "my_canvas" in code

    def test_generate_canvas_code_contains_widget_id(self) -> None:
        canvas = _make_canvas()
        code = CodeGenerator.generate_canvas_code(canvas)
        assert "btn_1" in code

    def test_generate_canvas_code_uses_champi_imgui_import(self) -> None:
        canvas = _make_canvas()
        code = CodeGenerator.generate_canvas_code(canvas)
        assert "champi_imgui" in code
        assert "champi_gen_ui" not in code

    def test_generate_canvas_code_no_widgets(self) -> None:
        canvas = _make_canvas()
        canvas.widget_registry.get_all.return_value = {}
        code = CodeGenerator.generate_canvas_code(canvas)
        ast.parse(code)
        assert "my_canvas" in code

    def test_generate_canvas_code_many_props(self) -> None:
        canvas = _make_canvas()
        w = canvas.widget_registry.get_all.return_value["btn_1"]
        w.state.properties = {
            "label": "Click me",
            "width": 100,
            "height": 50,
            "enabled": True,
        }
        code = CodeGenerator.generate_canvas_code(canvas)
        ast.parse(code)

    def test_generate_widget_snippet_basic(self) -> None:
        snippet = CodeGenerator.generate_widget_code_snippet("ButtonWidget", "btn_1")
        assert snippet == 'ButtonWidget("btn_1")'

    def test_generate_widget_snippet_with_kwargs(self) -> None:
        snippet = CodeGenerator.generate_widget_code_snippet(
            "ButtonWidget", "btn_1", label="OK", width=100
        )
        assert "ButtonWidget" in snippet
        assert "btn_1" in snippet
        assert "label" in snippet
        assert "width" in snippet

    def test_generate_widget_snippet_string_value(self) -> None:
        snippet = CodeGenerator.generate_widget_code_snippet(
            "TextWidget", "lbl", text="Hello"
        )
        assert '"Hello"' in snippet

    def test_generate_widget_snippet_list_value(self) -> None:
        snippet = CodeGenerator.generate_widget_code_snippet(
            "SliderWidget", "sl", range=[0, 100]
        )
        assert "[0, 100]" in snippet


class TestTemplateCodeGenerator:
    def test_generate_component_template_basic(self) -> None:
        code = TemplateCodeGenerator.generate_component_template(
            "my_panel", ["ButtonWidget", "TextWidget"]
        )
        assert "MyPanelComponent" in code
        assert "ButtonWidget" in code
        assert "TextWidget" in code

    def test_generate_component_template_is_valid_python(self) -> None:
        code = TemplateCodeGenerator.generate_component_template(
            "my_panel", ["ButtonWidget"]
        )
        ast.parse(code)

    def test_generate_component_template_empty_widgets(self) -> None:
        code = TemplateCodeGenerator.generate_component_template("empty_panel", [])
        ast.parse(code)
        assert "EmptyPanelComponent" in code

    def test_generate_component_template_snake_to_pascal(self) -> None:
        code = TemplateCodeGenerator.generate_component_template("foo_bar_baz", [])
        assert "FooBarBazComponent" in code

    def test_generate_component_template_has_render_method(self) -> None:
        code = TemplateCodeGenerator.generate_component_template(
            "panel", ["ButtonWidget"]
        )
        assert "def render" in code

    def test_generate_component_template_has_get_widget(self) -> None:
        code = TemplateCodeGenerator.generate_component_template(
            "panel", ["ButtonWidget"]
        )
        assert "def get_widget" in code
