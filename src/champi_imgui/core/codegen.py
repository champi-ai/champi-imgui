"""Code generation for creating standalone UI scripts."""

from typing import Any


class CodeGenerator:
    """Generate Python code from canvas/widget instances."""

    @staticmethod
    def generate_canvas_code(canvas: Any) -> str:
        """Generate a complete runnable Python script for a canvas."""
        lines = [
            '"""Generated UI code."""',
            "",
            "from champi_imgui.core.canvas import CanvasManager",
            "",
            "",
            "def create_ui():",
            '    """Create the UI."""',
            "    canvas_manager = CanvasManager()",
            "",
            f"    # Create canvas: {canvas.state.canvas_id}",
            "    canvas = canvas_manager.create_canvas(",
            f'        canvas_id="{canvas.state.canvas_id}",',
            f'        title="{canvas.state.title}",',
            f"        size={tuple(canvas.state.size)},",
            "    )",
            "",
        ]

        widgets = list(canvas.widget_registry.get_all().values())
        if widgets:
            lines.append("    # Create widgets")

        for widget in widgets:
            lines.extend(CodeGenerator._widget_lines(widget))

        lines.extend(
            [
                "    return canvas",
                "",
                "",
                'if __name__ == "__main__":',
                "    canvas = create_ui()",
            ]
        )

        return "\n".join(lines)

    @staticmethod
    def _widget_lines(widget: Any) -> list[str]:
        widget_type = widget.__class__.__name__
        var = widget.widget_id.replace(".", "_").replace("-", "_")
        props = widget.state.properties

        args: list[str] = [f'"{widget.widget_id}"']
        for k, v in props.items():
            if v is None:
                continue
            if isinstance(v, str):
                args.append(f'{k}="{v}"')
            elif isinstance(v, (list, tuple)):
                args.append(f"{k}={list(v)}")
            elif isinstance(v, (bool, int, float)):
                args.append(f"{k}={v!r}")

        lines: list[str] = []
        if len(args) <= 3:
            lines.append(f"    {var} = {widget_type}({', '.join(args)})")
        else:
            lines.append(f"    {var} = {widget_type}(")
            for i, arg in enumerate(args):
                comma = "," if i < len(args) - 1 else ""
                lines.append(f"        {arg}{comma}")
            lines.append("    )")
        lines.append(f"    canvas.add_widget({var})")
        lines.append("")
        return lines

    @staticmethod
    def generate_widget_code_snippet(
        widget_type: str, widget_id: str, **kwargs: Any
    ) -> str:
        """Generate a single widget construction expression."""
        args: list[str] = [f'"{widget_id}"']
        for k, v in kwargs.items():
            if isinstance(v, str):
                args.append(f'{k}="{v}"')
            elif isinstance(v, (list, tuple)):
                args.append(f"{k}={list(v)}")
            else:
                args.append(f"{k}={v!r}")
        return f"{widget_type}({', '.join(args)})"


class TemplateCodeGenerator:
    """Generate reusable component class code."""

    @staticmethod
    def generate_component_template(name: str, widgets: list[str]) -> str:
        """Generate a Python class wrapping the given widget types as a component."""
        class_name = "".join(word.capitalize() for word in name.split("_"))

        lines = [
            f"class {class_name}Component:",
            f'    """Reusable {name} component."""',
            "",
            "    def __init__(self, component_id: str):",
            "        self.component_id = component_id",
            "        self.widgets: dict = {}",
            "        self._create_widgets()",
            "",
            "    def _create_widgets(self) -> None:",
        ]

        if not widgets:
            lines.append("        pass")
        else:
            for i, widget_type in enumerate(widgets):
                key = f"{widget_type.lower()}_{i}"
                lines.append(
                    f"        self.widgets['{key}'] = {widget_type}(f'{{self.component_id}}.widget_{i}')"
                )

        lines.extend(
            [
                "",
                "    def render(self, canvas: object) -> None:",
                '        """Render component on canvas."""',
                "        for widget in self.widgets.values():",
                "            canvas.add_widget(widget)",
                "",
                "    def get_widget(self, key: str) -> object:",
                '        """Get widget by key."""',
                "        return self.widgets.get(key)",
            ]
        )

        return "\n".join(lines)
