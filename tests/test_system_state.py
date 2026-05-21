"""Tests for to_diagnostics() methods and system-state MCP tools (issues #135-#140)."""

from unittest.mock import MagicMock, patch

# ─────────────────────────── AnimationManager ────────────────────────────────


def test_animation_manager_diagnostics_empty():
    from champi_imgui.extensions.animation import AnimationManager

    mgr = AnimationManager()
    d = mgr.to_diagnostics()
    assert d["active_count"] == 0
    assert d["total_count"] == 0
    assert d["animations"] == []


def test_animation_manager_diagnostics_enum_values():
    from champi_imgui.extensions.animation import (
        AnimationManager,
        AnimationState,
        EasingFunction,
    )

    mgr = AnimationManager()
    mgr.create("fade", 0.0, 1.0, 0.5, easing=EasingFunction.LINEAR)
    d = mgr.to_diagnostics()
    assert d["total_count"] == 1
    anim = d["animations"][0]
    # state and easing must be string values, not enum instances
    assert isinstance(anim["state"], str)
    assert isinstance(anim["easing"], str)
    assert anim["state"] == AnimationState.IDLE.value
    assert anim["easing"] == EasingFunction.LINEAR.value


# ─────────────────────────── NotificationManager ─────────────────────────────


def test_notification_manager_diagnostics_empty():
    from champi_imgui.extensions.notification import NotificationManager

    mgr = NotificationManager()
    d = mgr.to_diagnostics()
    assert d["queued_count"] == 0
    assert d["recent"] == []


def test_notification_manager_diagnostics_with_entry():
    from champi_imgui.extensions.notification import (
        NotificationManager,
        NotificationType,
    )

    mgr = NotificationManager()
    with patch("champi_imgui.extensions.notification.imgui") as mock_imgui:
        mock_imgui.get_time.return_value = 0.0
        mgr.add("Title", "Body", NotificationType.INFO, duration=5.0)
    d = mgr.to_diagnostics()
    assert d["queued_count"] == 1
    n = d["recent"][0]
    assert isinstance(n["type"], str)
    assert n["type"] == NotificationType.INFO.value


# ──────────────────────────── LayoutManager ──────────────────────────────────


def test_layout_manager_diagnostics_defaults():
    from champi_imgui.layout.manager import LayoutManager, LayoutMode

    mgr = LayoutManager()
    d = mgr.to_diagnostics()
    assert d["mode"] == LayoutMode.FREE.value
    assert isinstance(d["mode"], str)
    assert "spacing" in d
    assert "grid_columns" in d


def test_layout_manager_diagnostics_after_mode_change():
    from champi_imgui.layout.manager import LayoutManager, LayoutMode

    mgr = LayoutManager()
    mgr.set_mode(LayoutMode.GRID)
    mgr.set_grid_columns(4)
    d = mgr.to_diagnostics()
    assert d["mode"] == LayoutMode.GRID.value
    assert d["grid_columns"] == 4


# ──────────────────────────── DataStore ──────────────────────────────────────


def test_data_store_diagnostics_empty():
    from champi_imgui.core.binding import DataStore

    ds = DataStore()
    d = ds.to_diagnostics()
    assert d["key_count"] == 0
    assert d["signal_path_count"] == 0
    assert d["signal_paths"] == []


def test_data_store_diagnostics_with_data():
    from champi_imgui.core.binding import DataStore

    ds = DataStore()
    ds.set("foo", 42)
    ds.set("bar.baz", "hello")
    d = ds.to_diagnostics()
    assert d["key_count"] == 2
    assert d["signal_path_count"] == 2
    paths = [p["path"] for p in d["signal_paths"]]
    assert "foo" in paths
    assert "bar.baz" in paths


# ─────────────────────────── BindingManager ──────────────────────────────────


def test_binding_manager_diagnostics_empty():
    from champi_imgui.core.binding import BindingManager, DataStore

    mgr = BindingManager(DataStore())
    d = mgr.to_diagnostics()
    assert d["binding_count"] == 0
    assert d["paths"] == []


def test_binding_manager_diagnostics_with_binding():
    from champi_imgui.core.binding import BindingManager, DataStore

    ds = DataStore()
    mgr = BindingManager(ds)
    mgr.bind("sensor.temp", "label_01", "text")
    d = mgr.to_diagnostics()
    assert d["binding_count"] == 1
    assert "sensor.temp" in d["paths"]


# ──────────────────────────── EventQueue ─────────────────────────────────────


def test_event_queue_diagnostics_empty():
    from champi_imgui.core.events import EventQueue

    q = EventQueue()
    d = q.to_diagnostics()
    assert d["pending_count"] == 0
    assert d["subscription_count"] == 0


def test_event_queue_diagnostics_with_subscription():
    from champi_imgui.core.events import EventQueue

    q = EventQueue()
    q.subscribe("btn1", ["click"])
    q.push("btn1", "click", {"x": 10})
    d = q.to_diagnostics()
    assert d["pending_count"] == 1
    assert d["subscription_count"] == 1


# ─────────────────────────── TemplateManager ─────────────────────────────────


def test_template_manager_diagnostics_empty(tmp_path):
    from champi_imgui.core.serialization import TemplateManager

    mgr = TemplateManager(template_dir=str(tmp_path))
    d = mgr.to_diagnostics()
    assert d["saved"] == []
    assert d["cached"] == []


# ─────────────────────────── ThemeManager ────────────────────────────────────


def test_theme_manager_diagnostics_no_theme():
    from champi_imgui.themes.manager import ThemeManager

    mgr = ThemeManager()
    d = mgr.to_diagnostics()
    assert d["current"] is None
    assert d["available"] == []


def test_theme_manager_diagnostics_after_register():
    from champi_imgui.themes.manager import Theme, ThemeManager

    mgr = ThemeManager()
    mgr.register_theme(Theme(name="dark"))
    mgr.register_theme(Theme(name="light"))
    d = mgr.to_diagnostics()
    assert d["current"] is None
    assert set(d["available"]) == {"dark", "light"}


# ──────────────────────── get_system_state tool ──────────────────────────────


def _patch_managers(monkeypatch):
    """Return a dict of minimal mock managers for server.main globals."""
    from champi_imgui.server import main as m

    mock_canvas_mgr = MagicMock()
    mock_canvas_mgr.list_canvases.return_value = []

    monkeypatch.setattr(m, "canvas_manager", mock_canvas_mgr)
    monkeypatch.setattr(
        m,
        "animation_manager",
        MagicMock(
            **{
                "to_diagnostics.return_value": {
                    "active_count": 0,
                    "total_count": 0,
                    "animations": [],
                }
            }
        ),
    )
    monkeypatch.setattr(
        m,
        "data_store",
        MagicMock(
            **{
                "to_diagnostics.return_value": {
                    "key_count": 0,
                    "signal_path_count": 0,
                    "signal_paths": [],
                }
            }
        ),
    )
    monkeypatch.setattr(
        m,
        "binding_manager",
        MagicMock(**{"to_diagnostics.return_value": {"binding_count": 0, "paths": []}}),
    )
    monkeypatch.setattr(
        m,
        "layout_manager",
        MagicMock(
            **{
                "to_diagnostics.return_value": {
                    "mode": "free",
                    "spacing": 5.0,
                    "grid_columns": 3,
                }
            }
        ),
    )
    monkeypatch.setattr(
        m,
        "theme_manager",
        MagicMock(
            **{"to_diagnostics.return_value": {"current": None, "available": []}}
        ),
    )
    monkeypatch.setattr(
        m,
        "template_manager",
        MagicMock(**{"to_diagnostics.return_value": {"saved": [], "cached": []}}),
    )
    monkeypatch.setattr(
        m,
        "notification_manager",
        MagicMock(
            **{"to_diagnostics.return_value": {"pending_count": 0, "notifications": []}}
        ),
    )
    monkeypatch.setattr(
        m,
        "event_queue",
        MagicMock(
            **{
                "to_diagnostics.return_value": {
                    "pending_count": 0,
                    "subscription_count": 0,
                }
            }
        ),
    )

    return mock_canvas_mgr


def test_get_system_state_success(monkeypatch):
    from champi_imgui.server import main as m

    _patch_managers(monkeypatch)

    result = m.get_system_state.fn()
    assert result["success"] is True
    data = result["data"]
    assert "version" in data
    assert "uptime_seconds" in data
    assert data["uptime_seconds"] >= 0
    assert data["canvas_count"] == 0
    assert data["canvases"] == []
    assert "managers" in data
    assert "signals" in data
    assert "canvas_updated" in data["signals"]
    assert "widget_created" in data["signals"]
    assert "widget_updated" in data["signals"]


def test_get_system_state_managers_keys(monkeypatch):
    from champi_imgui.server import main as m

    _patch_managers(monkeypatch)

    result = m.get_system_state.fn()
    managers = result["data"]["managers"]
    assert set(managers.keys()) == {
        "animations",
        "data_store",
        "bindings",
        "layout",
        "themes",
        "templates",
        "notifications",
        "events",
    }


# ────────────────────────── get_canvas_diagnostics ───────────────────────────


def test_get_canvas_diagnostics_not_found(monkeypatch):
    from champi_imgui.server import main as m

    mock_mgr = MagicMock()
    mock_mgr.get_canvas.return_value = None
    monkeypatch.setattr(m, "canvas_manager", mock_mgr)

    result = m.get_canvas_diagnostics.fn("missing_canvas")
    assert result["success"] is False
    assert "not found" in result["error"]


def test_get_canvas_diagnostics_healthy_canvas(monkeypatch):
    from champi_imgui.server import main as m

    mock_widget = MagicMock()
    mock_widget.__class__.__name__ = "ButtonWidget"
    mock_widget.state.visible = True
    mock_widget.state.enabled = True

    mock_registry = MagicMock()
    mock_registry.get_all.return_value = {"btn1": mock_widget}

    mock_canvas = MagicMock()
    mock_canvas.state.title = "Test Canvas"
    mock_canvas.state.size = (800, 600)
    mock_canvas.widget_registry = mock_registry
    mock_canvas.is_render_healthy.return_value = True
    mock_canvas._render_thread = MagicMock()
    mock_canvas._render_thread.is_alive.return_value = True
    mock_canvas._render_error = None

    mock_mgr = MagicMock()
    mock_mgr.get_canvas.return_value = mock_canvas
    monkeypatch.setattr(m, "canvas_manager", mock_mgr)

    result = m.get_canvas_diagnostics.fn("canvas1")
    assert result["success"] is True
    data = result["data"]
    assert data["canvas_id"] == "canvas1"
    assert data["title"] == "Test Canvas"
    assert data["size"] == [800, 600]
    assert data["widget_count"] == 1
    assert len(data["widgets"]) == 1
    assert data["widgets"][0]["widget_id"] == "btn1"
    assert data["render"]["is_healthy"] is True
    assert data["render"]["last_error"] is None
