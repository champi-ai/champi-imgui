"""File dialog integration using imgui_bundle's portable file dialogs."""

from collections.abc import Callable

from imgui_bundle import imgui, portable_file_dialogs
from loguru import logger

from champi_imgui.core.widget import Widget

_AnyDialog = (
    portable_file_dialogs.open_file
    | portable_file_dialogs.save_file
    | portable_file_dialogs.select_folder
)


class FileDialogMode:
    """File dialog mode constants."""

    OPEN_FILE = "open_file"
    OPEN_FOLDER = "open_folder"
    SAVE_FILE = "save_file"


class FileDialog:
    """Low-level wrapper around portable_file_dialogs."""

    def __init__(self) -> None:
        self.current_dialog: _AnyDialog | None = None
        self.result_callback: Callable | None = None

    def open_file(
        self,
        title: str = "Open File",
        filters: list[str] | None = None,
        default_path: str = "",
        callback: Callable | None = None,
    ) -> None:
        """Open a file selection dialog."""
        try:
            self.result_callback = callback
            self.current_dialog = portable_file_dialogs.open_file(
                title=title,
                default_path=default_path,
                filters=filters or [],
                options=portable_file_dialogs.opt.none,
            )
        except Exception as e:
            logger.error(f"Error opening file dialog: {e}")

    def open_folder(
        self,
        title: str = "Select Folder",
        default_path: str = "",
        callback: Callable | None = None,
    ) -> None:
        """Open a folder selection dialog."""
        try:
            self.result_callback = callback
            self.current_dialog = portable_file_dialogs.select_folder(
                title=title,
                default_path=default_path,
            )
        except Exception as e:
            logger.error(f"Error opening folder dialog: {e}")

    def save_file(
        self,
        title: str = "Save File",
        filters: list[str] | None = None,
        default_path: str = "",
        callback: Callable | None = None,
    ) -> None:
        """Open a save file dialog."""
        try:
            self.result_callback = callback
            self.current_dialog = portable_file_dialogs.save_file(
                title=title,
                default_path=default_path,
                filters=filters or [],
                options=portable_file_dialogs.opt.none,
            )
        except Exception as e:
            logger.error(f"Error opening save dialog: {e}")

    def update(self) -> str | None:
        """Poll dialog state. Returns selected path (string) when ready."""
        if not self.current_dialog:
            return None
        if self.current_dialog.ready():
            raw = self.current_dialog.result()
            # open_file returns list[str]; save_file/select_folder return str
            if isinstance(raw, list):
                result: str | None = raw[0] if raw else None
            else:
                result = raw if raw else None
            if result and self.result_callback:
                self.result_callback(result)
            self.current_dialog = None
            self.result_callback = None
            return result
        return None

    def is_active(self) -> bool:
        return self.current_dialog is not None


class FileDialogWidget(Widget):
    """Widget that renders a browse button and file selection dialog."""

    def __init__(
        self,
        widget_id: str,
        button_label: str = "Browse...",
        mode: str = FileDialogMode.OPEN_FILE,
        title: str = "Select File",
        filters: list[str] | None = None,
        **props,
    ) -> None:
        props["button_label"] = button_label
        props["mode"] = mode
        props["title"] = title
        props["filters"] = filters or []
        props["selected_path"] = ""
        props["dialog_open"] = False
        super().__init__(widget_id, **props)
        self.file_dialog = FileDialog()

    def render(self) -> str | None:
        """Render widget. Returns selected path when user completes a selection."""
        button_label = self.state.properties.get("button_label", "Browse...")
        selected_path = self.state.properties.get("selected_path", "")
        dialog_open = self.state.properties.get("dialog_open", False)

        if selected_path:
            imgui.text(f"Selected: {selected_path}")
            imgui.same_line()

        if imgui.button(button_label):
            self._open_dialog()
            self.state.properties["dialog_open"] = True

        if dialog_open:
            result = self.file_dialog.update()
            if result:
                self.state.properties["selected_path"] = result
                self.state.properties["dialog_open"] = False
                self.trigger_callback("on_select", result)
                return result

        return None

    def get_selected_path(self) -> str:
        return str(self.state.properties.get("selected_path", ""))

    def set_filters(self, filters: list[str]) -> None:
        self.state.properties["filters"] = filters

    def _open_dialog(self) -> None:
        mode = self.state.properties.get("mode", FileDialogMode.OPEN_FILE)
        title = self.state.properties.get("title", "Select File")
        filters = self.state.properties.get("filters", [])
        if mode == FileDialogMode.OPEN_FILE:
            self.file_dialog.open_file(title=title, filters=filters)
        elif mode == FileDialogMode.OPEN_FOLDER:
            self.file_dialog.open_folder(title=title)
        elif mode == FileDialogMode.SAVE_FILE:
            self.file_dialog.save_file(title=title, filters=filters)


class MessageDialog:
    """Static helpers for native OS message dialogs."""

    @staticmethod
    def info(title: str, message: str) -> None:
        """Show an informational message dialog."""
        try:
            portable_file_dialogs.message(
                title=title,
                text=message,
                _choice=portable_file_dialogs.choice.ok,
                _icon=portable_file_dialogs.icon.info,
            )
        except Exception as e:
            logger.error(f"Error showing info dialog: {e}")

    @staticmethod
    def warning(title: str, message: str) -> None:
        """Show a warning message dialog."""
        try:
            portable_file_dialogs.message(
                title=title,
                text=message,
                _choice=portable_file_dialogs.choice.ok,
                _icon=portable_file_dialogs.icon.warning,
            )
        except Exception as e:
            logger.error(f"Error showing warning dialog: {e}")

    @staticmethod
    def error(title: str, message: str) -> None:
        """Show an error message dialog."""
        try:
            portable_file_dialogs.message(
                title=title,
                text=message,
                _choice=portable_file_dialogs.choice.ok,
                _icon=portable_file_dialogs.icon.error,
            )
        except Exception as e:
            logger.error(f"Error showing error dialog: {e}")
