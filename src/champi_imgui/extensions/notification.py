"""Notification system for toast-style UI messages."""

from dataclasses import dataclass
from enum import Enum

from imgui_bundle import imgui
from loguru import logger


class NotificationType(Enum):
    """Notification severity types."""

    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class Notification:
    """A single notification entry."""

    title: str
    message: str
    type: NotificationType
    duration: float = 3.0
    dismissible: bool = True
    timestamp: float = 0.0
    visible: bool = True


class NotificationManager:
    """Manager for toast-style notifications. render() must be called each frame."""

    def __init__(self, max_notifications: int = 5) -> None:
        self.notifications: list[Notification] = []
        self.max_notifications = max_notifications
        self.notification_height = 80.0
        self.notification_width = 300.0
        self.padding = 10.0
        logger.debug("Initialized NotificationManager")

    def add(
        self,
        title: str,
        message: str,
        type: NotificationType = NotificationType.INFO,
        duration: float = 3.0,
        dismissible: bool = True,
    ) -> None:
        """Add a notification. Oldest is dropped when max is exceeded."""
        notification = Notification(
            title=title,
            message=message,
            type=type,
            duration=duration,
            dismissible=dismissible,
            timestamp=imgui.get_time(),
        )
        self.notifications.append(notification)
        if len(self.notifications) > self.max_notifications:
            self.notifications.pop(0)
        logger.debug(f"Added notification: {title} ({type.value})")

    def info(self, title: str, message: str, duration: float = 3.0) -> None:
        self.add(title, message, NotificationType.INFO, duration)

    def success(self, title: str, message: str, duration: float = 3.0) -> None:
        self.add(title, message, NotificationType.SUCCESS, duration)

    def warning(self, title: str, message: str, duration: float = 4.0) -> None:
        self.add(title, message, NotificationType.WARNING, duration)

    def error(self, title: str, message: str, duration: float = 5.0) -> None:
        self.add(title, message, NotificationType.ERROR, duration)

    def render(self) -> None:
        """Render active notifications as overlays. Must be called from the render thread."""
        current_time = imgui.get_time()
        viewport = imgui.get_main_viewport()
        size = viewport.size

        self.notifications = [
            n
            for n in self.notifications
            if n.visible
            and (n.duration == 0 or current_time - n.timestamp < n.duration)
        ]

        y_offset = size.y - self.padding
        for i, notification in enumerate(reversed(self.notifications)):
            y_offset -= self.notification_height + self.padding
            x_pos = size.x - self.notification_width - self.padding
            self._render_notification(notification, x_pos, y_offset, i)

    def clear_all(self) -> None:
        """Remove all notifications."""
        self.notifications.clear()

    def get_notification_count(self) -> int:
        return len(self.notifications)

    def _render_notification(
        self, notification: Notification, x: float, y: float, index: int
    ) -> None:
        window_id = f"##notification_{index}"
        imgui.set_next_window_pos(imgui.ImVec2(x, y))
        imgui.set_next_window_size(
            imgui.ImVec2(self.notification_width, self.notification_height)
        )
        flags = (
            imgui.WindowFlags_.no_decoration
            | imgui.WindowFlags_.no_move
            | imgui.WindowFlags_.no_saved_settings
            | imgui.WindowFlags_.no_focus_on_appearing
            | imgui.WindowFlags_.no_nav
        )
        bg_color, text_color = self._get_notification_colors(notification.type)
        imgui.push_style_color(imgui.Col_.window_bg, bg_color)
        imgui.push_style_color(imgui.Col_.text, text_color)
        if imgui.begin(window_id, None, flags):
            imgui.text(notification.title)
            imgui.spacing()
            imgui.push_text_wrap_pos(imgui.get_content_region_avail().x)
            imgui.text(notification.message)
            imgui.pop_text_wrap_pos()
            if notification.dismissible:
                imgui.same_line()
                imgui.set_cursor_pos_x(imgui.get_window_width() - 30)
                if imgui.small_button("X##" + window_id):
                    notification.visible = False
        imgui.end()
        imgui.pop_style_color(2)

    def _get_notification_colors(
        self, type: NotificationType
    ) -> tuple[tuple[float, float, float, float], tuple[float, float, float, float]]:
        match type:
            case NotificationType.INFO:
                return (0.2, 0.4, 0.8, 0.95), (1.0, 1.0, 1.0, 1.0)
            case NotificationType.SUCCESS:
                return (0.2, 0.7, 0.3, 0.95), (1.0, 1.0, 1.0, 1.0)
            case NotificationType.WARNING:
                return (0.9, 0.7, 0.2, 0.95), (0.1, 0.1, 0.1, 1.0)
            case NotificationType.ERROR:
                return (0.8, 0.2, 0.2, 0.95), (1.0, 1.0, 1.0, 1.0)
            case _:
                return (0.3, 0.3, 0.3, 0.95), (1.0, 1.0, 1.0, 1.0)
