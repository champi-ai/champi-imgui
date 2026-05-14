"""Tests for drawing widgets.

Tests the DrawingWidget, BrushWidget, and CanvasMenuWidget implementations.
"""

import pytest


class TestDrawingWidget:
    """Tests for DrawingWidget class."""

    def test_initialization(self):
        """Test that DrawingWidget initializes correctly."""
        from champi_imgui.widgets.drawing import DrawingWidget

        widget = DrawingWidget("test_drawing")
        assert widget.widget_id == "test_drawing"
        assert widget.state.properties["color"] == (1.0, 0.0, 0.0, 1.0)
        assert widget.state.properties["brush_size"] == 5.0

    def test_custom_parameters(self):
        """Test DrawingWidget with custom parameters."""
        from champi_imgui.widgets.drawing import DrawingWidget

        widget = DrawingWidget(
            "test_drawing",
            color=(0.0, 1.0, 0.0, 1.0),  # Green
            brush_size=10.0,
            line_width=2.0,
            is_eraser=True,
            brush_style="dashed",
        )

        assert widget.state.properties["color"] == (0.0, 1.0, 0.0, 1.0)
        assert widget.state.properties["brush_size"] == 10.0
        assert widget.state.properties["line_width"] == 2.0
        assert widget.state.properties["is_eraser"] is True
        assert widget.state.properties["brush_style"] == "dashed"

    def test_history_initialization(self):
        """Test that history is properly initialized."""
        from champi_imgui.widgets.drawing import DrawingWidget

        # Default: empty history
        widget = DrawingWidget("test")
        assert widget.state.properties["history"] == []
        assert widget.state.properties["history_index"] == -1

        # With pre-populated history
        history = [{"data": []}]
        widget = DrawingWidget("test", history=history, history_index=0)
        assert len(widget.state.properties["history"]) == 1

    def test_serialize(self):
        """Test that widget can be serialized."""
        from champi_imgui.widgets.drawing import DrawingWidget

        widget = DrawingWidget("test_draw")
        data = widget.serialize()

        assert data["widget_id"] == "test_draw"
        assert data["widget_type"] == "DrawingWidget"
        assert "properties" in data


class TestBrushWidget:
    """Tests for BrushWidget class."""

    def test_initialization(self):
        """Test that BrushWidget initializes correctly."""
        from champi_imgui.widgets.drawing import BrushWidget

        widget = BrushWidget("test_brush")
        assert widget.widget_id == "test_brush"
        assert widget.state.properties["color"] == (1.0, 0.0, 0.0, 1.0)
        assert widget.state.properties["brush_size"] == 5.0

    def test_custom_brush_settings(self):
        """Test BrushWidget with custom brush settings."""
        from champi_imgui.widgets.drawing import BrushWidget

        widget = BrushWidget(
            "test_brush",
            color=(0.0, 0.0, 1.0, 1.0),  # Blue
            brush_size=8.0,
            line_width=3.0,
            is_eraser=False,
            brush_style="dots",
        )

        assert widget.state.properties["color"] == (0.0, 0.0, 1.0, 1.0)
        assert widget.state.properties["brush_size"] == 8.0
        assert widget.state.properties["is_eraser"] is False
        assert widget.state.properties["brush_style"] == "dots"

    def test_serialize(self):
        """Test that widget can be serialized."""
        from champi_imgui.widgets.drawing import BrushWidget

        widget = BrushWidget("test_brush_ctrl")
        data = widget.serialize()

        assert data["widget_id"] == "test_brush_ctrl"
        assert data["widget_type"] == "BrushWidget"


class TestCanvasMenuWidget:
    """Tests for CanvasMenuWidget class."""

    def test_initialization(self):
        """Test that CanvasMenuWidget initializes correctly."""
        from champi_imgui.widgets.drawing import CanvasMenuWidget

        widget = CanvasMenuWidget("test_menu")
        assert widget.widget_id == "test_menu"
        assert widget.state.properties["can_undo"] is True
        assert widget.state.properties["can_redo"] is True

    def test_disabled_commands(self):
        """Test CanvasMenuWidget with disabled undo/redo."""
        from champi_imgui.widgets.drawing import CanvasMenuWidget

        widget = CanvasMenuWidget(
            "test_menu",
            can_undo=False,
            can_redo=False,
            history_size=5,
        )

        assert widget.state.properties["can_undo"] is False
        assert widget.state.properties["can_redo"] is False
        assert widget.state.properties["history_size"] == 5

    def test_serialize(self):
        """Test that widget can be serialized."""
        from champi_imgui.widgets.drawing import CanvasMenuWidget

        widget = CanvasMenuWidget("test_menu")
        data = widget.serialize()

        assert data["widget_id"] == "test_menu"
        assert data["widget_type"] == "CanvasMenuWidget"


class TestDrawingWidgetRendering:
    """Tests for DrawingWidget rendering behavior."""

    def test_visible_widget(self):
        """Test render when widget is visible."""
        from champi_imgui.widgets.drawing import DrawingWidget

        widget = DrawingWidget("visible_draw")
        widget.set_visible(True)

        # Should not raise an exception
        widget.render()

    def test_hidden_widget(self):
        """Test render when widget is hidden."""
        from champi_imgui.widgets.drawing import DrawingWidget

        widget = DrawingWidget("hidden_draw")
        widget.set_visible(False)

        # Should not raise an exception
        widget.render()


class TestColorParsing:
    """Tests for color parsing in main.py helpers."""

    def test_hex_color_parsing(self):
        """Test hex color parsing."""
        from champi_imgui.server.main import _hex_to_rgba

        # Red
        assert _hex_to_rgba("#FF0000") == (1.0, 0.0, 0.0, 1.0)
        # Blue
        assert _hex_to_rgba("#0000FF") == (0.0, 0.0, 1.0, 1.0)
        # Green
        assert _hex_to_rgba("#00FF00") == (0.0, 1.0, 0.0, 1.0)
        # With alpha
        assert _hex_to_rgba("#FF000080") == (1.0, 0.0, 0.0, 0.5)

    def test_named_colors(self):
        """Test named color parsing."""
        from champi_imgui.server.main import _parse_color

        # Named colors
        assert _parse_color("red") == (1.0, 0.0, 0.0, 1.0)
        assert _parse_color("blue") == (0.0, 0.0, 1.0, 1.0)
        assert _parse_color("green") == (0.0, 1.0, 0.0, 1.0)
        assert _parse_color("white") == (1.0, 1.0, 1.0, 1.0)
        assert _parse_color("black") == (0.0, 0.0, 0.0, 1.0)

    def test_invalid_color(self):
        """Test that invalid colors default to red."""
        from champi_imgui.server.main import _parse_color

        assert _parse_color("invalid") == (1.0, 0.0, 0.0, 1.0)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
