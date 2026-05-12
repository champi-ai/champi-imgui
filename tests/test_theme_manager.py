"""Tests for ThemeManager and ThemeColors/ThemeStyle dataclasses."""

from unittest.mock import patch

from champi_imgui.themes.manager import (
    ColorScheme,
    Theme,
    ThemeColors,
    ThemeManager,
    ThemeStyle,
)
from champi_imgui.themes.presets import (
    THEME_PRESETS,
    create_dark_theme,
    create_nord_theme,
)


class TestThemeColors:
    def test_defaults(self) -> None:
        colors = ThemeColors()
        assert colors.window_bg == (0.1, 0.1, 0.1, 1.0)
        assert colors.text == (1.0, 1.0, 1.0, 1.0)

    def test_custom_values(self) -> None:
        colors = ThemeColors(window_bg=(0.5, 0.5, 0.5, 1.0))
        assert colors.window_bg == (0.5, 0.5, 0.5, 1.0)
        assert colors.text == (1.0, 1.0, 1.0, 1.0)


class TestThemeStyle:
    def test_defaults(self) -> None:
        style = ThemeStyle()
        assert style.alpha == 1.0
        assert style.window_rounding == 0.0

    def test_custom_rounding(self) -> None:
        style = ThemeStyle(window_rounding=4.0, frame_rounding=2.0)
        assert style.window_rounding == 4.0
        assert style.frame_rounding == 2.0


class TestTheme:
    def test_creation(self) -> None:
        theme = Theme(name="TestTheme")
        assert theme.name == "TestTheme"
        assert isinstance(theme.colors, ThemeColors)
        assert isinstance(theme.style, ThemeStyle)

    def test_custom_colors(self) -> None:
        colors = ThemeColors(window_bg=(0.2, 0.2, 0.2, 1.0))
        theme = Theme(name="Custom", colors=colors)
        assert theme.colors.window_bg == (0.2, 0.2, 0.2, 1.0)


class TestThemeManager:
    def test_init(self) -> None:
        manager = ThemeManager()
        assert manager.current_theme is None
        assert manager.themes == {}

    def test_register_theme(self) -> None:
        manager = ThemeManager()
        theme = Theme(name="MyTheme")
        manager.register_theme(theme)
        assert "MyTheme" in manager.themes
        assert manager.themes["MyTheme"] is theme

    def test_list_themes_empty(self) -> None:
        manager = ThemeManager()
        assert manager.list_themes() == []

    def test_list_themes_after_register(self) -> None:
        manager = ThemeManager()
        manager.register_theme(Theme(name="A"))
        manager.register_theme(Theme(name="B"))
        assert set(manager.list_themes()) == {"A", "B"}

    def test_get_current_theme_initially_none(self) -> None:
        manager = ThemeManager()
        assert manager.get_current_theme() is None

    def test_apply_theme_by_name_not_found(self) -> None:
        manager = ThemeManager()
        result = manager.apply_theme_by_name("nonexistent")
        assert result is False

    def test_apply_theme_by_name_found(self) -> None:
        manager = ThemeManager()
        theme = Theme(name="Test")
        manager.register_theme(theme)
        with patch.object(manager, "apply_theme") as mock_apply:
            result = manager.apply_theme_by_name("Test")
        assert result is True
        mock_apply.assert_called_once_with(theme)

    def test_apply_theme_sets_current(self) -> None:
        manager = ThemeManager()
        theme = Theme(name="Test")
        with (
            patch.object(manager, "_apply_colors"),
            patch.object(manager, "_apply_style"),
        ):
            manager.apply_theme(theme)
        assert manager.current_theme is theme

    def test_apply_color_scheme(self) -> None:
        manager = ThemeManager()
        with patch("champi_imgui.themes.manager.imgui") as mock_imgui:
            manager.apply_color_scheme(ColorScheme.DARK)
            mock_imgui.style_colors_dark.assert_called_once()

            manager.apply_color_scheme(ColorScheme.LIGHT)
            mock_imgui.style_colors_light.assert_called_once()

            manager.apply_color_scheme(ColorScheme.CLASSIC)
            mock_imgui.style_colors_classic.assert_called_once()


class TestThemePresets:
    def test_preset_count(self) -> None:
        assert len(THEME_PRESETS) == 9

    def test_preset_keys(self) -> None:
        expected = {
            "dark",
            "light",
            "cherry",
            "nord",
            "dracula",
            "gruvbox",
            "solarized_dark",
            "monokai",
            "material",
        }
        assert set(THEME_PRESETS.keys()) == expected

    def test_dark_theme_name(self) -> None:
        theme = create_dark_theme()
        assert theme.name == "Dark"

    def test_nord_theme_rounding(self) -> None:
        theme = create_nord_theme()
        assert theme.style.window_rounding == 3.0
        assert theme.style.frame_rounding == 2.0

    def test_all_presets_are_theme_instances(self) -> None:
        for key, theme in THEME_PRESETS.items():
            assert isinstance(theme, Theme), f"{key} is not a Theme"
            assert isinstance(theme.colors, ThemeColors)
            assert isinstance(theme.style, ThemeStyle)
