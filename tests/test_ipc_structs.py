"""Tests for IPC command struct serialization.

Covers: UPDATE_TITLE / UPDATE_SIZE separation, cross-platform alignment,
and CommandType enum values (closes #144, #151).
"""

import pytest

from champi_imgui.ipc.command_types import CommandType
from champi_imgui.ipc.structs import (
    UPDATE_SIZE_STRUCT,
    UPDATE_TITLE_STRUCT,
    get_struct_size,
    pack_command,
    unpack_command,
)


class TestCommandTypeValues:
    def test_update_title_value(self) -> None:
        assert CommandType.UPDATE_TITLE == 3

    def test_update_size_value(self) -> None:
        assert CommandType.UPDATE_SIZE == 4

    def test_shutdown_value(self) -> None:
        assert CommandType.SHUTDOWN == 5

    def test_no_update_state(self) -> None:
        names = [m.name for m in CommandType]
        assert "UPDATE_STATE" not in names


class TestUpdateTitleRoundTrip:
    def test_pack_unpack_preserves_title(self) -> None:
        packed = pack_command(
            CommandType.UPDATE_TITLE, 1, canvas_id="main", title="Hello"
        )
        result = unpack_command(packed)
        assert result.command_type == CommandType.UPDATE_TITLE
        assert result.data["canvas_id"] == "main"
        assert result.data["title"] == "Hello"

    def test_title_result_has_no_size_fields(self) -> None:
        packed = pack_command(CommandType.UPDATE_TITLE, 1, canvas_id="x", title="T")
        result = unpack_command(packed)
        assert "width" not in result.data
        assert "height" not in result.data

    def test_get_struct_size_update_title(self) -> None:
        assert get_struct_size(CommandType.UPDATE_TITLE) == UPDATE_TITLE_STRUCT.size

    def test_unicode_title_round_trips(self) -> None:
        packed = pack_command(CommandType.UPDATE_TITLE, 99, canvas_id="c", title="Ñoño")
        result = unpack_command(packed)
        assert result.data["title"] == "Ñoño"


class TestUpdateSizeRoundTrip:
    def test_pack_unpack_preserves_dimensions(self) -> None:
        packed = pack_command(
            CommandType.UPDATE_SIZE, 2, canvas_id="main", width=1920, height=1080
        )
        result = unpack_command(packed)
        assert result.command_type == CommandType.UPDATE_SIZE
        assert result.data["width"] == 1920
        assert result.data["height"] == 1080

    def test_size_result_has_no_title_field(self) -> None:
        packed = pack_command(
            CommandType.UPDATE_SIZE, 2, canvas_id="x", width=800, height=600
        )
        result = unpack_command(packed)
        assert "title" not in result.data

    def test_get_struct_size_update_size(self) -> None:
        assert get_struct_size(CommandType.UPDATE_SIZE) == UPDATE_SIZE_STRUCT.size

    @pytest.mark.parametrize(
        "width,height",
        [
            (800, 600),
            (1920, 1080),
            (3840, 2160),
            (1, 1),
            (65535, 65535),
        ],
    )
    def test_various_dimensions_round_trip(self, width: int, height: int) -> None:
        packed = pack_command(
            CommandType.UPDATE_SIZE, 1, canvas_id="c", width=width, height=height
        )
        result = unpack_command(packed)
        assert result.data["width"] == width
        assert result.data["height"] == height


class TestCrossContamination:
    def test_update_title_does_not_affect_size(self) -> None:
        """A title-only pack must not contain width/height fields."""
        packed = pack_command(
            CommandType.UPDATE_TITLE, 5, canvas_id="cv", title="New Title"
        )
        result = unpack_command(packed)
        assert result.data.get("title") == "New Title"
        assert "width" not in result.data
        assert "height" not in result.data

    def test_update_size_does_not_affect_title(self) -> None:
        """A size-only pack must not contain a title field."""
        packed = pack_command(
            CommandType.UPDATE_SIZE, 6, canvas_id="cv", width=640, height=480
        )
        result = unpack_command(packed)
        assert result.data.get("width") == 640
        assert result.data.get("height") == 480
        assert "title" not in result.data


class TestStructAlignment:
    def test_update_size_width_field_is_4byte_aligned(self) -> None:
        """Width integer must start at a 4-byte aligned offset (ARM64 requirement)."""
        import struct as _struct

        # offset after QB + 64s + 3x padding
        offset = _struct.calcsize("<QB64s3x")
        assert offset % 4 == 0, f"width field at offset {offset} is not 4-byte aligned"

    def test_update_size_round_trip_exact_values(self) -> None:
        """Guard against byte-swap or misread on big-endian / strict-alignment platforms."""
        for w, h in [(0x1234, 0x5678), (0xDEAD, 0xBEEF), (1920, 1080)]:
            packed = pack_command(
                CommandType.UPDATE_SIZE, 1, canvas_id="a", width=w, height=h
            )
            result = unpack_command(packed)
            assert result.data["width"] == w, (
                f"width mismatch: expected {w:#x}, got {result.data['width']:#x}"
            )
            assert result.data["height"] == h, (
                f"height mismatch: expected {h:#x}, got {result.data['height']:#x}"
            )
