"""Tests for FileDialog, FileDialogWidget, and MessageDialog."""

from unittest.mock import MagicMock, patch

from champi_imgui.extensions.file_dialog import (
    FileDialog,
    FileDialogMode,
    FileDialogWidget,
    MessageDialog,
)


class TestFileDialogMode:
    def test_constants(self) -> None:
        assert FileDialogMode.OPEN_FILE == "open_file"
        assert FileDialogMode.OPEN_FOLDER == "open_folder"
        assert FileDialogMode.SAVE_FILE == "save_file"


class TestFileDialog:
    def test_init(self) -> None:
        fd = FileDialog()
        assert fd.current_dialog is None
        assert fd.result_callback is None

    def test_is_active_false(self) -> None:
        fd = FileDialog()
        assert fd.is_active() is False

    def test_update_no_dialog(self) -> None:
        fd = FileDialog()
        assert fd.update() is None

    def test_open_file_creates_dialog(self) -> None:
        fd = FileDialog()
        mock_dialog = MagicMock()
        with patch(
            "champi_imgui.extensions.file_dialog.portable_file_dialogs"
        ) as mock_pfd:
            mock_pfd.open_file.return_value = mock_dialog
            mock_pfd.opt.none = 0
            fd.open_file(title="Test")
        assert fd.current_dialog is mock_dialog
        assert fd.is_active() is True

    def test_open_file_exception_handled(self) -> None:
        fd = FileDialog()
        with patch(
            "champi_imgui.extensions.file_dialog.portable_file_dialogs"
        ) as mock_pfd:
            mock_pfd.open_file.side_effect = RuntimeError("no display")
            fd.open_file()
        assert fd.current_dialog is None

    def test_update_returns_path_when_ready(self) -> None:
        fd = FileDialog()
        mock_dialog = MagicMock()
        mock_dialog.ready.return_value = True
        mock_dialog.result.return_value = ["/path/to/file.txt"]
        fd.current_dialog = mock_dialog  # type: ignore[assignment]
        result = fd.update()
        assert result == "/path/to/file.txt"
        assert fd.current_dialog is None

    def test_update_calls_callback(self) -> None:
        fd = FileDialog()
        mock_dialog = MagicMock()
        mock_dialog.ready.return_value = True
        mock_dialog.result.return_value = ["/file.txt"]
        callback = MagicMock()
        fd.current_dialog = mock_dialog  # type: ignore[assignment]
        fd.result_callback = callback
        fd.update()
        callback.assert_called_once_with("/file.txt")

    def test_update_not_ready_returns_none(self) -> None:
        fd = FileDialog()
        mock_dialog = MagicMock()
        mock_dialog.ready.return_value = False
        fd.current_dialog = mock_dialog  # type: ignore[assignment]
        assert fd.update() is None
        assert fd.current_dialog is mock_dialog

    def test_save_file_result_string(self) -> None:
        fd = FileDialog()
        mock_dialog = MagicMock()
        mock_dialog.ready.return_value = True
        mock_dialog.result.return_value = "/save/path.txt"  # str not list
        fd.current_dialog = mock_dialog  # type: ignore[assignment]
        result = fd.update()
        assert result == "/save/path.txt"


class TestFileDialogWidget:
    def test_init(self) -> None:
        widget = FileDialogWidget("dlg1")
        assert widget.state.properties["button_label"] == "Browse..."
        assert widget.state.properties["mode"] == FileDialogMode.OPEN_FILE
        assert widget.state.properties["selected_path"] == ""

    def test_get_selected_path_empty(self) -> None:
        widget = FileDialogWidget("dlg1")
        assert widget.get_selected_path() == ""

    def test_set_filters(self) -> None:
        widget = FileDialogWidget("dlg1")
        widget.set_filters(["*.py", "*.txt"])
        assert widget.state.properties["filters"] == ["*.py", "*.txt"]

    def test_custom_mode(self) -> None:
        widget = FileDialogWidget("dlg1", mode=FileDialogMode.SAVE_FILE)
        assert widget.state.properties["mode"] == FileDialogMode.SAVE_FILE


class TestMessageDialog:
    def test_info(self) -> None:
        with patch(
            "champi_imgui.extensions.file_dialog.portable_file_dialogs"
        ) as mock_pfd:
            MessageDialog.info("Title", "Message")
            mock_pfd.message.assert_called_once()

    def test_warning(self) -> None:
        with patch(
            "champi_imgui.extensions.file_dialog.portable_file_dialogs"
        ) as mock_pfd:
            MessageDialog.warning("Title", "Message")
            mock_pfd.message.assert_called_once()

    def test_error(self) -> None:
        with patch(
            "champi_imgui.extensions.file_dialog.portable_file_dialogs"
        ) as mock_pfd:
            MessageDialog.error("Title", "Message")
            mock_pfd.message.assert_called_once()

    def test_exception_handled(self) -> None:
        with patch(
            "champi_imgui.extensions.file_dialog.portable_file_dialogs"
        ) as mock_pfd:
            mock_pfd.message.side_effect = RuntimeError("no display")
            MessageDialog.info("T", "M")  # should not raise
