"""Tests for NotificationManager."""

from unittest.mock import MagicMock, patch

from champi_imgui.extensions.notification import (
    Notification,
    NotificationManager,
    NotificationType,
)


class TestNotificationType:
    def test_values(self) -> None:
        assert NotificationType.INFO.value == "info"
        assert NotificationType.SUCCESS.value == "success"
        assert NotificationType.WARNING.value == "warning"
        assert NotificationType.ERROR.value == "error"


class TestNotification:
    def test_creation(self) -> None:
        n = Notification(title="Title", message="Msg", type=NotificationType.INFO)
        assert n.title == "Title"
        assert n.message == "Msg"
        assert n.type == NotificationType.INFO
        assert n.visible is True
        assert n.duration == 3.0


class TestNotificationManager:
    def test_init(self) -> None:
        manager = NotificationManager()
        assert manager.notifications == []
        assert manager.max_notifications == 5

    def test_add_info(self) -> None:
        manager = NotificationManager()
        with patch("champi_imgui.extensions.notification.imgui") as mock_imgui:
            mock_imgui.get_time.return_value = 0.0
            manager.add("Title", "Msg", NotificationType.INFO)
        assert len(manager.notifications) == 1
        assert manager.notifications[0].title == "Title"
        assert manager.notifications[0].type == NotificationType.INFO

    def test_convenience_methods(self) -> None:
        manager = NotificationManager()
        with patch("champi_imgui.extensions.notification.imgui") as mock_imgui:
            mock_imgui.get_time.return_value = 0.0
            manager.info("i", "msg")
            manager.success("s", "msg")
            manager.warning("w", "msg")
            manager.error("e", "msg")
        assert len(manager.notifications) == 4
        types = [n.type for n in manager.notifications]
        assert NotificationType.INFO in types
        assert NotificationType.SUCCESS in types
        assert NotificationType.WARNING in types
        assert NotificationType.ERROR in types

    def test_max_notifications_drops_oldest(self) -> None:
        manager = NotificationManager(max_notifications=2)
        with patch("champi_imgui.extensions.notification.imgui") as mock_imgui:
            mock_imgui.get_time.return_value = 0.0
            manager.add("A", "a", NotificationType.INFO)
            manager.add("B", "b", NotificationType.INFO)
            manager.add("C", "c", NotificationType.INFO)
        assert len(manager.notifications) == 2
        assert manager.notifications[0].title == "B"
        assert manager.notifications[1].title == "C"

    def test_clear_all(self) -> None:
        manager = NotificationManager()
        with patch("champi_imgui.extensions.notification.imgui") as mock_imgui:
            mock_imgui.get_time.return_value = 0.0
            manager.add("T", "M", NotificationType.INFO)
        manager.clear_all()
        assert manager.notifications == []

    def test_get_notification_count(self) -> None:
        manager = NotificationManager()
        with patch("champi_imgui.extensions.notification.imgui") as mock_imgui:
            mock_imgui.get_time.return_value = 0.0
            manager.add("T", "M", NotificationType.INFO)
            manager.add("T2", "M2", NotificationType.WARNING)
        assert manager.get_notification_count() == 2

    def test_expired_notifications_removed_on_render(self) -> None:
        manager = NotificationManager()
        with patch("champi_imgui.extensions.notification.imgui") as mock_imgui:
            mock_imgui.get_time.return_value = 0.0
            manager.add("T", "M", NotificationType.INFO, duration=1.0)
            # Advance time past duration
            mock_imgui.get_time.return_value = 5.0
            mock_imgui.get_main_viewport.return_value = MagicMock(
                size=MagicMock(x=1920, y=1080)
            )
            manager.render()
        assert len(manager.notifications) == 0

    def test_persistent_notification_not_removed(self) -> None:
        manager = NotificationManager()
        with patch("champi_imgui.extensions.notification.imgui") as mock_imgui:
            mock_imgui.get_time.return_value = 0.0
            manager.add("T", "M", NotificationType.INFO, duration=0)  # persistent
            mock_imgui.get_time.return_value = 1000.0
            mock_imgui.get_main_viewport.return_value = MagicMock(
                size=MagicMock(x=1920, y=1080)
            )
            manager.render()
        assert len(manager.notifications) == 1
