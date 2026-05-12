"""Tests for LayoutManager and AutoLayout."""

from unittest.mock import call, patch

import pytest

from champi_imgui.layout.manager import AutoLayout, LayoutManager, LayoutMode


class TestLayoutMode:
    def test_values(self) -> None:
        assert LayoutMode.HORIZONTAL.value == "horizontal"
        assert LayoutMode.VERTICAL.value == "vertical"
        assert LayoutMode.GRID.value == "grid"
        assert LayoutMode.STACK.value == "stack"
        assert LayoutMode.FREE.value == "free"


class TestLayoutManager:
    def test_init_defaults(self) -> None:
        manager = LayoutManager()
        assert manager.mode == LayoutMode.FREE
        assert manager.spacing == 5.0
        assert manager.padding == 10.0
        assert manager.grid_columns == 3

    def test_set_mode(self) -> None:
        manager = LayoutManager()
        manager.set_mode(LayoutMode.HORIZONTAL)
        assert manager.mode == LayoutMode.HORIZONTAL

    def test_set_mode_resets_col(self) -> None:
        manager = LayoutManager()
        manager._current_col = 2
        manager.set_mode(LayoutMode.GRID)
        assert manager._current_col == 0

    def test_set_spacing(self) -> None:
        manager = LayoutManager()
        manager.set_spacing(15.0)
        assert manager.spacing == 15.0

    def test_set_padding(self) -> None:
        manager = LayoutManager()
        manager.set_padding(20.0)
        assert manager.padding == 20.0

    def test_set_grid_columns(self) -> None:
        manager = LayoutManager()
        manager.set_grid_columns(4)
        assert manager.grid_columns == 4

    def test_set_grid_columns_minimum_one(self) -> None:
        manager = LayoutManager()
        manager.set_grid_columns(0)
        assert manager.grid_columns == 1

    def test_begin_layout_stack(self) -> None:
        manager = LayoutManager()
        manager.set_mode(LayoutMode.STACK)
        with patch("champi_imgui.layout.manager.imgui") as mock_imgui:
            manager.begin_layout()
            mock_imgui.begin_group.assert_called_once()

    def test_end_layout_stack(self) -> None:
        manager = LayoutManager()
        manager.set_mode(LayoutMode.STACK)
        with patch("champi_imgui.layout.manager.imgui") as mock_imgui:
            manager.end_layout()
            mock_imgui.end_group.assert_called_once()

    def test_end_layout_non_stack(self) -> None:
        manager = LayoutManager()
        manager.set_mode(LayoutMode.HORIZONTAL)
        with patch("champi_imgui.layout.manager.imgui") as mock_imgui:
            manager.end_layout()
            mock_imgui.end_group.assert_not_called()

    def test_next_widget_horizontal(self) -> None:
        manager = LayoutManager()
        manager.set_mode(LayoutMode.HORIZONTAL)
        with patch("champi_imgui.layout.manager.imgui") as mock_imgui:
            manager.next_widget_position()
            mock_imgui.same_line.assert_called_once_with(0, manager.spacing)

    def test_next_widget_free_no_call(self) -> None:
        manager = LayoutManager()
        manager.set_mode(LayoutMode.FREE)
        with patch("champi_imgui.layout.manager.imgui") as mock_imgui:
            manager.next_widget_position()
            mock_imgui.same_line.assert_not_called()
            mock_imgui.dummy.assert_not_called()

    def test_next_widget_grid_wraps(self) -> None:
        manager = LayoutManager()
        manager.set_mode(LayoutMode.GRID)
        manager.grid_columns = 2
        with patch("champi_imgui.layout.manager.imgui") as mock_imgui:
            manager.next_widget_position()  # col 0 -> 1, no wrap
            mock_imgui.same_line.assert_called_once()
            manager.next_widget_position()  # col 1 -> 0, wrap (dummy)
            mock_imgui.dummy.assert_called_once()

    def test_add_spacing(self) -> None:
        manager = LayoutManager()
        with patch("champi_imgui.layout.manager.imgui") as mock_imgui:
            manager.add_spacing(3)
            assert mock_imgui.spacing.call_count == 3

    def test_add_separator(self) -> None:
        manager = LayoutManager()
        with patch("champi_imgui.layout.manager.imgui") as mock_imgui:
            manager.add_separator()
            mock_imgui.separator.assert_called_once()

    def test_indent_unindent(self) -> None:
        manager = LayoutManager()
        with patch("champi_imgui.layout.manager.imgui") as mock_imgui:
            manager.indent(10.0)
            mock_imgui.indent.assert_called_once_with(10.0)
            manager.unindent(10.0)
            mock_imgui.unindent.assert_called_once_with(10.0)

    def test_push_pop_item_width(self) -> None:
        manager = LayoutManager()
        with patch("champi_imgui.layout.manager.imgui") as mock_imgui:
            manager.push_item_width(100.0)
            mock_imgui.push_item_width.assert_called_once_with(100.0)
            manager.pop_item_width()
            mock_imgui.pop_item_width.assert_called_once()


class TestAutoLayout:
    def test_context_manager(self) -> None:
        manager = LayoutManager()
        original_mode = manager.mode
        with patch.object(manager, "begin_layout") as mock_begin, \
             patch.object(manager, "end_layout") as mock_end:
            with AutoLayout(manager, LayoutMode.HORIZONTAL) as m:
                assert m is manager
                assert manager.mode == LayoutMode.HORIZONTAL
            assert manager.mode == original_mode
            mock_begin.assert_called_once()
            mock_end.assert_called_once()
