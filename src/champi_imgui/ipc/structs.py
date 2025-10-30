"""Binary struct serialization for IPC commands.

Fixed-size structs for efficient shared memory communication between
MCP server and Canvas render process.
"""

import struct
from dataclasses import dataclass
from typing import Any

from champi_imgui.ipc.command_types import CommandType

# Size constants (in bytes)
MAX_CANVAS_ID_SIZE = 64
MAX_TITLE_SIZE = 128
MAX_WIDGET_ID_SIZE = 64
MAX_WIDGET_TYPE_SIZE = 32

# Padding character for fixed-size strings
PAD_CHAR = b"#"

# Struct definitions
# Format: '=' (native byte order), 'Q' (8-byte unsigned long), 'B' (1-byte unsigned char)
HEADER_STRUCT = struct.Struct("=QB")  # seq_num + command_type

CLEAR_CANVAS_STRUCT = struct.Struct(
    f"=QB{MAX_CANVAS_ID_SIZE}s"
)  # seq_num + cmd_type + canvas_id

UPDATE_STATE_STRUCT = struct.Struct(
    f"=QB{MAX_CANVAS_ID_SIZE}s{MAX_TITLE_SIZE}sII"
)  # seq_num + cmd_type + canvas_id + title + width + height

SHUTDOWN_STRUCT = struct.Struct(
    f"=QB{MAX_CANVAS_ID_SIZE}s"
)  # seq_num + cmd_type + canvas_id

# Placeholder for Stage 6
ADD_WIDGET_STRUCT = struct.Struct(
    f"=QB{MAX_CANVAS_ID_SIZE}s{MAX_WIDGET_ID_SIZE}s{MAX_WIDGET_TYPE_SIZE}s"
)  # seq_num + cmd_type + canvas_id + widget_id + widget_type

ACK_STRUCT = struct.Struct("=Q")  # seq_num only


@dataclass
class CommandData:
    """Parsed command data from binary struct."""

    command_type: CommandType
    seq_num: int
    data: dict[str, Any]


def _pad_string(s: str, size: int) -> bytes:
    """Pad string to fixed size with PAD_CHAR."""
    encoded = s.encode("utf-8")[:size]
    return encoded.ljust(size, PAD_CHAR)


def _unpad_string(b: bytes) -> str:
    """Remove padding from fixed-size string."""
    return b.rstrip(PAD_CHAR).decode("utf-8", errors="ignore")


def get_struct_size(command_type: CommandType) -> int:
    """Get the size in bytes for a command type."""
    if command_type == CommandType.CLEAR_CANVAS:
        return CLEAR_CANVAS_STRUCT.size
    elif command_type == CommandType.UPDATE_STATE:
        return UPDATE_STATE_STRUCT.size
    elif command_type == CommandType.SHUTDOWN:
        return SHUTDOWN_STRUCT.size
    elif command_type == CommandType.ADD_WIDGET:
        return ADD_WIDGET_STRUCT.size
    elif command_type == CommandType.ACK:
        return ACK_STRUCT.size
    else:
        # Default to largest struct
        return max(
            CLEAR_CANVAS_STRUCT.size,
            UPDATE_STATE_STRUCT.size,
            SHUTDOWN_STRUCT.size,
            ADD_WIDGET_STRUCT.size,
        )


def pack_command(command_type: CommandType, seq_num: int, **kwargs: Any) -> bytes:
    """Pack command data into binary struct.

    Args:
        command_type: Type of command to pack
        seq_num: Sequence number for tracking
        **kwargs: Command-specific data

    Returns:
        Binary struct data
    """
    if command_type == CommandType.CLEAR_CANVAS:
        canvas_id = kwargs.get("canvas_id", "")
        return CLEAR_CANVAS_STRUCT.pack(
            seq_num, command_type, _pad_string(canvas_id, MAX_CANVAS_ID_SIZE)
        )

    elif command_type == CommandType.UPDATE_STATE:
        canvas_id = kwargs.get("canvas_id", "")
        title = kwargs.get("title", "")
        width = kwargs.get("width", 800)
        height = kwargs.get("height", 600)
        return UPDATE_STATE_STRUCT.pack(
            seq_num,
            command_type,
            _pad_string(canvas_id, MAX_CANVAS_ID_SIZE),
            _pad_string(title, MAX_TITLE_SIZE),
            width,
            height,
        )

    elif command_type == CommandType.SHUTDOWN:
        canvas_id = kwargs.get("canvas_id", "")
        return SHUTDOWN_STRUCT.pack(
            seq_num, command_type, _pad_string(canvas_id, MAX_CANVAS_ID_SIZE)
        )

    elif command_type == CommandType.ADD_WIDGET:
        # Placeholder for Stage 6
        canvas_id = kwargs.get("canvas_id", "")
        widget_id = kwargs.get("widget_id", "")
        widget_type = kwargs.get("widget_type", "")
        return ADD_WIDGET_STRUCT.pack(
            seq_num,
            command_type,
            _pad_string(canvas_id, MAX_CANVAS_ID_SIZE),
            _pad_string(widget_id, MAX_WIDGET_ID_SIZE),
            _pad_string(widget_type, MAX_WIDGET_TYPE_SIZE),
        )

    else:
        msg = f"Unknown command type: {command_type}"
        raise ValueError(msg)


def unpack_command(data: bytes) -> CommandData:
    """Unpack binary struct into command data.

    Args:
        data: Binary struct data

    Returns:
        CommandData with parsed fields
    """
    # Read header first
    seq_num, cmd_type_int = HEADER_STRUCT.unpack(data[: HEADER_STRUCT.size])
    command_type = CommandType(cmd_type_int)

    # Unpack based on command type
    if command_type == CommandType.CLEAR_CANVAS:
        seq_num, cmd_type_int, canvas_id_bytes = CLEAR_CANVAS_STRUCT.unpack(data)
        return CommandData(
            command_type=command_type,
            seq_num=seq_num,
            data={"canvas_id": _unpad_string(canvas_id_bytes)},
        )

    elif command_type == CommandType.UPDATE_STATE:
        (
            seq_num,
            cmd_type_int,
            canvas_id_bytes,
            title_bytes,
            width,
            height,
        ) = UPDATE_STATE_STRUCT.unpack(data)
        return CommandData(
            command_type=command_type,
            seq_num=seq_num,
            data={
                "canvas_id": _unpad_string(canvas_id_bytes),
                "title": _unpad_string(title_bytes),
                "width": width,
                "height": height,
            },
        )

    elif command_type == CommandType.SHUTDOWN:
        seq_num, cmd_type_int, canvas_id_bytes = SHUTDOWN_STRUCT.unpack(data)
        return CommandData(
            command_type=command_type,
            seq_num=seq_num,
            data={"canvas_id": _unpad_string(canvas_id_bytes)},
        )

    elif command_type == CommandType.ADD_WIDGET:
        # Placeholder for Stage 6
        (
            seq_num,
            cmd_type_int,
            canvas_id_bytes,
            widget_id_bytes,
            widget_type_bytes,
        ) = ADD_WIDGET_STRUCT.unpack(data)
        return CommandData(
            command_type=command_type,
            seq_num=seq_num,
            data={
                "canvas_id": _unpad_string(canvas_id_bytes),
                "widget_id": _unpad_string(widget_id_bytes),
                "widget_type": _unpad_string(widget_type_bytes),
            },
        )

    else:
        msg = f"Unknown command type: {command_type}"
        raise ValueError(msg)


def pack_ack(seq_num: int) -> bytes:
    """Pack acknowledgment with sequence number."""
    return ACK_STRUCT.pack(seq_num)


def unpack_ack(data: bytes) -> int:
    """Unpack acknowledgment to get sequence number."""
    result = ACK_STRUCT.unpack(data)
    return int(result[0])
