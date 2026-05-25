"""Unit tests for MCP server tool functions.

Tests call tool functions directly via FunctionTool.fn against a real
CanvasManager with auto_start=False (no ImGui render thread required).
"""

import contextlib
import uuid

import pytest

import champi_imgui.api.server as _srv_mod
from champi_imgui.api.server import create_mcp_app
from champi_imgui.core.canvas import CanvasManager

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
def fresh_canvas_manager(monkeypatch):
    manager = CanvasManager()
    monkeypatch.setattr(manager, "ensure_canvas_running", lambda canvas_id: True)
    _Server._mcp = create_mcp_app(canvas_manager=manager)
    yield manager
    for canvas in list(manager.canvases.values()):
        with contextlib.suppress(Exception):
            canvas.shm_manager.cleanup()
    _Server._mcp = None


@pytest.fixture()
def cid() -> str:
    """Return a unique canvas ID per test to avoid shared-memory name collisions."""
    return f"c_{uuid.uuid4().hex[:8]}"


# ---------------------------------------------------------------------------
# list_canvases
# ---------------------------------------------------------------------------


def test_list_canvases_empty():
    result = server.list_canvases.fn()
    assert result["success"] is True
    assert result["data"]["canvas_ids"] == []
    assert result["data"]["count"] == 0


# ---------------------------------------------------------------------------
# create_canvas
# ---------------------------------------------------------------------------


def test_create_canvas_success(cid):
    result = server.create_canvas.fn(cid, title="Test", auto_start=False)
    assert result["success"] is True
    assert result["data"]["canvas_id"] == cid
    assert result["data"]["title"] == "Test"


def test_create_canvas_duplicate(cid):
    server.create_canvas.fn(cid, auto_start=False)
    result = server.create_canvas.fn(cid, auto_start=False)
    assert result["success"] is False
    assert "already exists" in result["error"]


def test_create_canvas_appears_in_list(cid):
    server.create_canvas.fn(cid, auto_start=False)
    server.create_canvas.fn(cid + "_2", auto_start=False)
    result = server.list_canvases.fn()
    assert result["success"] is True
    assert set(result["data"]["canvas_ids"]) == {cid, cid + "_2"}
    assert result["data"]["count"] == 2


def test_create_canvas_default_size(cid):
    result = server.create_canvas.fn(cid, auto_start=False)
    assert result["data"]["size"] == [800, 600]


def test_create_canvas_custom_size(cid):
    result = server.create_canvas.fn(cid, width=1280, height=720, auto_start=False)
    assert result["data"]["size"] == [1280, 720]


# ---------------------------------------------------------------------------
# get_canvas_state
# ---------------------------------------------------------------------------


def test_get_canvas_state_not_found():
    result = server.get_canvas_state.fn("nonexistent")
    assert result["success"] is False
    assert "not found" in result["error"]


def test_get_canvas_state_success(cid):
    server.create_canvas.fn(cid, title="MyCanvas", auto_start=False)
    result = server.get_canvas_state.fn(cid)
    assert result["success"] is True
    assert result["data"]["canvas_id"] == cid
    assert result["data"]["title"] == "MyCanvas"


def test_get_canvas_state_includes_registered_widgets(cid):
    """get_canvas_state must report widgets from widget_registry, not canvas.state.widgets."""
    server.create_canvas.fn(cid, auto_start=False)
    server.add_drawing_area.fn(cid, "draw1")

    result = server.get_canvas_state.fn(cid)

    assert result["success"] is True
    widgets = result["data"]["widgets"]
    assert "draw1" in widgets, "DrawingWidget must appear in get_canvas_state response"


def test_get_canvas_state_widgets_empty_before_add(cid):
    """get_canvas_state returns an empty widgets dict when no widgets have been added."""
    server.create_canvas.fn(cid, auto_start=False)

    result = server.get_canvas_state.fn(cid)

    assert result["success"] is True
    assert result["data"]["widgets"] == {}


# ---------------------------------------------------------------------------
# shutdown_canvas
# ---------------------------------------------------------------------------


def test_shutdown_canvas_not_found():
    result = server.shutdown_canvas.fn("ghost")
    assert result["success"] is False
    assert "not found" in result["error"]


def test_shutdown_canvas_removes_from_list(cid):
    server.create_canvas.fn(cid, auto_start=False)
    result = server.shutdown_canvas.fn(cid)
    assert result["success"] is True
    assert result["data"]["shutdown"] is True
    assert cid not in server.list_canvases.fn()["data"]["canvas_ids"]


# ---------------------------------------------------------------------------
# _create_widget_in_canvas helper — canvas not found
# ---------------------------------------------------------------------------


def test_create_widget_canvas_not_found():
    result = server._create_widget_in_canvas("ghost", object())
    assert result["success"] is False
    assert "not found" in result["error"]


# ---------------------------------------------------------------------------
# Widget tools — canvas not found (covers every tool's error branch)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "fn,kwargs",
    [
        (server.add_button, {"canvas_id": "x", "widget_id": "w"}),
        (server.add_small_button, {"canvas_id": "x", "widget_id": "w"}),
        (server.add_arrow_button, {"canvas_id": "x", "widget_id": "w"}),
        (server.add_invisible_button, {"canvas_id": "x", "widget_id": "w"}),
        (server.add_text, {"canvas_id": "x", "widget_id": "w"}),
        (server.add_colored_text, {"canvas_id": "x", "widget_id": "w"}),
        (server.add_disabled_text, {"canvas_id": "x", "widget_id": "w"}),
        (server.add_wrapped_text, {"canvas_id": "x", "widget_id": "w"}),
        (server.add_bullet_text, {"canvas_id": "x", "widget_id": "w"}),
        (server.add_bullet, {"canvas_id": "x", "widget_id": "w"}),
        (server.add_label_text, {"canvas_id": "x", "widget_id": "w"}),
        (server.add_input_text, {"canvas_id": "x", "widget_id": "w"}),
        (server.add_checkbox, {"canvas_id": "x", "widget_id": "w"}),
        (server.add_input_int, {"canvas_id": "x", "widget_id": "w"}),
        (server.add_input_float, {"canvas_id": "x", "widget_id": "w"}),
        (server.add_input_double, {"canvas_id": "x", "widget_id": "w"}),
        (server.add_radio_button, {"canvas_id": "x", "widget_id": "w"}),
        (server.add_combo, {"canvas_id": "x", "widget_id": "w"}),
        (server.add_list_box, {"canvas_id": "x", "widget_id": "w"}),
        (server.add_color_picker, {"canvas_id": "x", "widget_id": "w"}),
        (server.add_color_picker3, {"canvas_id": "x", "widget_id": "w"}),
        (server.add_color_edit3, {"canvas_id": "x", "widget_id": "w"}),
        (server.add_color_edit4, {"canvas_id": "x", "widget_id": "w"}),
        (server.add_color_button, {"canvas_id": "x", "widget_id": "w"}),
        (server.add_progress_bar, {"canvas_id": "x", "widget_id": "w"}),
        (server.add_slider_int, {"canvas_id": "x", "widget_id": "w"}),
        (server.add_slider_float, {"canvas_id": "x", "widget_id": "w"}),
        (server.add_drag_int, {"canvas_id": "x", "widget_id": "w"}),
        (server.add_drag_float, {"canvas_id": "x", "widget_id": "w"}),
        (server.add_window, {"canvas_id": "x", "widget_id": "w"}),
        (server.add_child_window, {"canvas_id": "x", "widget_id": "w"}),
        (server.add_group, {"canvas_id": "x", "widget_id": "w"}),
        (server.add_collapsing_header, {"canvas_id": "x", "widget_id": "w"}),
        (server.add_tab_bar, {"canvas_id": "x", "widget_id": "w"}),
        (
            server.add_tab_item,
            {"canvas_id": "x", "widget_id": "w", "tab_bar_id": "bar"},
        ),
        (server.add_separator, {"canvas_id": "x", "widget_id": "w"}),
        (server.add_spacing, {"canvas_id": "x", "widget_id": "w"}),
        (server.add_dummy, {"canvas_id": "x", "widget_id": "w"}),
        (server.add_plot_lines, {"canvas_id": "x", "widget_id": "w"}),
        (server.add_help_marker, {"canvas_id": "x", "widget_id": "w"}),
        (server.add_menu_bar, {"canvas_id": "x", "widget_id": "w"}),
        (server.add_menu, {"canvas_id": "x", "widget_id": "w"}),
        (server.add_menu_item, {"canvas_id": "x", "widget_id": "w"}),
        (server.add_tree_node, {"canvas_id": "x", "widget_id": "w"}),
        (server.add_tooltip, {"canvas_id": "x", "widget_id": "w"}),
        (server.add_popup, {"canvas_id": "x", "widget_id": "w"}),
        (server.add_context_menu, {"canvas_id": "x", "widget_id": "w"}),
        (server.add_line_chart, {"canvas_id": "x", "widget_id": "w"}),
        (server.add_bar_chart, {"canvas_id": "x", "widget_id": "w"}),
        (server.add_scatter_plot, {"canvas_id": "x", "widget_id": "w"}),
        (server.add_pie_chart, {"canvas_id": "x", "widget_id": "w"}),
        (server.add_heatmap, {"canvas_id": "x", "widget_id": "w"}),
    ],
)
def test_widget_tool_canvas_not_found(fn, kwargs):
    result = fn.fn(**kwargs)
    assert result["success"] is False
    assert "not found" in result["error"]


# ---------------------------------------------------------------------------
# Widget tools — success paths (canvas with auto_start=False)
# ---------------------------------------------------------------------------


def test_add_button_success(cid):
    server.create_canvas.fn(cid, auto_start=False)
    result = server.add_button.fn(cid, "btn1", label="OK")
    assert result["success"] is True
    assert result["data"]["widget_id"] == "btn1"


def test_add_text_success(cid):
    server.create_canvas.fn(cid, auto_start=False)
    result = server.add_text.fn(cid, "txt1", text="Hello")
    assert result["success"] is True
    assert result["data"]["widget_id"] == "txt1"


def test_add_checkbox_success(cid):
    server.create_canvas.fn(cid, auto_start=False)
    result = server.add_checkbox.fn(cid, "chk1", label="Enable", checked=True)
    assert result["success"] is True
    assert result["data"]["widget_id"] == "chk1"


def test_add_slider_float_success(cid):
    server.create_canvas.fn(cid, auto_start=False)
    result = server.add_slider_float.fn(cid, "sl1", value=0.5, v_min=0.0, v_max=1.0)
    assert result["success"] is True
    assert result["data"]["widget_id"] == "sl1"


def test_add_slider_int_success(cid):
    server.create_canvas.fn(cid, auto_start=False)
    result = server.add_slider_int.fn(cid, "sl1", value=5, v_min=0, v_max=10)
    assert result["success"] is True
    assert result["data"]["widget_id"] == "sl1"


def test_add_drag_float_success(cid):
    server.create_canvas.fn(cid, auto_start=False)
    result = server.add_drag_float.fn(cid, "df1", value=0.25)
    assert result["success"] is True
    assert result["data"]["widget_id"] == "df1"


def test_add_drag_int_success(cid):
    server.create_canvas.fn(cid, auto_start=False)
    result = server.add_drag_int.fn(cid, "di1", value=3)
    assert result["success"] is True
    assert result["data"]["widget_id"] == "di1"


def test_add_progress_bar_success(cid):
    server.create_canvas.fn(cid, auto_start=False)
    result = server.add_progress_bar.fn(cid, "pb1", value=0.75)
    assert result["success"] is True
    assert result["data"]["widget_id"] == "pb1"


def test_add_input_text_success(cid):
    server.create_canvas.fn(cid, auto_start=False)
    result = server.add_input_text.fn(cid, "inp1", value="hello")
    assert result["success"] is True
    assert result["data"]["widget_id"] == "inp1"


def test_add_combo_success(cid):
    server.create_canvas.fn(cid, auto_start=False)
    result = server.add_combo.fn(cid, "cmb1", items=["a", "b", "c"])
    assert result["success"] is True
    assert result["data"]["widget_id"] == "cmb1"


def test_add_separator_success(cid):
    server.create_canvas.fn(cid, auto_start=False)
    result = server.add_separator.fn(cid, "sep1")
    assert result["success"] is True
    assert result["data"]["widget_id"] == "sep1"


def test_add_color_picker_success(cid):
    server.create_canvas.fn(cid, auto_start=False)
    result = server.add_color_picker.fn(cid, "cp1")
    assert result["success"] is True
    assert result["data"]["widget_id"] == "cp1"


def test_add_line_chart_success(cid):
    server.create_canvas.fn(cid, auto_start=False)
    result = server.add_line_chart.fn(cid, "lc1")
    assert result["success"] is True
    assert result["data"]["widget_id"] == "lc1"


def test_add_menu_bar_success(cid):
    server.create_canvas.fn(cid, auto_start=False)
    result = server.add_menu_bar.fn(cid, "mb1")
    assert result["success"] is True
    assert result["data"]["widget_id"] == "mb1"


def test_add_tree_node_success(cid):
    server.create_canvas.fn(cid, auto_start=False)
    result = server.add_tree_node.fn(cid, "tn1", label="Node")
    assert result["success"] is True
    assert result["data"]["widget_id"] == "tn1"


def test_multiple_widgets_on_same_canvas(cid):
    server.create_canvas.fn(cid, auto_start=False)
    server.add_button.fn(cid, "btn1")
    server.add_text.fn(cid, "txt1")
    server.add_slider_float.fn(cid, "sl1")
    canvas = server.canvas_manager.get_canvas(cid)
    assert canvas is not None
    assert len(canvas.widget_registry.get_all()) == 3


def test_widget_data_contains_expected_keys(cid):
    server.create_canvas.fn(cid, auto_start=False)
    result = server.add_button.fn(cid, "btn1", label="Test")
    data = result["data"]
    assert "widget_id" in data
    assert "widget_type" in data
    assert "visible" in data
    assert "enabled" in data
