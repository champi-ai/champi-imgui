"""Tests for ImageWidget."""

from unittest.mock import MagicMock, patch

import pytest

from champi_imgui.widgets.display import ImageWidget


class TestImageWidgetInit:
    def test_default_properties(self):
        w = ImageWidget("img1")
        assert w.state.properties["file_path"] == ""
        assert w.state.properties["width"] == 200.0
        assert w.state.properties["height"] == 200.0
        assert w._texture_id is None
        assert w._loaded_path == ""

    def test_custom_properties(self):
        w = ImageWidget("img2", file_path="/tmp/test.png", width=400.0, height=300.0)
        assert w.state.properties["file_path"] == "/tmp/test.png"
        assert w.state.properties["width"] == 400.0
        assert w.state.properties["height"] == 300.0

    def test_widget_id(self):
        w = ImageWidget("my_image")
        assert w.widget_id == "my_image"


class TestImageWidgetSerialization:
    def test_serialize_includes_properties(self):
        w = ImageWidget("img3", file_path="/tmp/pic.jpg", width=100.0, height=50.0)
        data = w.serialize()
        assert data["widget_id"] == "img3"
        assert data["properties"]["file_path"] == "/tmp/pic.jpg"
        assert data["properties"]["width"] == 100.0
        assert data["properties"]["height"] == 50.0


class TestImageWidgetLoadTexture:
    def test_load_texture_missing_file_returns_none(self):
        w = ImageWidget("img4")
        result = w._load_texture("/nonexistent/path/image.png")
        assert result is None

    def test_load_texture_mocked_success(self):
        w = ImageWidget("img5")
        mock_img = MagicMock()
        mock_img.width = 64
        mock_img.height = 64
        mock_img.convert.return_value = mock_img

        import numpy as np

        mock_array = np.zeros((64, 64, 4), dtype=np.uint8)

        with (
            patch("PIL.Image.open", return_value=mock_img),
            patch("numpy.array", return_value=mock_array),
            patch("OpenGL.GL.glGenTextures", return_value=42),
            patch("OpenGL.GL.glBindTexture"),
            patch("OpenGL.GL.glTexParameteri"),
            patch("OpenGL.GL.glTexImage2D"),
        ):
            result = w._load_texture("/fake/image.png")
        assert result == 42


class TestImageWidgetRender:
    def test_render_invisible_skips(self):
        w = ImageWidget("img6", file_path="/tmp/x.png")
        w.state.visible = False
        with patch("champi_imgui.widgets.display.imgui") as mock_imgui:
            w.render()
            mock_imgui.image.assert_not_called()
            mock_imgui.text_disabled.assert_not_called()

    def test_render_no_file_path_shows_placeholder(self):
        w = ImageWidget("img7", file_path="")
        with patch("champi_imgui.widgets.display.imgui") as mock_imgui:
            w.render()
            mock_imgui.text_disabled.assert_called_once()
            mock_imgui.image.assert_not_called()

    def test_render_failed_load_shows_placeholder(self):
        w = ImageWidget("img8", file_path="/nonexistent.png")
        with patch("champi_imgui.widgets.display.imgui") as mock_imgui:
            w.render()
            mock_imgui.text_disabled.assert_called_once()
            mock_imgui.image.assert_not_called()

    def test_render_reloads_on_path_change(self):
        w = ImageWidget("img9", file_path="/a.png")
        w._texture_id = 10
        w._loaded_path = "/a.png"
        w.state.properties["file_path"] = "/b.png"

        with patch.object(w, "_load_texture", return_value=None) as mock_load:
            with patch("champi_imgui.widgets.display.imgui"):
                w.render()
        mock_load.assert_called_once_with("/b.png")

    def test_render_calls_imgui_image_with_texture(self):
        w = ImageWidget("img10", file_path="/real.png", width=320.0, height=240.0)
        w._texture_id = 99
        w._loaded_path = "/real.png"

        with patch("champi_imgui.widgets.display.imgui") as mock_imgui:
            mock_imgui.ImTextureRef.return_value = MagicMock()
            mock_imgui.ImVec2.return_value = MagicMock()
            mock_imgui.is_item_clicked.return_value = False
            w.render()
            mock_imgui.image.assert_called_once()

    def test_click_triggers_callback(self):
        w = ImageWidget("img11", file_path="/x.png")
        w._texture_id = 1
        w._loaded_path = "/x.png"

        clicked = []
        w.register_callback("click", lambda: clicked.append(True))

        with patch("champi_imgui.widgets.display.imgui") as mock_imgui:
            mock_imgui.ImTextureRef.return_value = MagicMock()
            mock_imgui.ImVec2.return_value = MagicMock()
            mock_imgui.is_item_clicked.return_value = True
            w.render()

        assert clicked == [True]
