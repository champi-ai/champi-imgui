"""Theme manager for styling and appearance."""

from dataclasses import dataclass, field
from enum import Enum

from imgui_bundle import imgui
from loguru import logger


class ColorScheme(Enum):
    """Built-in color schemes."""

    DARK = "dark"
    LIGHT = "light"
    CLASSIC = "classic"
    CHERRY = "cherry"
    CUSTOM = "custom"


@dataclass
class ThemeColors:
    """Theme color configuration."""

    window_bg: tuple[float, float, float, float] = (0.1, 0.1, 0.1, 1.0)
    child_bg: tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)
    popup_bg: tuple[float, float, float, float] = (0.08, 0.08, 0.08, 0.94)
    frame_bg: tuple[float, float, float, float] = (0.16, 0.16, 0.16, 1.0)
    frame_bg_hovered: tuple[float, float, float, float] = (0.26, 0.26, 0.26, 1.0)
    frame_bg_active: tuple[float, float, float, float] = (0.28, 0.28, 0.28, 1.0)
    title_bg: tuple[float, float, float, float] = (0.04, 0.04, 0.04, 1.0)
    title_bg_active: tuple[float, float, float, float] = (0.16, 0.16, 0.16, 1.0)
    title_bg_collapsed: tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.51)
    menu_bar_bg: tuple[float, float, float, float] = (0.14, 0.14, 0.14, 1.0)
    scrollbar_bg: tuple[float, float, float, float] = (0.02, 0.02, 0.02, 0.53)
    scrollbar_grab: tuple[float, float, float, float] = (0.31, 0.31, 0.31, 1.0)
    scrollbar_grab_hovered: tuple[float, float, float, float] = (0.41, 0.41, 0.41, 1.0)
    scrollbar_grab_active: tuple[float, float, float, float] = (0.51, 0.51, 0.51, 1.0)
    check_mark: tuple[float, float, float, float] = (0.26, 0.59, 0.98, 1.0)
    slider_grab: tuple[float, float, float, float] = (0.24, 0.52, 0.88, 1.0)
    slider_grab_active: tuple[float, float, float, float] = (0.26, 0.59, 0.98, 1.0)
    button: tuple[float, float, float, float] = (0.26, 0.59, 0.98, 0.4)
    button_hovered: tuple[float, float, float, float] = (0.26, 0.59, 0.98, 1.0)
    button_active: tuple[float, float, float, float] = (0.06, 0.53, 0.98, 1.0)
    header: tuple[float, float, float, float] = (0.26, 0.59, 0.98, 0.31)
    header_hovered: tuple[float, float, float, float] = (0.26, 0.59, 0.98, 0.8)
    header_active: tuple[float, float, float, float] = (0.26, 0.59, 0.98, 1.0)
    separator: tuple[float, float, float, float] = (0.43, 0.43, 0.5, 0.5)
    separator_hovered: tuple[float, float, float, float] = (0.1, 0.4, 0.75, 0.78)
    separator_active: tuple[float, float, float, float] = (0.1, 0.4, 0.75, 1.0)
    resize_grip: tuple[float, float, float, float] = (0.26, 0.59, 0.98, 0.2)
    resize_grip_hovered: tuple[float, float, float, float] = (0.26, 0.59, 0.98, 0.67)
    resize_grip_active: tuple[float, float, float, float] = (0.26, 0.59, 0.98, 0.95)
    tab: tuple[float, float, float, float] = (0.18, 0.35, 0.58, 0.86)
    tab_hovered: tuple[float, float, float, float] = (0.26, 0.59, 0.98, 0.8)
    tab_active: tuple[float, float, float, float] = (0.2, 0.41, 0.68, 1.0)
    tab_unfocused: tuple[float, float, float, float] = (0.07, 0.1, 0.15, 0.97)
    tab_unfocused_active: tuple[float, float, float, float] = (0.14, 0.26, 0.42, 1.0)
    docking_preview: tuple[float, float, float, float] = (0.26, 0.59, 0.98, 0.7)
    docking_empty_bg: tuple[float, float, float, float] = (0.2, 0.2, 0.2, 1.0)
    plot_lines: tuple[float, float, float, float] = (0.61, 0.61, 0.61, 1.0)
    plot_lines_hovered: tuple[float, float, float, float] = (1.0, 0.43, 0.35, 1.0)
    plot_histogram: tuple[float, float, float, float] = (0.9, 0.7, 0.0, 1.0)
    plot_histogram_hovered: tuple[float, float, float, float] = (1.0, 0.6, 0.0, 1.0)
    text: tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0)
    text_disabled: tuple[float, float, float, float] = (0.5, 0.5, 0.5, 1.0)
    text_selected_bg: tuple[float, float, float, float] = (0.26, 0.59, 0.98, 0.35)
    drag_drop_target: tuple[float, float, float, float] = (1.0, 1.0, 0.0, 0.9)
    nav_highlight: tuple[float, float, float, float] = (0.26, 0.59, 0.98, 1.0)
    nav_windowing_highlight: tuple[float, float, float, float] = (1.0, 1.0, 1.0, 0.7)
    nav_windowing_dim_bg: tuple[float, float, float, float] = (0.8, 0.8, 0.8, 0.2)
    modal_window_dim_bg: tuple[float, float, float, float] = (0.8, 0.8, 0.8, 0.35)


@dataclass
class ThemeStyle:
    """Theme style configuration."""

    alpha: float = 1.0
    disabled_alpha: float = 0.6
    window_padding: tuple[float, float] = (8.0, 8.0)
    window_rounding: float = 0.0
    window_border_size: float = 1.0
    window_min_size: tuple[float, float] = (32.0, 32.0)
    window_title_align: tuple[float, float] = (0.0, 0.5)
    child_rounding: float = 0.0
    child_border_size: float = 1.0
    popup_rounding: float = 0.0
    popup_border_size: float = 1.0
    frame_padding: tuple[float, float] = (4.0, 3.0)
    frame_rounding: float = 0.0
    frame_border_size: float = 0.0
    item_spacing: tuple[float, float] = (8.0, 4.0)
    item_inner_spacing: tuple[float, float] = (4.0, 4.0)
    touch_extra_padding: tuple[float, float] = (0.0, 0.0)
    indent_spacing: float = 21.0
    columns_min_spacing: float = 6.0
    scrollbar_size: float = 14.0
    scrollbar_rounding: float = 9.0
    grab_min_size: float = 12.0
    grab_rounding: float = 0.0
    tab_rounding: float = 4.0
    tab_border_size: float = 0.0
    tab_min_width_for_close_button: float = 0.0
    button_text_align: tuple[float, float] = (0.5, 0.5)
    selectable_text_align: tuple[float, float] = (0.0, 0.0)
    display_window_padding: tuple[float, float] = (19.0, 19.0)
    display_safe_area_padding: tuple[float, float] = (3.0, 3.0)
    curve_tessellation_tol: float = 1.25
    circle_tessellation_max_error: float = 0.3
    separator_text_border_size: float = 3.0
    separator_text_align: tuple[float, float] = (0.0, 0.5)
    separator_text_padding: tuple[float, float] = (20.0, 3.0)


@dataclass
class Theme:
    """Complete theme configuration."""

    name: str
    colors: ThemeColors = field(default_factory=ThemeColors)
    style: ThemeStyle = field(default_factory=ThemeStyle)


class ThemeManager:
    """Manager for themes and styling."""

    def __init__(self) -> None:
        self.current_theme: Theme | None = None
        self.themes: dict[str, Theme] = {}
        logger.debug("Initialized ThemeManager")

    def register_theme(self, theme: Theme) -> None:
        """Register a theme."""
        self.themes[theme.name] = theme
        logger.debug(f"Registered theme: {theme.name}")

    def apply_theme(self, theme: Theme) -> None:
        """Apply a theme to ImGui. Must be called from the render thread."""
        self.current_theme = theme
        self._apply_colors(theme.colors)
        self._apply_style(theme.style)
        logger.info(f"Applied theme: {theme.name}")

    def apply_theme_by_name(self, name: str) -> bool:
        """Apply a theme by name (case-insensitive). Returns True if found and applied."""
        # Exact match first
        if name in self.themes:
            self.apply_theme(self.themes[name])
            return True
        # Case-insensitive fallback
        name_lower = name.lower()
        for key, theme in self.themes.items():
            if key.lower() == name_lower:
                self.apply_theme(theme)
                return True
        logger.error(f"Theme not found: {name}")
        return False

    def apply_color_scheme(self, scheme: ColorScheme) -> None:
        """Apply a built-in ImGui color scheme."""
        if scheme == ColorScheme.DARK:
            imgui.style_colors_dark()
        elif scheme == ColorScheme.LIGHT:
            imgui.style_colors_light()
        elif scheme == ColorScheme.CLASSIC:
            imgui.style_colors_classic()
        logger.info(f"Applied color scheme: {scheme.value}")

    def get_current_theme(self) -> Theme | None:
        """Get the currently applied theme."""
        return self.current_theme

    def list_themes(self) -> list[str]:
        """List all registered theme names."""
        return list(self.themes.keys())

    def _apply_colors(self, colors: ThemeColors) -> None:
        style = imgui.get_style()
        c = imgui.Col_

        def sc(col: imgui.Col_, value: tuple[float, float, float, float]) -> None:
            style.set_color_(col.value, value)

        sc(c.window_bg, colors.window_bg)
        sc(c.child_bg, colors.child_bg)
        sc(c.popup_bg, colors.popup_bg)
        sc(c.frame_bg, colors.frame_bg)
        sc(c.frame_bg_hovered, colors.frame_bg_hovered)
        sc(c.frame_bg_active, colors.frame_bg_active)
        sc(c.title_bg, colors.title_bg)
        sc(c.title_bg_active, colors.title_bg_active)
        sc(c.title_bg_collapsed, colors.title_bg_collapsed)
        sc(c.menu_bar_bg, colors.menu_bar_bg)
        sc(c.scrollbar_bg, colors.scrollbar_bg)
        sc(c.scrollbar_grab, colors.scrollbar_grab)
        sc(c.scrollbar_grab_hovered, colors.scrollbar_grab_hovered)
        sc(c.scrollbar_grab_active, colors.scrollbar_grab_active)
        sc(c.check_mark, colors.check_mark)
        sc(c.slider_grab, colors.slider_grab)
        sc(c.slider_grab_active, colors.slider_grab_active)
        sc(c.button, colors.button)
        sc(c.button_hovered, colors.button_hovered)
        sc(c.button_active, colors.button_active)
        sc(c.header, colors.header)
        sc(c.header_hovered, colors.header_hovered)
        sc(c.header_active, colors.header_active)
        sc(c.separator, colors.separator)
        sc(c.separator_hovered, colors.separator_hovered)
        sc(c.separator_active, colors.separator_active)
        sc(c.resize_grip, colors.resize_grip)
        sc(c.resize_grip_hovered, colors.resize_grip_hovered)
        sc(c.resize_grip_active, colors.resize_grip_active)
        sc(c.tab, colors.tab)
        sc(c.tab_hovered, colors.tab_hovered)
        # tab_active → tab_selected in newer imgui-bundle
        sc(c.tab_selected, colors.tab_active)
        # tab_unfocused → tab_dimmed; tab_unfocused_active → tab_dimmed_selected
        sc(c.tab_dimmed, colors.tab_unfocused)
        sc(c.tab_dimmed_selected, colors.tab_unfocused_active)
        sc(c.docking_preview, colors.docking_preview)
        sc(c.docking_empty_bg, colors.docking_empty_bg)
        sc(c.plot_lines, colors.plot_lines)
        sc(c.plot_lines_hovered, colors.plot_lines_hovered)
        sc(c.plot_histogram, colors.plot_histogram)
        sc(c.plot_histogram_hovered, colors.plot_histogram_hovered)
        sc(c.text, colors.text)
        sc(c.text_disabled, colors.text_disabled)
        sc(c.text_selected_bg, colors.text_selected_bg)
        sc(c.drag_drop_target, colors.drag_drop_target)
        # nav_highlight → nav_cursor in newer imgui-bundle
        sc(c.nav_cursor, colors.nav_highlight)
        sc(c.nav_windowing_highlight, colors.nav_windowing_highlight)
        sc(c.nav_windowing_dim_bg, colors.nav_windowing_dim_bg)
        sc(c.modal_window_dim_bg, colors.modal_window_dim_bg)

    def _apply_style(self, s: ThemeStyle) -> None:
        style = imgui.get_style()
        style.alpha = s.alpha
        style.disabled_alpha = s.disabled_alpha
        style.window_padding = imgui.ImVec2(*s.window_padding)
        style.window_rounding = s.window_rounding
        style.window_border_size = s.window_border_size
        style.window_min_size = imgui.ImVec2(*s.window_min_size)
        style.window_title_align = imgui.ImVec2(*s.window_title_align)
        style.child_rounding = s.child_rounding
        style.child_border_size = s.child_border_size
        style.popup_rounding = s.popup_rounding
        style.popup_border_size = s.popup_border_size
        style.frame_padding = imgui.ImVec2(*s.frame_padding)
        style.frame_rounding = s.frame_rounding
        style.frame_border_size = s.frame_border_size
        style.item_spacing = imgui.ImVec2(*s.item_spacing)
        style.item_inner_spacing = imgui.ImVec2(*s.item_inner_spacing)
        style.touch_extra_padding = imgui.ImVec2(*s.touch_extra_padding)
        style.indent_spacing = s.indent_spacing
        style.columns_min_spacing = s.columns_min_spacing
        style.scrollbar_size = s.scrollbar_size
        style.scrollbar_rounding = s.scrollbar_rounding
        style.grab_min_size = s.grab_min_size
        style.grab_rounding = s.grab_rounding
        style.tab_rounding = s.tab_rounding
        style.tab_border_size = s.tab_border_size
        # tab_min_width_for_close_button was renamed to tab_min_width_base in newer imgui-bundle
        style.tab_min_width_base = s.tab_min_width_for_close_button
        style.button_text_align = imgui.ImVec2(*s.button_text_align)
        style.selectable_text_align = imgui.ImVec2(*s.selectable_text_align)
        style.display_window_padding = imgui.ImVec2(*s.display_window_padding)
        style.display_safe_area_padding = imgui.ImVec2(*s.display_safe_area_padding)
        style.curve_tessellation_tol = s.curve_tessellation_tol
        style.circle_tessellation_max_error = s.circle_tessellation_max_error
        style.separator_text_border_size = s.separator_text_border_size
        style.separator_text_align = imgui.ImVec2(*s.separator_text_align)
        style.separator_text_padding = imgui.ImVec2(*s.separator_text_padding)
